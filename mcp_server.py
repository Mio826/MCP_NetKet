from fastmcp import FastMCP
from netket_schemas import LatticeSchema, HilbertSpaceSchema, HamiltonianSchema
from netket_jsons import NetKetJSONManager, QuantumSystemState
from typing import Literal, Optional, Dict, Any, List, Union
import numpy as np
import netket as nk
from netket.experimental.operator.fermion import destroy as c
from netket.experimental.operator.fermion import create as cdag
from scipy.sparse.linalg import eigsh
import matplotlib.pyplot as plt
import io
import base64
import shutil

# Create the MCP server object
mcp = FastMCP('NetKet Quantum Many-Body Physics Server')

# Global JSON manager for state management
json_manager = NetKetJSONManager()

@mcp.tool()
def create_quantum_system(description: Optional[str] = None) -> Dict[str, Any]:
    '''Create a new quantum system for analysis.
    
    This tool creates a new quantum system with a unique ID that can be used
    to build up a complete quantum many-body system step by step.
    
    Args:
        description: Optional description of the system to create
        
    Returns:
        Dictionary containing the system ID and status
        
    Example:
        - Input: {"description": "SSH model on 24-site chain"}
        - Output: {
            "system_id": "system_a1b2c3d4",
            "status": "empty",
            "message": "New quantum system created successfully"
        }
    '''
    system_id = json_manager.create_system(description)
    system = json_manager.systems[system_id]
    return {
        "system_id": system_id,
        "status": system.status,
        "message": "New quantum system created successfully"
    }

@mcp.tool()
def set_lattice(system_id: str, lattice_spec: str) -> Dict[str, Any]:
    '''Set the lattice geometry for a quantum system.
    
    This tool sets the lattice component of a quantum system using text-based specification.
    
    Args:
        system_id: The ID of the quantum system
        lattice_spec: Text description of the lattice (e.g., "chain of 24 sites", "4x4 square lattice")
        
    Returns:
        Dictionary containing the updated system status and lattice information
        
    Examples:
        - Input: {"system_id": "system_a1b2c3d4", "lattice_spec": "chain of 24 sites"}
        - Output: {
            "system_id": "system_a1b2c3d4",
            "lattice": "chain of 24 sites",
            "lattice_type": "chain",
            "extent": [24],
            "status": "partial"
        }
    '''
    json_manager.update_component("lattice", lattice_spec, system_id)
    system = json_manager.systems[system_id]
    return {
        "system_id": system_id,
        "lattice": system.lattice.text,
        "lattice_type": system.lattice.lattice_type,
        "extent": system.lattice.extent,
        "status": system.status,
        "warnings": system.warnings
    }

@mcp.tool()
def set_hilbert_space(system_id: str, hilbert_spec: str) -> Dict[str, Any]:
    '''Set the Hilbert space for a quantum system.
    
    This tool sets the Hilbert space component of a quantum system using text-based specification.
    
    Args:
        system_id: The ID of the quantum system
        hilbert_spec: Text description of the Hilbert space (e.g., "1 fermion", "spin-1/2 on each site")
        
    Returns:
        Dictionary containing the updated system status and Hilbert space information
        
    Examples:
        - Input: {"system_id": "system_a1b2c3d4", "hilbert_spec": "1 fermion"}
        - Output: {
            "system_id": "system_a1b2c3d4",
            "hilbert": "1 fermion",
            "space_type": "fermion",
            "n_particles": 1,
            "status": "partial"
        }
    '''
    json_manager.update_component("hilbert", hilbert_spec, system_id)
    system = json_manager.systems[system_id]
    return {
        "system_id": system_id,
        "hilbert": system.hilbert.text,
        "space_type": system.hilbert.space_type,
        "n_particles": system.hilbert.n_particles,
        "status": system.status,
        "warnings": system.warnings
    }

