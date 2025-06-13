import numpy as np
from scipy.sparse.linalg import eigsh
import sys

from mcp.server.fastmcp import FastMCP

import netket.graph as nkgraph
import netket.hilbert as nkh
import netket.experimental as nkx
from fermion_builder import *


with open("mcp_log.txt", "a") as f:
    f.write("netket_interface.py\n")

mcp = FastMCP("netket_interface")

# Global model store (in-memory, for chaining tools later)
MODEL_STORE = {}
Hamiltonian_STORE = {}
# use to reset model storage
def model_reset():
    MODEL_STORE = {}
    return MODEL_STORE
#Warning information
warnings = []


# Candidate graph mapping
graph_candidates = {
    "chain": nkgraph.Chain,
    "square": nkgraph.Square,
    "triangular": nkgraph.Triangular,
    "kagome": nkgraph.Kagome,
    "honeycomb": nkgraph.Honeycomb,
    "fcc": nkgraph.FCC,
    "bcc": nkgraph.BCC,
    "pyrochlore": nkgraph.Pyrochlore,
    "cube": nkgraph.Cube,
    "hypercube": nkgraph.Hypercube,
    "double": nkgraph.DoubledGraph,
}

def match_graph_class(name: str):
    name = name.strip().lower()
    for key, graph_class in graph_candidates.items():
        if key in name:
            return graph_class
    raise ValueError(f"Unknown or unsupported lattice '{name}'.")

@mcp.tool()
def build_graph_and_hilbert(
    lattice: str,
    extent: list,
    particle: str = "spin",
    spin: float = 0.5,
    particle_n: int = 1,
    bosonic_modes: int=1,
) -> dict:
    """
    Build NetKet Graph and Hilbert space given a lattice name and particle type.
    Returns a handle ID to access later.
    lattice: Lattice name.
    extent: Lattice extent
    particle: particle type, fermion, boson, or spin
    spin: spin of particle, for fermion, it's usually 1/2 (electron)
    particle_n: particle numbers
    bosonic_modes: bosonic_modes number
    """
    GraphClass = match_graph_class(lattice)
    try:
        graph = GraphClass(extent)
    except Exception as e:
        raise RuntimeError(f"Failed to build graph '{lattice}' with extent {extent}: {e}")

    # Build Hilbert space
    if particle.lower() == "spin":
        hilbert = nkh.Spin(s=spin, N=graph.n_nodes)
    elif particle.lower() == "fermion":
        if particle_n is None:
            raise ValueError("particle number must be specified for fermions")
        hilbert = nkx.hilbert.SpinOrbitalFermions(graph.n_nodes,s=spin,n_fermions=particle_n)
    elif particle.lower() == "boson":
        if particle_n is None:
            raise ValueError("particle number must be specified for bosons")
        hilbert = nkh.Fock(n_particles=particle_n, N=bosonic_modes, n_max=None)  # basic default
    else:
        raise ValueError(f"Unsupported particle type: {particle}")

    # Store model in memory
    handle = f"model_{len(MODEL_STORE)}"
    MODEL_STORE[handle] = {
        "graph": graph,
        "hilbert": hilbert,
        "meta": {
            "lattice": lattice,
            "extent": extent,
            "particle": particle,
        },
    }

    return {
        "handle": handle,
        "graph_nodes": graph.n_nodes,
        "hilbert_type": hilbert.__class__.__name__,
        "description": str(hilbert),
    }

