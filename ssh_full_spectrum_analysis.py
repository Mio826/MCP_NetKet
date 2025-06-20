#!/usr/bin/env python3
"""
SSH model: full spectrum and edge state profile using MCP tools.
"""
import numpy as np
import matplotlib.pyplot as plt
from mcp_server import create_quantum_system, set_lattice, set_hilbert_space, set_hamiltonian, parameter_sweep, compute_energy_spectrum, analyze_ground_state

def main():
    L = 12
    t1 = 1.0
    ratios = np.linspace(0.1, 2.0, 40)  # t2/t1 values to sweep
    t2_values = (ratios * t1).tolist()
    
    # --- Full spectrum for 1 fermion ---
    n_fermions = 1
    system_id = create_quantum_system("SSH full spectrum")['system_id']
    set_lattice(system_id, f"chain of {L} sites")
    set_hilbert_space(system_id, f"{n_fermions} fermion")
    set_hamiltonian(system_id, f"SSH model with t1={t1}", parameter_ranges={"t2": t2_values})
    sweep = parameter_sweep(system_id, "t2")
    all_eigenvalues = np.array(sweep["all_eigenvalues"])
    plt.figure(figsize=(8, 5))
    for i in range(all_eigenvalues.shape[1]):
        plt.plot(ratios, all_eigenvalues[:, i], color='black', lw=0.8)
    plt.axvline(1.0, color='red', linestyle='--', label='$t_2/t_1 = 1$')
    plt.xlabel('$t_2 / t_1$', fontsize=14)
    plt.ylabel('Eigenvalue', fontsize=14)
    plt.title(f'SSH Spectrum with 1 Fermion on {L} Sites', fontsize=15)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("ssh_full_spectrum.png", dpi=150)
    plt.close()
    print("Saved: ssh_full_spectrum.png")
    
    # --- Edge state profile for zero mode at t2/t1=0.2 (1 spinless fermion) ---
    idx = np.argmin(np.abs(ratios - 0.2))
    t2_topo = t2_values[idx]
    system_id3 = create_quantum_system("SSH zero mode profile")['system_id']
    set_lattice(system_id3, f"chain of {L} sites")
    set_hilbert_space(system_id3, f"1 spinless fermion")
    set_hamiltonian(system_id3, f"SSH model with t1={t1}, t2={t2_topo}")
    spectrum = compute_energy_spectrum(system_id3, num_eigenvalues=L)
    # Extract eigenvalues and eigenvectors
    from mcp_server import json_manager
    system = json_manager.systems[system_id3]
    eigvals = np.array(system.results["energy_spectrum"]["eigenvalues"])
    eigvecs = np.array(system.results["energy_spectrum"]["eigenvectors"])
    zero_idx = np.argmin(np.abs(eigvals))
    psi_zero = eigvecs[:, zero_idx]
    prob_density = np.abs(psi_zero)**2
    plt.figure(figsize=(6, 4))
    plt.plot(range(len(prob_density)), prob_density, 'o-')
    plt.xlabel("Site index")
    plt.ylabel(r"$|\psi(i)|^2$")
    plt.title(f"Spatial profile of zero-energy eigenstate at $t_2/t_1 = {t2_topo/t1:.2f}$ (1 spinless fermion)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("ssh_edge_state_profile.png", dpi=150)
    plt.close()
    print("Saved: ssh_edge_state_profile.png (zero mode, spinless)")

if __name__ == "__main__":
    main() 