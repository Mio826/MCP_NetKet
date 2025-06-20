#!/usr/bin/env python3
"""
Analysis of the Transverse-Field Ising Model quantum phase transition (energy gap and degeneracy).
"""

import numpy as np
import matplotlib.pyplot as plt
from mcp_server import create_quantum_system, set_lattice, set_hilbert_space, set_hamiltonian, compute_energy_spectrum

def analyze_ising_transition():
    print("Analyzing Ising Model Quantum Phase Transition (Energy Gap and Degeneracy)")
    print("=" * 50)
    L = 12
    Jz = 1.0
    hx_values = np.linspace(0, 2, 21)
    gaps = []
    degeneracies = []
    for hx in hx_values:
        system_id = create_quantum_system(f"Ising hx={hx}")['system_id']
        set_lattice(system_id, f"chain of {L} sites")
        set_hilbert_space(system_id, "spin-1/2 on each site")
        set_hamiltonian(system_id, f"Ising model with Jz={Jz}, hx={hx}")
        spectrum = compute_energy_spectrum(system_id, num_eigenvalues=4)
        eigvals = np.array(spectrum["eigenvalues"])
        gap = eigvals[1] - eigvals[0]
        gaps.append(gap)
        # Count degeneracy: number of eigenvalues within 1e-8 of ground state
        degeneracy = np.sum(np.abs(eigvals - eigvals[0]) < 1e-8)
        degeneracies.append(degeneracy)
        print(f"hx={hx:.2f}: gap={gap:.6f}, degeneracy={degeneracy}")
    # Plot
    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax1.plot(hx_values, gaps, 'o-', color='red', label='Energy Gap')
    ax1.set_xlabel('hx')
    ax1.set_ylabel('Energy Gap', color='red')
    ax1.tick_params(axis='y', labelcolor='red')
    ax2 = ax1.twinx()
    ax2.plot(hx_values, degeneracies, 's--', color='blue', label='Degeneracy')
    ax2.set_ylabel('Ground State Degeneracy', color='blue')
    ax2.tick_params(axis='y', labelcolor='blue')
    plt.title('Ising Model: Energy Gap and Degeneracy vs. $h_x$')
    fig.tight_layout()
    plt.savefig("ising_phase_transition.png", dpi=150)
    plt.close()
    print("Plot saved to: ising_phase_transition.png")
    print("\n✅ Ising gap and degeneracy analysis complete!")

if __name__ == "__main__":
    analyze_ising_transition() 