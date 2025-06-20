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