@mcp.tool()
def set_hamiltonian(system_id: str, hamiltonian_spec: str, 
                   parameter_ranges: Optional[Dict[str, List[float]]] = None) -> Dict[str, Any]:
    '''Set the Hamiltonian for a quantum system with optional parameter ranges for sweeps.
    
    This tool sets the Hamiltonian component of a quantum system using text-based specification.
    It can also include parameter ranges for automatic parameter sweeps.
    
    Args:
        system_id: The ID of the quantum system
        hamiltonian_spec: Text description of the Hamiltonian (e.g., "SSH model with t1=1, t2=0.2")
        parameter_ranges: Optional parameter ranges for sweeps (e.g., {"t2": [0.1, 0.5, 1.0, 1.5, 2.0]})
        
    Returns:
        Dictionary containing the updated system status and Hamiltonian information
        
    Examples:
        - Input: {
            "system_id": "system_a1b2c3d4", 
            "hamiltonian_spec": "SSH model with t1=1, t2=0.2",
            "parameter_ranges": {"t2": [0.1, 0.5, 1.0, 1.5, 2.0]}
          }
        - Output: {
            "system_id": "system_a1b2c3d4",
            "hamiltonian": "SSH model with t1=1, t2=0.2",
            "model_type": "SSH",
            "parameters": {"t1": 1.0, "t2": 0.2},
            "parameter_ranges": {"t2": [0.1, 0.5, 1.0, 1.5, 2.0]},
            "status": "complete"
          }
    '''
    # Create HamiltonianSchema with parameter ranges
    hamiltonian_data = {"text": hamiltonian_spec}
    if parameter_ranges:
        hamiltonian_data["parameter_ranges"] = parameter_ranges
    
    json_manager.update_component("hamiltonian", hamiltonian_data, system_id)
    system = json_manager.systems[system_id]
    
    # Extract parameters for display
    params = system.hamiltonian.get_parameters() if system.hamiltonian else {}
    
    return {
        "system_id": system_id,
        "hamiltonian": system.hamiltonian.text,
        "model_type": system.hamiltonian.model_type.upper() if system.hamiltonian else None,
        "parameters": params,
        "parameter_ranges": system.hamiltonian.parameter_ranges if system.hamiltonian else None,
        "status": system.status,
        "warnings": system.warnings
    }

@mcp.tool()
def compute_energy_spectrum(system_id: str, num_eigenvalues: int = 10, which: str = "SA") -> Dict[str, Any]:
    '''Compute the energy spectrum of a quantum system.
    
    This tool performs exact diagonalization to find the energy eigenvalues
    of the system's Hamiltonian. It automatically builds the Hamiltonian from
    the system specification if needed.
    
    Args:
        system_id: The ID of the quantum system
        num_eigenvalues: Number of eigenvalues to compute (default: 10)
        which: Which eigenvalues to compute ("SA" for smallest algebraic, "LA" for largest algebraic)
        
    Returns:
        Dictionary containing the energy spectrum
        
    Examples:
        - Input: {"system_id": "system_a1b2c3d4", "num_eigenvalues": 5}
        - Output: {
            "system_id": "system_a1b2c3d4",
            "eigenvalues": [-2.5, -1.8, -0.3, 0.3, 1.8],
            "ground_state_energy": -2.5,
            "energy_gap": 1.5,
            "num_eigenvalues": 5
          }
    '''
    system = json_manager.systems[system_id]
    
    # Check if all required components are present
    if not system.lattice or not system.hilbert or not system.hamiltonian:
        raise ValueError("System must have lattice, Hilbert space, and Hamiltonian defined. "
                        "Use set_lattice(), set_hilbert_space(), and set_hamiltonian() first.")
    
    # Build Hamiltonian from specification
    H, hi, graph = _build_hamiltonian_from_spec(system)
    
    # Function for exact diagonalization
    def ED(H, k=num_eigenvalues, which=which):
        if hi.n_states > 1e3:  # sparse matrix
            sp_h = H.to_sparse()
            eig_vals, eig_vecs = eigsh(sp_h, k=k, which=which)
            sort_idx = np.argsort(eig_vals)
            eig_vals_sorted = eig_vals[sort_idx]
            eig_vecs_sorted = eig_vecs[:, sort_idx]
        else:
            eig_vals_sorted, eig_vecs_sorted = np.linalg.eigh(H.to_dense())
            if k < len(eig_vals_sorted):
                eig_vals_sorted = eig_vals_sorted[:k]
                eig_vecs_sorted = eig_vecs_sorted[:, :k]
        return eig_vals_sorted, eig_vecs_sorted
    
    eigvals, eigvecs = ED(H)
    
    # Store results
    system.results["energy_spectrum"] = {
        "eigenvalues": eigvals.tolist(),
        "eigenvectors": eigvecs.tolist(),
        "ground_state_energy": float(eigvals[0]),
        "energy_gap": float(eigvals[1] - eigvals[0]) if len(eigvals) > 1 else 0.0
    }
    system.results["model_type"] = system.hamiltonian.model_type
    system.results["parameters"] = system.hamiltonian.get_parameters()
    json_manager.save_system(system_id)
    
    return {
        "system_id": system_id,
        "eigenvalues": eigvals.tolist(),
        "ground_state_energy": float(eigvals[0]),
        "energy_gap": float(eigvals[1] - eigvals[0]) if len(eigvals) > 1 else 0.0,
        "num_eigenvalues": len(eigvals),
        "model_type": system.hamiltonian.model_type.upper(),
        "parameters": system.hamiltonian.get_parameters()
    }

