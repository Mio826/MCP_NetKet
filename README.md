# NetKet MCP Server for Quantum Many-Body Physics

A Model Context Protocol (MCP) server for quantum many-body physics using NetKet. This server provides a simplified, modular framework for defining and simulating quantum systems with text-based commands.

## 🚀 Quick Start

### 1. Installation

```bash
pip install netket fastmcp pydantic numpy scipy matplotlib
```

### 2. Run the Server

Start the MCP server in a terminal:
```bash
python mcp_server.py
```

### 3. Use in a Client

In a separate Python script or Jupyter notebook, you can interact with the server's tools. For example, to create a system and compute its ground state energy:

```python
from mcp_server import create_quantum_system, set_lattice, set_hilbert_space, set_hamiltonian, compute_energy_spectrum

# Create a system for a 1D chain of 24 sites
sys_id = create_quantum_system("My SSH Chain")['system_id']

# Define its properties
set_lattice(sys_id, "chain of 24 sites")
set_hilbert_space(sys_id, "1 spinless fermion")
set_hamiltonian(sys_id, "SSH model with t1=1.0, t2=0.2")

# Compute and print the ground state energy
spectrum = compute_energy_spectrum(sys_id, num_eigenvalues=1)
print(f"Ground State Energy: {spectrum['ground_state_energy']}")
```

## 🔬 Analysis Scripts

This repository includes ready-to-run analysis scripts that demonstrate how to use the server to explore key physical phenomena. All generated plots are saved in a dedicated folder under `quantum_systems/`.

### 1. SSH Model: Topological Edge States

- **Script:** `ssh_full_spectrum_analysis.py`
- **Physics:** Visualizes the symmetric energy spectrum and the zero-energy edge states characteristic of the topological phase in the Su-Schrieffer-Heeger (SSH) model.
- **Usage:** 
  ```bash
  python ssh_full_spectrum_analysis.py
  ```

### 2. Hubbard Model: Mott Metal-Insulator Transition

- **Script:** `analyze_hubbard.py`
- **Physics:** Calculates and plots the Mott gap as a function of the on-site repulsion `U`, demonstrating the transition from a metal to a Mott insulator.
- **Usage:**
  ```bash
  python analyze_hubbard.py
  ```

### 3. Ising Model: Quantum Phase Transition

- **Script:** `analyze_ising.py`
- **Physics:** Shows the quantum phase transition by plotting the energy gap and ground-state degeneracy as a function of the transverse magnetic field `hx`.
- **Usage:**
  ```bash
  python analyze_ising.py
  ```

## ⚙️ Core Concepts & API

The server operates on a simple, schema-based design. You define components of your system using text, which the server parses into NetKet objects.

### Supported Specifications

- **Lattice:** `"chain of 24 sites"`, `"8x8 square lattice"`, `"4x4x4 cubic lattice"`
- **Hilbert Space:** `"spin-1/2 on each site"`, `"10 spinless fermions"`, `"4 fermions with spin-1/2"`
- **Hamiltonian:**
  - `"SSH model with t1=1, t2=0.2"`
  - `"Hubbard model with t=1, U=4"`
  - `"Ising model with Jz=1, hx=0.5"`
  - `"Heisenberg model with J=1"`

### Main API Tools

- `create_quantum_system()`: Creates a new system and returns its ID.
- `set_lattice()`: Sets the lattice geometry.
- `set_hilbert_space()`: Sets the particle type and constraints.
- `set_hamiltonian()`: Defines the model and its parameters.
- `compute_energy_spectrum()`: Performs exact diagonalization.
- `analyze_ground_state()`: Calculates properties of the lowest-energy state.
- `parameter_sweep()`: Runs calculations over a range of parameter values.
- `generate_plot()`: Creates plots from analysis results.
- `list_quantum_systems()`: Lists all currently managed systems.
- `delete_quantum_system()`: Removes a system and all its data.