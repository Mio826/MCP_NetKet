#!/usr/bin/env python3
"""
Analysis of the Hubbard model metal-insulator transition (Mott gap).
"""

import numpy as np
import matplotlib.pyplot as plt
from mcp_server import create_quantum_system, set_lattice, set_hilbert_space, set_hamiltonian, compute_energy_spectrum

def analyze_hubbard_transition():
    print("Analyzing Hubbard Model Metal-Insulator Transition (Mott gap)")
    print("=" * 50)
    L = 10
    t = 1.0
    U_values = np.linspace(0, 8, 17)
    N = L  # half-filling for spin-1/2 fermions
    gs_energies = []
    gap_mott = []
    for U in U_values:
        # E0(N)
        sys_N = create_quantum_system(f"Hubbard N={N} U={U}")['system_id']
        set_lattice(sys_N, f"chain of {L} sites")
        set_hilbert_space(sys_N, f"{N} fermions with spin-1/2")
        set_hamiltonian(sys_N, f"Hubbard model with t={t}, U={U}")
        e0_N = compute_energy_spectrum(sys_N, num_eigenvalues=1)["ground_state_energy"]
        # E0(N+1)
        sys_Np1 = create_quantum_system(f"Hubbard N={N+1} U={U}")['system_id']
        set_lattice(sys_Np1, f"chain of {L} sites")
        set_hilbert_space(sys_Np1, f"{N+1} fermions with spin-1/2")
        set_hamiltonian(sys_Np1, f"Hubbard model with t={t}, U={U}")
        e0_Np1 = compute_energy_spectrum(sys_Np1, num_eigenvalues=1)["ground_state_energy"]
        # E0(N-1)
        sys_Nm1 = create_quantum_system(f"Hubbard N={N-1} U={U}")['system_id']
        set_lattice(sys_Nm1, f"chain of {L} sites")
        set_hilbert_space(sys_Nm1, f"{N-1} fermions with spin-1/2")
        set_hamiltonian(sys_Nm1, f"Hubbard model with t={t}, U={U}")
        e0_Nm1 = compute_energy_spectrum(sys_Nm1, num_eigenvalues=1)["ground_state_energy"]
        gs_energies.append(e0_N)
        gap_mott.append(e0_Np1 + e0_Nm1 - 2 * e0_N)
        print(f"U={U:.2f}: E0(N)={e0_N:.3f}, gap={gap_mott[-1]:.3f}")
    # Plot only the Mott gap
    plt.figure(figsize=(7, 5))
    plt.plot(U_values, gap_mott, 'o-', color='red')
    plt.xlabel('U')
    plt.ylabel('Mott Gap')
    plt.title('Hubbard Model: Mott Gap vs. U')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("hubbard_phase_transition.png", dpi=150)
    plt.close()
    print("Plot saved to: hubbard_phase_transition.png")
    print("\n✅ Hubbard Mott gap analysis complete!")

if __name__ == "__main__":
    analyze_hubbard_transition() 