@mcp.tool()
def analyze_ground_state(system_id: str) -> Dict[str, Any]:
    '''Analyze the ground state properties of a quantum system.
    
    This tool computes various properties of the ground state, including
    energy, degeneracy, and spatial profile for fermionic systems.
    It automatically computes the energy spectrum if not already available.
    
    Args:
        system_id: The ID of the quantum system
        
    Returns:
        Dictionary containing ground state analysis
        
    Examples:
        - Input: {"system_id": "system_a1b2c3d4"}
        - Output: {
            "system_id": "system_a1b2c3d4",
            "ground_state_energy": -2.5,
            "degeneracy": 1,
            "spatial_profile": [0.1, 0.2, 0.3, ...],
            "localization": "extended"
          }
    '''
    system = json_manager.systems[system_id]
    
    # Check if all required components are present
    if not system.lattice or not system.hilbert or not system.hamiltonian:
        raise ValueError("System must have lattice, Hilbert space, and Hamiltonian defined. "
                        "Use set_lattice(), set_hilbert_space(), and set_hamiltonian() first.")
    
    # Compute energy spectrum if not already available
    if "energy_spectrum" not in system.results:
        # Build Hamiltonian and compute spectrum
        H, hi, graph = _build_hamiltonian_from_spec(system)
        
        # Function for exact diagonalization
        def ED(H, k=5, which="SA"):
            if hi.n_states > 1e3:  # sparse matrix
                sp_h = H.to_sparse()
                eig_vals, eig_vecs = eigsh(sp_h, k=k, which=which)
                sort_idx = np.argsort(eig_vals)
                eig_vals_sorted = eig_vals[sort_idx]
                eig_vecs_sorted = eig_vecs[:, sort_idx]
            else:
                eig_vals_sorted, eig_vecs_sorted = np.linalg.eigh(H.to_dense())
                if k < len(eig_vals_sorted):
                    eig_vals_sorted = eig_vals_sorted[:k]
                    eig_vecs_sorted = eig_vecs_sorted[:, :k]
            return eig_vals_sorted, eig_vecs_sorted
        
        eigvals, eigvecs = ED(H)
        
        # Store spectrum results
        system.results["energy_spectrum"] = {
            "eigenvalues": eigvals.tolist(),
            "eigenvectors": eigvecs.tolist(),
            "ground_state_energy": float(eigvals[0]),
            "energy_gap": float(eigvals[1] - eigvals[0]) if len(eigvals) > 1 else 0.0
        }
        system.results["model_type"] = system.hamiltonian.model_type
        system.results["parameters"] = system.hamiltonian.get_parameters()
    
    spectrum = system.results["energy_spectrum"]
    eigvals = np.array(spectrum["eigenvalues"])
    eigvecs = np.array(spectrum["eigenvectors"])
    
    # Find ground state
    E0 = eigvals[0]
    degeneracy = np.sum(np.abs(eigvals - E0) < 1e-8)
    
    # Get ground state wavefunction
    psi_gs = eigvecs[:, 0]
    prob_density = np.abs(psi_gs)**2
    
    # Analyze localization
    if system.hilbert.space_type == "fermion":
        # For fermions, analyze particle distribution
        localization = "localized" if np.std(prob_density) > 0.1 else "extended"
    else:
        localization = "N/A"
    
    # Store results
    system.results["ground_state_analysis"] = {
        "ground_state_energy": float(E0),
        "degeneracy": int(degeneracy),
        "spatial_profile": prob_density.tolist(),
        "localization": localization
    }
    # Do NOT store any NetKet objects in results
    json_manager.save_system(system_id)
    
    return {
        "system_id": system_id,
        "ground_state_energy": float(E0),
        "degeneracy": int(degeneracy),
        "spatial_profile": prob_density.tolist(),
        "localization": localization,
        "model_type": system.hamiltonian.model_type.upper(),
        "parameters": system.hamiltonian.get_parameters()
    }