@mcp.tool()
def build_Hamiltonian(
    handle: str,
    fermion_para = {'t':0, 'u':0, 'v':0, 'B':0},
    boson_para = {'t':0, 'mu':0},
    spin_para = {'J':0, 'Jz':0, 'hx':0, 'hz':0},
    ) -> dict:
    """
    handle: model handler
    fermion_para: t: real hopping, u: hubbard interaction, v: nearest coulomb interaction, B:zeeman field
    boson_para: t: real hopping, mu: chemical potential
    spin_para: J: Heisenberg exchange, Jz: Ising exchange, hx: transverse field, hz: longitudinal field
    """
    model = MODEL_STORE[handle]
    H_total = 0
    if MODEL_STORE['model_0']['meta']['particle'].lower() == "fermion":
        if not (all(value == 0 for value in boson_para.values()) and all(value == 0 for value in spin_para.values())):
            warnings.append(f"{handle} is fermion system, while holding boson or spin model parameters")
        t,u,v,B = fermion_para['t'],fermion_para['u'],fermion_para['v'],fermion_para['B']
        hi,graph = model['hilbert'], model['graph']
        H_total = Hop(hi,graph,t)+Hubbard(hi,graph,u)+Coulomb(hi,graph,v)+Zeeman(hi,graph,B)

    Hamiltonian_STORE[handle] = H_total
    return {
        "handle": handle,
        "Hamiltonian": H_total,
        "warning": "; ".join(warnings) if warnings else None
    }


#function for exact diagnalization
@mcp.tool()
def ED(handle, k=5, which="SA"):
    """
    input: type(H) =#exact diagonalization, type(H) = netket.experimental.operator._fermion_operator_2nd_numba.FermionOperator2nd
           k: used in sparse matrix ED
    output: eigenvalues, eigenstates, ground state degeneracy
    """
    H = Hamiltonian_STORE[handle]
    hi = H.hilbert
    if hi.n_states>1e3: #sparse matrix
        sp_h = H.to_sparse()
        eig_vals, eig_vecs = eigsh(sp_h, k=k, which=which)
        sort_idx = np.argsort(eig_vals)
        eig_vals_sorted = eig_vals[sort_idx]
        eig_vecs_sorted = eig_vecs[:, sort_idx]
    else:
        eig_vals_sorted, eig_vecs_sorted = np.linalg.eigh(H.to_dense())
    E0 = np.min(eig_vals_sorted)
    degeneracy = np.sum(np.abs(eig_vals_sorted - E0) < 1e-8)
    return eig_vals_sorted, eig_vecs_sorted, degeneracy

#function for calculating expecation value
@mcp.tool()
def expect_ED(OP,eig_vec)->float:
    """
    OP: netket type operator
    eig_vec: eigenvector
    This function is used to calculate expectation value of OP under eig_vec
    """
    OP = OP.to_dense()
    ket = np.array(eig_vec).reshape(-1,1)
    bra = np.array(ket.conjugate().reshape(1,-1))
    return (bra@(OP@ket)).item()

#function correlation calculation from exact diagonalization
@mcp.tool()
def correlation(eig_vec, op1, op2, connect=True) ->float:
    """
    eig_vec: eigenvector
    op1: operator1 op2: operator 2
    connect: bool: calculating disconnected or connected correlation function?
    This function is used to calculate correlation between op1 and op2 under eig_vec
    """
    OP = (op1*op2).to_dense()
    return expect_ED(OP,eig_vec)

#nearest spin-spin correlation function
@mcp.tool()
def spin_correlation(handle, connect=True) -> list:
    """
    this function is specially used to calculate the nearest spin-spin correlation under ground state of model MODEL_STORE[handle]
    function structure: 1. get ground state by ED, 2. catch the graph of model, 3. go through the graph edges as nearest bonds 4. return the spin-spin correlation as a list
    """
    _,eigenstates,_ = ED(handle, k=5, which="SA")
    groundstate = eigenstates[:,0]
    graph = MODEL_STORE[handle]["graph"]
    SS_expect = []
    for (i,j) in graph.edges:
        spin_i = electron_spin(graph,i)
        spin_j = electron_spin(graph,j)
        SS_expect.append(correlation(groundstate,spin_i,spin_j))
    return SS_expect


if __name__ == "__main__":
    print("[MCP STDIO READY! netket_interface]", file=sys.stderr, flush=True)
    try:
        mcp.run(transport="stdio")
    except Exception as e:
        with open("mcp_log.txt", "a") as f:
            f.write(f"Crash: {e}\n")

