#!/usr/bin/env python3
"""
Analysis of the Ising model quantum phase transition (energy gap and degeneracy).
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from mcp_server import create_quantum_system, set_lattice, set_hilbert_space, set_hamiltonian, compute_energy_spectrum

def analyze_ising_transition():
    print("Analyzing Ising Model Quantum Phase Transition (Energy Gap and Degeneracy)")
    print("=" * 60)
    L = 16
    Jz = 1.0
    hx_values = np.linspace(0, 2, 21)
    gaps = []
    degeneracies = []
    
    # Create the main analysis system
    sys_id = create_quantum_system("Ising Phase Transition Analysis")['system_id']
    
    for hx in hx_values:
        set_lattice(sys_id, f"chain of {L} sites")
        set_hilbert_space(sys_id, "spin-1/2 on each site")
        set_hamiltonian(sys_id, f"Ising model with Jz={Jz}, hx={hx}")
        spectrum = compute_energy_spectrum(sys_id, num_eigenvalues=5)
        eigvals = spectrum["eigenvalues"]
        gap = eigvals[1] - eigvals[0] if len(eigvals) > 1 else 0.0
        # Count degeneracy (states within 1e-8 of ground state)
        degeneracy = sum(1 for e in eigvals if abs(e - eigvals[0]) < 1e-8)
        gaps.append(gap)
        degeneracies.append(degeneracy)
        print(f"hx={hx:.2f}: gap={gap:.6f}, degeneracy={degeneracy}")
    
    # Create dual-axis plot
    fig, ax1 = plt.subplots(figsize=(8, 6))
    ax2 = ax1.twinx()
    
    # Plot energy gap on primary axis
    line1 = ax1.plot(hx_values, gaps, 'o-', color='blue', label='Energy Gap')
    ax1.set_xlabel('hx (Transverse Field)', fontsize=12)
    ax1.set_ylabel('Energy Gap', color='blue', fontsize=12)
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1.grid(True, alpha=0.3)
    
    # Plot degeneracy on secondary axis
    line2 = ax2.plot(hx_values, degeneracies, 's-', color='red', label='Ground State Degeneracy')
    ax2.set_ylabel('Degeneracy', color='red', fontsize=12)
    ax2.tick_params(axis='y', labelcolor='red')
    ax2.set_ylim(0, 3)  # Degeneracy is typically 1 or 2
    
    # Add legend
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left')
    
    plt.title('Ising Model: Energy Gap and Degeneracy vs. Transverse Field', fontsize=14)
    plt.tight_layout()
    
    # Save plot in the system directory
    system_dir = Path("quantum_systems") / sys_id
    system_dir.mkdir(exist_ok=True)
    plot_path = system_dir / "ising_phase_transition.png"
    plt.savefig(plot_path, dpi=150)
    plt.close()
    print(f"Plot saved to: {plot_path}")
    print("\n✅ Ising gap and degeneracy analysis complete!")

if __name__ == "__main__":
    analyze_ising_transition() 