@mcp.tool()
def parameter_sweep(system_id: str, parameter_name: str, 
                   parameter_range: Optional[List[float]] = None) -> Dict[str, Any]:
    '''Perform a parameter sweep for a quantum model.
    
    This tool varies one parameter while keeping others fixed, computing
    the energy spectrum at each point. It can use parameter ranges from
    the Hamiltonian specification if available.
    
    Args:
        system_id: The ID of the quantum system
        parameter_name: Name of parameter to sweep (e.g., "t2", "U", "J")
        parameter_range: List of parameter values to try (optional, uses Hamiltonian specification if not provided)
        
    Returns:
        Dictionary containing sweep results
        
    Examples:
        - Input: {
            "system_id": "system_a1b2c3d4",
            "parameter_name": "t2"
          }
        - Output: {
            "system_id": "system_a1b2c3d4",
            "parameter_name": "t2",
            "parameter_range": [0.1, 0.5, 1.0, 1.5, 2.0],
            "ground_state_energies": [-2.1, -1.8, -1.5, -1.8, -2.1],
            "energy_gaps": [0.5, 0.8, 0.0, 0.8, 0.5]
          }
    '''
    system = json_manager.systems[system_id]
    
    # Check if all required components are present
    if not system.lattice or not system.hilbert or not system.hamiltonian:
        raise ValueError("System must have lattice, Hilbert space, and Hamiltonian defined. "
                        "Use set_lattice(), set_hilbert_space(), and set_hamiltonian() first.")
    
    # Get parameter range from Hamiltonian specification if not provided
    if parameter_range is None:
        if system.hamiltonian.parameter_ranges and parameter_name in system.hamiltonian.parameter_ranges:
            parameter_range = system.hamiltonian.parameter_ranges[parameter_name]
        else:
            raise ValueError(f"No parameter range provided and no range found in Hamiltonian specification for '{parameter_name}'. "
                           "Either provide parameter_range or set it in set_hamiltonian() with parameter_ranges.")
    
    # Create NetKet objects
    graph = system.lattice.to_netket_graph()
    hi = system.hilbert.to_netket_hilbert(graph)
    
    # Function for exact diagonalization
    def ED(H, k=5, which="SA"):
        if hi.n_states > 1e3:  # sparse matrix
            sp_h = H.to_sparse()
            eig_vals, eig_vecs = eigsh(sp_h, k=k, which=which)
            sort_idx = np.argsort(eig_vals)
            eig_vals_sorted = eig_vals[sort_idx]
            eig_vecs_sorted = eig_vecs[:, sort_idx]
        else:
            eig_vals_sorted, eig_vecs_sorted = np.linalg.eigh(H.to_dense())
        return eig_vals_sorted, eig_vecs_sorted
    
    ground_state_energies = []
    energy_gaps = []
    spectra_data = {}
    all_eigenvalues = []  # Store all eigenvalues for each parameter value
    
    # Get base parameters from Hamiltonian specification
    base_params = system.hamiltonian.get_parameters()
    model_type = system.hamiltonian.model_type
    
    for param_value in parameter_range:
        # Create a temporary Hamiltonian with the new parameter value
        temp_params = base_params.copy()
        temp_params[parameter_name] = param_value
        
        # Create a temporary HamiltonianSchema
        temp_hamiltonian = HamiltonianSchema(
            model_type=model_type,
            parameters=temp_params
        )
        
        # Build Hamiltonian using the schema's method
        H = temp_hamiltonian.build_netket_hamiltonian(hi, graph, system_hilbert=system.hilbert)
        
        # Compute spectrum
        eigvals, eigvecs = ED(H, k=hi.n_states if hi.n_states <= 100 else 10)  # Only compute all if small
        ground_state_energies.append(float(eigvals[0]))
        energy_gaps.append(float(eigvals[1] - eigvals[0]) if len(eigvals) > 1 else 0.0)
        spectra_data[f"{parameter_name}_{param_value}"] = eigvals.tolist()
        all_eigenvalues.append(eigvals.tolist())
    
    # Store results
    system.results["parameter_sweep"] = {
        "parameter_name": parameter_name,
        "parameter_range": parameter_range,
        "ground_state_energies": ground_state_energies,
        "energy_gaps": energy_gaps,
        "spectra_data": spectra_data,
        "all_eigenvalues": all_eigenvalues,
        "model_type": model_type,
        "base_parameters": base_params
    }
    # Do NOT store any NetKet objects in results
    json_manager.save_system(system_id)
    
    return {
        "system_id": system_id,
        "parameter_name": parameter_name,
        "parameter_range": parameter_range,
        "ground_state_energies": ground_state_energies,
        "energy_gaps": energy_gaps,
        "all_eigenvalues": all_eigenvalues,
        "model_type": model_type.upper(),
        "base_parameters": base_params
    }

