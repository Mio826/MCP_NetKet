# NetKet MCP Server for Quantum Many-Body Physics

A Model Context Protocol (MCP) server for quantum many-body physics using NetKet, featuring a **simplified, modular design** with predefined Hamiltonian models.

## 🎯 **Key Features**

### **Simplified Hamiltonian System**
- **Predefined Models**: SSH, Hubbard, Fermion Hopping, Heisenberg, Ising, Kitaev
- **Clean Parameter Specification**: Simple text-based input with automatic parameter extraction
- **No Complex Parsing**: Removed LaTeX parsing and custom term handling for reliability
- **Modular Design**: Easy to extend with new predefined models

### **Text-Based Specification**
- **Lattice**: `"chain of 24 sites"`, `"4x4 square lattice"`, `"2x2x2 cubic lattice"`
- **Hilbert Space**: `"1 fermion"`, `"spin-1/2 on each site"`, `"8 fermions with spin-1/2"`
- **Hamiltonian**: `"SSH model with t1=1, t2=0.2"`, `"Hubbard model with t=1, U=4"`

### **Automatic NetKet Integration**
- Converts text specifications to NetKet objects automatically
- Handles spin-1/2 fermions correctly (uses integer spin indices)
- Supports parameter sweeps and energy spectrum computation

## 🚀 **Quick Start**

### **1. Create a Quantum System**
```python
# Create a new system
system_id = create_quantum_system("SSH model analysis")
```

### **2. Set Lattice**
```python
# Set the lattice geometry
set_lattice(system_id, "chain of 24 sites")
```

### **3. Set Hilbert Space**
```python
# Set the Hilbert space
set_hilbert_space(system_id, "1 fermion")
```

### **4. Set Hamiltonian**
```python
# Set the Hamiltonian with optional parameter ranges
set_hamiltonian(
    system_id, 
    "SSH model with t1=1, t2=0.2",
    parameter_ranges={"t2": [0.1, 0.5, 1.0, 1.5, 2.0]}
)
```

### **5. Compute Energy Spectrum**
```python
# Compute the energy spectrum
compute_energy_spectrum(system_id, num_eigenvalues=10)
```

### **6. Analyze Ground State**
```python
# Analyze ground state properties
analyze_ground_state(system_id)
```

### **7. Parameter Sweep**
```python
# Perform parameter sweep
parameter_sweep(system_id, "t2")
```

### **8. Generate Plots**
```python
# Generate plots
generate_plot(system_id, "parameter_sweep")
```

## 📋 **Supported Models**

### **Fermion Models**
- **SSH Model**: `"SSH model with t1=1, t2=0.2"`
- **Hubbard Model**: `"Hubbard model with t=1, U=4"`
- **Fermion Hopping**: `"Fermion hopping with t=1, B=0.5"`

### **Spin Models**
- **Heisenberg Model**: `"Heisenberg model with J=1"`
- **Ising Model**: `"Ising model with Jz=1, hx=0.5"`
- **Kitaev Model**: `"Kitaev model with Jx=1, Jy=0.8, Jz=1.2"`

## 🏗️ **Architecture**

### **Schema-Based Design**
```
Text Input → Schema Parsing → NetKet Objects → Computation
```

### **Core Components**
- **LatticeSchema**: Converts lattice descriptions to NetKet graphs
- **HilbertSpaceSchema**: Converts Hilbert space descriptions to NetKet Hilbert spaces
- **HamiltonianSchema**: Converts Hamiltonian descriptions to NetKet operators

### **MCP Tools**
- `create_quantum_system()`: Create new system
- `set_lattice()`: Set lattice geometry
- `set_hilbert_space()`: Set Hilbert space
- `set_hamiltonian()`: Set Hamiltonian with parameter ranges
- `compute_energy_spectrum()`: Compute eigenvalues
- `analyze_ground_state()`: Analyze ground state
- `parameter_sweep()`: Parameter sweeps
- `generate_plot()`: Generate plots
- `list_quantum_systems()`: List all systems
- `get_system_details()`: Get system details
- `delete_quantum_system()`: Delete system

## 🔧 **Installation**

```bash
pip install netket fastmcp pydantic numpy scipy matplotlib
```

## 📖 **Documentation**

See `MCP_SERVER_README.md` for detailed API documentation and examples.

## 🎯 **Benefits of Simplified Design**

1. **Reliability**: No complex parsing means fewer bugs
2. **Maintainability**: Clean, modular code structure
3. **Extensibility**: Easy to add new predefined models
4. **Performance**: Direct NetKet integration without overhead
5. **Usability**: Simple text-based interface for physicists

## 🔮 **Future Extensions**

The simplified design makes it easy to add new predefined models:
- Add new model types to `HamiltonianSchema`
- Implement building logic in `build_netket_hamiltonian()`
- Update parameter parsing in `_parse_hamiltonian_text()`

This approach provides a solid foundation for quantum many-body physics research while maintaining simplicity and reliability.

## 🧪 Example Analyses and Physical Interpretation

This repository includes ready-to-run analysis scripts for classic quantum many-body models. These scripts demonstrate how to use the MCP tools to reveal phase transitions and key physical phenomena:

### **1. SSH Model: Topological Edge States and Spectrum**
- **Script:** `ssh_full_spectrum_analysis.py`
- **What it does:**
  - Computes the full single-particle spectrum as a function of dimerization ratio \( t_2/t_1 \).
  - Plots the spatial profile of the zero-energy edge state in the topological phase (using 1 spinless fermion).
- **Physical meaning:**
  - The spectrum shows the gap closing at the topological transition.
  - The edge state profile reveals localization at the chain ends in the topological phase.

### **2. Hubbard Model: Mott Metal-Insulator Transition**
- **Script:** `analyze_hubbard.py`
- **What it does:**
  - Computes the true Mott gap (charge gap) as a function of on-site repulsion \( U \) at half-filling.
  - Plots only the Mott gap (no ground state energy).
- **Physical meaning:**
  - The gap is small at \( U=0 \) (metallic), and opens for \( U>0 \) (Mott insulator).
  - Demonstrates the Mott transition in finite-size systems.

### **3. Ising Model: Quantum Phase Transition**
- **Script:** `analyze_ising.py`
- **What it does:**
  - Computes the lowest few eigenvalues for a chain of spins as a function of transverse field \( h_x \).
  - Plots both the energy gap (between ground and first excited state) and the ground state degeneracy as a function of \( h_x \).
- **Physical meaning:**
  - The gap is nearly zero and the ground state is two-fold degenerate in the ferromagnetic phase (\( h_x < 1 \)).
  - The gap opens and degeneracy drops to 1 in the paramagnetic phase (\( h_x > 1 \)).
  - The transition is clearly visible as the point where the gap opens and degeneracy changes.

### **How to use these scripts**
- Each script is self-contained and can be run directly (e.g., `python3 analyze_ising.py`).
- The output plots are saved as PNG files in the working directory.
- The scripts serve as templates for further model studies and can be easily adapted to new models or observables.

### **Best Practices for Extending Analyses**
- Use the MCP tools to build systems modularly: set lattice, Hilbert space, and Hamiltonian step by step.
- For phase transitions, scan the relevant parameter (e.g., \( t_2/t_1 \), \( U \), \( h_x \)).
- Plot physically meaningful observables: energy gap, order parameter (magnetization), degeneracy, or spatial profiles.
- For symmetry-broken phases, consider adding a tiny symmetry-breaking field to reveal the order parameter in finite systems.

These examples provide a robust starting point for both users and developers to explore quantum phase transitions and many-body physics using the MCP server and NetKet.