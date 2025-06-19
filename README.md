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