@mcp.tool()
def generate_plot(system_id: str, plot_type: str, file_path: Optional[str] = None) -> Dict[str, Any]:
    '''Generate plots for quantum system analysis.
    
    This tool creates various types of plots based on the system's analysis results.
    
    Args:
        system_id: The ID of the quantum system
        plot_type: Type of plot ("spectrum", "ground_state", "parameter_sweep")
        file_path: Optional path to save the plot image file (e.g., "ssh_transition.png")
        
    Returns:
        Dictionary containing plot data
        
    Examples:
        - Input: {"system_id": "system_a1b2c3d4", "plot_type": "parameter_sweep", "file_path": "ssh_transition.png"}
        - Output: {
            "system_id": "system_a1b2c3d4",
            "plot_type": "parameter_sweep",
            "file_path": "ssh_transition.png",
            "description": "Parameter sweep plot saved to file"
          }
    '''
    system = json_manager.systems[system_id]
    
    if plot_type == "spectrum" and "energy_spectrum" in system.results:
        # Plot energy spectrum
        spectrum = system.results["energy_spectrum"]
        eigvals = spectrum["eigenvalues"]
        
        plt.figure(figsize=(8, 6))
        plt.plot(range(len(eigvals)), eigvals, 'o-', markersize=6)
        plt.xlabel("Eigenvalue index", fontsize=12)
        plt.ylabel("Energy", fontsize=12)
        plt.title(f"Energy Spectrum: {system.results.get('model_type', 'Unknown')} Model", fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
    elif plot_type == "ground_state" and "ground_state_analysis" in system.results:
        # Plot ground state spatial profile
        gs_analysis = system.results["ground_state_analysis"]
        spatial_profile = gs_analysis["spatial_profile"]
        
        plt.figure(figsize=(8, 5))
        plt.plot(range(len(spatial_profile)), spatial_profile, 'o-', markersize=4)
        plt.xlabel("Site index", fontsize=12)
        plt.ylabel("|ψ(i)|²", fontsize=12)
        plt.title(f"Ground State Profile: {system.results.get('model_type', 'Unknown')} Model", fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
    elif plot_type == "parameter_sweep" and "parameter_sweep" in system.results:
        # Plot parameter sweep results
        sweep = system.results["parameter_sweep"]
        param_range = sweep["parameter_range"]
        gs_energies = sweep["ground_state_energies"]
        energy_gaps = sweep["energy_gaps"]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Ground state energy
        ax1.plot(param_range, gs_energies, 'o-', markersize=6)
        ax1.set_xlabel(sweep["parameter_name"], fontsize=12)
        ax1.set_ylabel("Ground State Energy", fontsize=12)
        ax1.set_title("Ground State Energy", fontsize=14)
        ax1.grid(True, alpha=0.3)
        
        # Energy gap
        ax2.plot(param_range, energy_gaps, 'o-', markersize=6, color='red')
        ax2.set_xlabel(sweep["parameter_name"], fontsize=12)
        ax2.set_ylabel("Energy Gap", fontsize=12)
        ax2.set_title("Energy Gap", fontsize=14)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
    else:
        raise ValueError(f"No data available for plot type: {plot_type}")
    
    if file_path:
        # Save plot to file inside the system's directory
        system_dir = json_manager.storage_dir / system_id
        system_dir.mkdir(exist_ok=True)
        full_path = system_dir / file_path
        
        plt.savefig(full_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return {
            "system_id": system_id,
            "plot_type": plot_type,
            "file_path": str(full_path),
            "description": f"{plot_type.replace('_', ' ').title()} plot saved to file"
        }
    else:
        # Return plot as base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plot_data = base64.b64encode(buf.getvalue()).decode()
        plt.close()
        
        return {
            "system_id": system_id,
            "plot_type": plot_type,
            "plot_data": plot_data,
            "description": f"{plot_type.replace('_', ' ').title()} plot as base64"
        }

@mcp.tool()
def list_quantum_systems() -> List[Dict[str, Any]]:
    '''List all available quantum systems.
    
    Returns:
        List of dictionaries containing system information
        
    Example:
        - Output: [
            {
                "system_id": "system_a1b2c3d4",
                "status": "complete",
                "last_modified": "2024-01-15T10:30:00",
                "lattice": "chain of 24 sites",
                "hilbert": "1 fermion",
                "hamiltonian": "SSH model with t1=1, t2=0.2"
            }
        ]
    '''
    return json_manager.list_systems()

@mcp.tool()
def get_system_details(system_id: str) -> Dict[str, Any]:
    '''Get detailed information about a specific quantum system.
    
    Args:
        system_id: The ID of the quantum system
        
    Returns:
        Dictionary containing complete system details
        
    Example:
        - Input: {"system_id": "system_a1b2c3d4"}
        - Output: {
            "system_id": "system_a1b2c3d4",
            "status": "complete",
            "created_at": "2024-01-15T10:00:00",
            "last_modified": "2024-01-15T10:30:00",
            "lattice": {...},
            "hilbert": {...},
            "hamiltonian": {...},
            "results": {...},
            "warnings": []
        }
    '''
    if system_id not in json_manager.systems:
        raise ValueError(f"System {system_id} not found")
    
    system = json_manager.systems[system_id]
    return system.to_dict()

@mcp.tool()
def delete_quantum_system(system_id: str) -> Dict[str, Any]:
    '''Delete a quantum system and its associated data.
    
    Args:
        system_id: The ID of the quantum system to delete
        
    Returns:
        Dictionary confirming deletion
        
    Example:
        - Input: {"system_id": "system_a1b2c3d4"}
        - Output: {
            "system_id": "system_a1b2c3d4",
            "status": "deleted",
            "message": "System deleted successfully"
        }
    '''
    if system_id not in json_manager.systems:
        raise ValueError(f"System {system_id} not found")
    
    # Remove from memory
    del json_manager.systems[system_id]

    # Delete the entire system directory
    system_dir = json_manager.storage_dir / system_id
    if system_dir.exists():
        shutil.rmtree(system_dir)
    
    return {
        "system_id": system_id,
        "status": "deleted",
        "message": "System and all associated files deleted successfully"
    }

def _build_hamiltonian_from_spec(system) -> Any:
    """Helper function to build NetKet Hamiltonian from system specification."""
    if not system.lattice or not system.hilbert or not system.hamiltonian:
        raise ValueError("System must have lattice, Hilbert space, and Hamiltonian defined")
    
    # Create NetKet objects
    graph = system.lattice.to_netket_graph()
    hi = system.hilbert.to_netket_hilbert(graph)
    
    # Build Hamiltonian using the schema's method, passing the Hilbert space schema
    H = system.hamiltonian.build_netket_hamiltonian(hi, graph, system_hilbert=system.hilbert)
    
    return H, hi, graph

# This is the main entry point for your server
if __name__ == "__main__":
    mcp.run() 