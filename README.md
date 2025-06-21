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

## 🖥️ Lucien AI Desktop Integration

Integrate this MCP server with [Lucien AI desktop](https://pathintegral.notion.site/how-to-use-lucien#2159dd60ece1807986c3f9ab795a1a05) for an enhanced AI-powered quantum physics research experience!

### Step 1: Install Lucien AI
1. Download and install [Lucien AI desktop](https://pathintegral.notion.site/how-to-use-lucien#2159dd60ece1807986c3f9ab795a1a05)
2. Log in to your Lucien account
3. In Lucien's **Settings**, follow the instructions to install `uv` (Lucien's package manager)

### Step 2: Clone the Repository
```bash
git clone <your-repo-url>
cd MCP_NetKet
```

### Step 3: Configure MCP Server in Lucien
1. Open Lucien AI desktop
2. Go to **Settings** → **MCP Servers**
3. Click **Add Server** and configure:

   **Server Configuration:**
   - **Server name**: `NetKet-MCP`
   - **Command**: `uv`
   - **Arguments**: `run mcp run /path/to/your/MCP_NetKet/mcp_server.py`
     *(Replace with your actual local path to mcp_server.py)*
   - **Environment**: 
     - Variable: `UV_PROJECT_ENVIRONMENT`
     - Value: `/path/to/your/MCP_NetKet`
     *(Replace with your actual local path to the MCP_NetKet folder)*

4. Click **Save**

### Step 4: Start Using!
- The NetKet MCP server will now be available in your Lucien AI conversations
- You can use natural language to create quantum systems, run simulations, and analyze results
- Try the [Interactive Demo](#-interactive-demo-ising-model-quantum-phase-transition) below!

**Example Lucien conversation:**
```
"Create a quantum system for the SSH model on a 24-site chain with 1 fermion and analyze its energy spectrum"
```

## 🎯 Interactive Demo: Ising Model Quantum Phase Transition

Try this step-by-step demo to see the MCP server in action! This demonstrates a quantum phase transition where the system changes from an ordered to a disordered phase.

### Step 1: Setup System
```
Create a quantum system for the Ising model on a 16-site chain with spin-1/2 particles. Set the Ising Hamiltonian with Jz=1 and a transverse field hx ranging from 0 to 2.
```

### Step 2: Run Analysis & Plot Gap
```
Perform a parameter sweep over hx. From the results, create a plot showing the energy gap as a function of the transverse field.
```

### Step 3: Plot Degeneracy
```
Using the same sweep results, create a plot showing the ground state degeneracy as a function of the transverse field.
```

### Step 4: Display and Interpret
```
Display both plots and explain what we observe about the Ising model quantum phase transition, specifically how the energy gap closes and the degeneracy drops from 2 to 1 at the critical point around hx=1.
```

**Expected Results:**
- **Energy gap**: Closes at the critical point (hx ≈ 1)
- **Degeneracy**: Drops from 2 (ordered phase) to 1 (disordered phase) at the critical point
- **Physical interpretation**: The system transitions from a magnetically ordered state to a disordered state

This demo showcases the power of the flexible `analyze_eigenstate` and `plot_xy` tools for custom quantum physics analysis!

## 🔬 Analysis Scripts

This repository includes ready-to-run analysis scripts that demonstrate how to use the server to explore key physical phenomena. 

All generated plots are saved in a dedicated folder under `/tmp/quantum_systems/`. The `/tmp` directory is a standard folder for temporary files at the root of your filesystem, which ensures compatibility with read-only environments. You can access it via the terminal with `cd /tmp` or, on macOS, using the Finder's "Go to Folder" command (Shift+Cmd+G). **Please note that its contents may be cleared upon system restart.**

### 1. SSH Model: Topological Edge States
- **Script:** `analyze_ssh.py`
- **Physics:** Visualizes the full energy spectrum and the zero-energy edge states characteristic of the topological phase in the Su-Schrieffer-Heeger (SSH) model.
- **Usage:** 
  ```bash
  python analyze_ssh.py
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
- **Physics:** Shows the quantum phase transition by plotting both the energy gap and ground-state degeneracy as a function of the transverse magnetic field `hx`.
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
- `analyze_eigenstate()`: Analyzes any specific eigenstate by index.
- `parameter_sweep()`: Runs calculations over a range of parameter values.
- `plot_xy()`: Creates custom 2D plots from any data.
- `generate_plot()`: Creates plots from analysis results.
- `list_quantum_systems()`: Lists all currently managed systems.
- `delete_quantum_system()`: Removes a system and all its data.