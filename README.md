# MCP_NetKet

An "AI for many-body physics" researcher based on Model Context Protocol (MCP) and NetKet. This project provides a bridge between AI agents and quantum many-body simulations using NetKet.

## Overview

This project implements a schema-based interface for defining and managing quantum many-body systems. It provides:
- Text-based specification of quantum lattices, Hilbert spaces, and Hamiltonians
- JSON-based state management for quantum systems
- Integration with NetKet for quantum simulations
- AI-friendly interfaces through the Model Context Protocol

## Requirements

Required packages:
- NumPy 
- SciPy
- NetKet: 3.17.1
- Qutip: 5.2.0
- MCP: 1.9.3
- Pydantic

## Core Components

### 1. Schema Definitions (`netket_schemas.py`)

Contains Pydantic models for defining quantum system components:

- `LatticeSchema`: Defines quantum lattices
  - Supports various lattice types (chain, square, triangular, etc.)
  - Text-based specification (e.g., "4x4 square lattice")
  - Converts to NetKet graph objects

- `HilbertSpaceSchema`: Defines quantum Hilbert spaces
  - Supports spins, fermions, and bosons
  - Text-based specification (e.g., "spin-1/2 on each site")
  - Handles particle number constraints

- `HamiltonianSchema`: Defines quantum Hamiltonians
  - Supports common models (Hubbard, Heisenberg, etc.)
  - Parameter specification (t, U, J, etc.)
  - Text-based specification (e.g., "Hubbard model with t=1, U=4")

### 2. JSON Management (`netket_jsons.py`)

Provides state management for quantum systems:

- `QuantumSystemState`: Represents complete quantum system state
  - Unique system ID
  - Component tracking (lattice, Hilbert space, Hamiltonian)
  - History and validation

- `NetKetJSONManager`: Manages system states
  - File-based storage
  - System creation and updates
  - Component validation
  - System listing and loading

## Usage Examples

```python
# Create a new quantum system
manager = NetKetJSONManager()
system_id = manager.create_system()

# Define components using text specification
manager.update_component("lattice", "4x4 square lattice")
manager.update_component("hilbert", "spin-1/2 on each site")
manager.update_component("hamiltonian", "Heisenberg model with J=1")

# Load and inspect systems
system = manager.load_system(system_id)
systems = manager.list_systems()
```

## Supported Features

### Supported Lattice Types

| Lattice Type   | Example Text Input           | Extent Format      | Notes                        |
|----------------|-----------------------------|--------------------|------------------------------|
| chain          | `chain of 8 sites`          | `[8]`              | 1D chain, length=int         |
| square         | `4x4 square lattice`        | `[4, 4]`           | Only n x n supported         |
| cube           | `2x2x2 cubic lattice`       | `[2, 2, 2]`        | Only n x n x n supported     |
| hypercube      | `hypercube 4`               | `[4]`              | Only single dimension        |
| triangular     | `3x3 triangular lattice`    | `[3, 3]`           | 2D, extent                   |
| kagome         | `kagome lattice 3x3`        | `[3, 3]`           | 2D, extent                   |
| honeycomb      | `honeycomb lattice 4x4`     | `[4, 4]`           | 2D, extent                   |
| fcc            | `2x2x2 fcc lattice`         | `[2, 2, 2]`        | 3D, extent                   |
| bcc            | `2x2x2 bcc lattice`         | `[2, 2, 2]`        | 3D, extent                   |
| pyrochlore     | `2x2x2 pyrochlore lattice`  | `[2, 2, 2]`        | 3D, extent                   |

---

### Supported Hilbert Space Types

| Space Type | Example Text Inputs | Required Fields | Constraints & Notes |
|------------|-------------------|-----------------|-------------------|
| spin       | - `spin-1/2 on each site`<br>- `spin-1 on each site` | `spin` | - Default is spin-1/2<br>- Defines spin space on each lattice site<br>- Supports arbitrary spin values |
| fermion    | - `4 fermions with spin-1/2`<br>- `2 fermions`<br>- `3 spin-1/2 fermions in 4 sites` | `n_particles`, `spin` | - Follows Pauli exclusion principle<br>- Maximum filling depends on spin and sites<br>- Spin-1/2 is most common case |
| boson      | - `3 bosons`<br>- `2 bosons in 3 modes`<br>- `5 bosons per site` | `n_particles`, `n_modes` (optional) | - No particle number restrictions<br>- Modes default to 1 if not specified<br>- Can specify local/global constraints |

---

### Supported Hamiltonian Interactions and Their Equations

| Model Type         | Example Text Input                        | Supported Parameters         | Hamiltonian Equation                                                                                  |
|--------------------|-------------------------------------------|-----------------------------|------------------------------------------------------------------------------------------------------|
|   Hubbard          | `Hubbard model with t=1, U=4`             | `t`, `U`                    | $ H = -t \sum_{\langle i,j \rangle, \sigma} (c_{i\sigma}^\dagger c_{j\sigma} + h.c.) + U \sum_i n_{i\uparrow} n_{i\downarrow} $ |
|   Extended Hubbard | `Extended Hubbard: t=1, U=4, V=0.5`     | `t`, `U`, `V`               | $ H = -t \sum_{\langle i,j \rangle, \sigma} (c_{i\sigma}^\dagger c_{j\sigma} + h.c.) + U \sum_i n_{i\uparrow} n_{i\downarrow} + V \sum_{\langle i,j \rangle} n_i n_j $ |
|   Heisenberg       | `Heisenberg model with J=1, hx=0.5`       | `J`, `hx`, `hz`             | $ H = J \sum_{\langle i,j \rangle} \vec{S}_i \cdot \vec{S}_j + h_x \sum_i S_i^x + h_z \sum_i S_i^z $ |
|   Ising            | `Ising model with Jz=1, hx=0.2`           | `Jz`, `hx`, `hz`            | $ H = J_z \sum_{\langle i,j \rangle} S_i^z S_j^z + h_x \sum_i S_i^x + h_z \sum_i S_i^z $           |
|   Fermion hopping  | `Fermion hopping t=1 and Zeeman field B=0.1` | `t`, `B`                | $ H = -t \sum_{\langle i,j \rangle, \sigma} (c_{i\sigma}^\dagger c_{j\sigma} + h.c.) + B \sum_i (n_{i\uparrow} - n_{i\downarrow}) $ |
|   Boson            | `Boson model with t=1, mu=0.5`            | `t`, `mu`                   | $ H = -t \sum_{\langle i,j \rangle} (b_i^\dagger b_j + h.c.) - \mu \sum_i n_i $                    |

---

**Legend:**
- $ c_{i\sigma}^\dagger, c_{i\sigma} $: Fermionic creation/annihilation operators at site $ i $ with spin $ \sigma $
- $ n_{i\sigma} = c_{i\sigma}^\dagger c_{i\sigma} $: Number operator
- $ n_i = n_{i\uparrow} + n_{i\downarrow} $: Total number operator at site $ i $
- $ \vec{S}_i $: Spin operator at site $ i $
- $ S_i^x, S_i^z $: Spin-x and spin-z operators
- $ b_i^\dagger, b_i $: Bosonic creation/annihilation operators
- $ \langle i,j \rangle $: Sum over nearest neighbors
- $ h.c. $: Hermitian conjugate

---

**Notes:**
- All parameters (`t`, `U`, `V`, `J`, `Jz`, `hx`, `hz`, `B`, `mu`) are real numbers specified in the text input.
- All text inputs are case-insensitive and flexible in format.
- Only supported combinations will be parsed; invalid or unsupported text will raise a validation error.
- For custom models, extend the schema and parsing logic as needed.
