#!/usr/bin/env python3
"""
Analyse comparative C++ vs Python.
Lit benchmark_cpp.csv et benchmark_python.csv, génère les graphiques et le rapport.
"""
import csv
import os
import sys
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import defaultdict

BENCH_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BENCH_DIR, ".."))
FIGURES_DIR = os.path.join(ROOT_DIR, "results", "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)


def charger_csv(fichier):
    """Charge un fichier CSV de benchmark. Retourne dict[n] -> listes de mesures."""
    data = defaultdict(lambda: {'theta_no': [], 'theta_bh': [], 't_no': [], 't_bh': [],
                                 'cost_init_no': [], 'cost_final_no': [],
                                 'cost_init_bh': [], 'cost_final_bh': []})
    if not os.path.exists(fichier):
        print(f"[ERREUR] Fichier {fichier} introuvable.")
        return {}

    with open(fichier, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            n = int(row['n'])
            data[n]['theta_no'].append(float(row['theta_no']))
            data[n]['t_no'].append(float(row['t_stepping_no']))
            data[n]['theta_bh'].append(float(row['theta_bh']))
            t_bh = float(row['t_stepping_bh'])
            data[n]['t_bh'].append(t_bh if t_bh >= 0 else None)
    return dict(data)


def stats(values):
    """Retourne (mean, max, median) en ms, filtrant les None."""
    v = [x for x in values if x is not None]
    if not v:
        return 0, 0, 0
    arr = np.array(v) * 1000  # convert to ms
    return float(np.mean(arr)), float(np.max(arr)), float(np.median(arr))


def plot_comparaison_init(cpp_data, py_data, tailles):
    """Graphique 1: Temps d'initialisation C++ vs Python."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Nord-Ouest
    ax = axes[0]
    cpp_no = [stats(cpp_data[n]['theta_no'])[2] for n in tailles]
    py_no = [stats(py_data[n]['theta_no'])[2] for n in tailles]
    x = np.arange(len(tailles))
    w = 0.35
    ax.bar(x - w/2, py_no, w, label='Python', color='#3498db', alpha=0.8)
    ax.bar(x + w/2, cpp_no, w, label='C++', color='#e74c3c', alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([str(n) for n in tailles])
    ax.set_xlabel('n')
    ax.set_ylabel('Temps médian (ms)')
    ax.set_title('θ_NO : Nord-Ouest (initialisation)')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_yscale('log')

    # Balas-Hammer
    ax = axes[1]
    cpp_bh = [stats(cpp_data[n]['theta_bh'])[2] for n in tailles]
    py_bh = [stats(py_data[n]['theta_bh'])[2] for n in tailles]
    ax.bar(x - w/2, py_bh, w, label='Python', color='#3498db', alpha=0.8)
    ax.bar(x + w/2, cpp_bh, w, label='C++', color='#e74c3c', alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([str(n) for n in tailles])
    ax.set_xlabel('n')
    ax.set_ylabel('Temps médian (ms)')
    ax.set_title('θ_BH : Balas-Hammer (initialisation)')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_yscale('log')

    plt.suptitle('Comparaison C++ vs Python — Temps d\'initialisation', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, 'comparaison_initialisation.png'), dpi=150)
    plt.close()
    print("[OK] comparaison_initialisation.png")


def plot_comparaison_stepping(cpp_data, py_data, tailles):
    """Graphique 2: Temps du marche-pied C++ vs Python."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    tailles_step = [n for n in tailles if stats(cpp_data[n]['t_no'])[0] > 0]

    x = np.arange(len(tailles_step))
    w = 0.35

    # t_NO
    ax = axes[0]
    cpp_vals = [stats(cpp_data[n]['t_no'])[2] for n in tailles_step]
    py_vals = [stats(py_data[n]['t_no'])[2] for n in tailles_step]
    ax.bar(x - w/2, py_vals, w, label='Python', color='#3498db', alpha=0.8)
    ax.bar(x + w/2, cpp_vals, w, label='C++', color='#e74c3c', alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([str(n) for n in tailles_step])
    ax.set_xlabel('n')
    ax.set_ylabel('Temps médian (ms)')
    ax.set_title('t_NO : Marche-pied après Nord-Ouest')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_yscale('log')

    # t_BH
    ax = axes[1]
    tailles_bh = [n for n in tailles_step if any(v is not None for v in cpp_data[n]['t_bh'])]
    x2 = np.arange(len(tailles_bh))
    cpp_vals = [stats(cpp_data[n]['t_bh'])[2] for n in tailles_bh]
    py_vals = [stats(py_data[n]['t_bh'])[2] for n in tailles_bh]
    ax.bar(x2 - w/2, py_vals, w, label='Python', color='#3498db', alpha=0.8)
    ax.bar(x2 + w/2, cpp_vals, w, label='C++', color='#e74c3c', alpha=0.8)
    ax.set_xticks(x2)
    ax.set_xticklabels([str(n) for n in tailles_bh])
    ax.set_xlabel('n')
    ax.set_ylabel('Temps médian (ms)')
    ax.set_title('t_BH : Marche-pied après Balas-Hammer')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_yscale('log')

    plt.suptitle('Comparaison C++ vs Python — Marche-pied (optimisation)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, 'comparaison_marchepied.png'), dpi=150)
    plt.close()
    print("[OK] comparaison_marchepied.png")


def plot_speedup(cpp_data, py_data, tailles):
    """Graphique 3: Facteur d'accélération (speedup) C++ / Python."""
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))

    speedup_no_init = []
    speedup_bh_init = []
    speedup_no_step = []
    speedup_bh_step = []

    for n in tailles:
        py_no = stats(py_data[n]['theta_no'])[2]
        cpp_no = stats(cpp_data[n]['theta_no'])[2]
        speedup_no_init.append(py_no / cpp_no if cpp_no > 0 else 0)

        py_bh = stats(py_data[n]['theta_bh'])[2]
        cpp_bh = stats(cpp_data[n]['theta_bh'])[2]
        speedup_bh_init.append(py_bh / cpp_bh if cpp_bh > 0 else 0)

        py_t_no = stats(py_data[n]['t_no'])[2]
        cpp_t_no = stats(cpp_data[n]['t_no'])[2]
        speedup_no_step.append(py_t_no / cpp_t_no if cpp_t_no > 0 else 0)

        py_t_bh = stats(py_data[n]['t_bh'])[2]
        cpp_t_bh = stats(cpp_data[n]['t_bh'])[2]
        speedup_bh_step.append(py_t_bh / cpp_t_bh if cpp_t_bh > 0 else 0)

    x = np.arange(len(tailles))
    w = 0.2
    ax.bar(x - 1.5*w, speedup_no_init, w, label='θ_NO', color='steelblue', alpha=0.8)
    ax.bar(x - 0.5*w, speedup_bh_init, w, label='θ_BH', color='darkorange', alpha=0.8)
    ax.bar(x + 0.5*w, speedup_no_step, w, label='t_NO', color='seagreen', alpha=0.8)
    ax.bar(x + 1.5*w, speedup_bh_step, w, label='t_BH', color='crimson', alpha=0.8)

    ax.axhline(y=1, color='black', linestyle='--', linewidth=1)
    ax.set_xticks(x)
    ax.set_xticklabels([str(n) for n in tailles])
    ax.set_xlabel('n', fontsize=12)
    ax.set_ylabel('Speedup (Python / C++)', fontsize=12)
    ax.set_title('Facteur d\'accélération C++ par rapport à Python', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, 'comparaison_speedup.png'), dpi=150)
    plt.close()
    print("[OK] comparaison_speedup.png")


def plot_loglog_compare(cpp_data, py_data, tailles):
    """Graphique 4: Log-log avec courbes de référence."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    x = np.array(tailles, dtype=float)

    # C++
    ax = axes[0]
    theta_no = [stats(cpp_data[n]['theta_no'])[1] for n in tailles]
    theta_bh = [stats(cpp_data[n]['theta_bh'])[1] for n in tailles]
    t_no = [stats(cpp_data[n]['t_no'])[1] for n in tailles]

    ax.loglog(x, theta_no, 'o-', label='θ_NO (C++)', linewidth=2)
    ax.loglog(x, theta_bh, 's-', label='θ_BH (C++)', linewidth=2)
    ax.loglog(x, t_no, '^-', label='t_NO (C++)', linewidth=2)

    # Reference curves
    max_y = max(max(theta_no), max(theta_bh), max(t_no))
    refs = {'O(n)': x, 'O(n²)': x**2, 'O(n³)': x**3}
    for label, y_ref in refs.items():
        y_scaled = y_ref / y_ref[0] * max_y * 0.1
        ax.loglog(x, y_scaled, '--', alpha=0.5, label=label)

    ax.set_xlabel('n')
    ax.set_ylabel('Temps pire cas (ms)')
    ax.set_title('C++ — Complexité (log-log)')
    ax.legend(fontsize=9)
    ax.grid(True, which='both', alpha=0.3)

    # Python
    ax = axes[1]
    theta_no = [stats(py_data[n]['theta_no'])[1] for n in tailles]
    theta_bh = [stats(py_data[n]['theta_bh'])[1] for n in tailles]
    t_no = [stats(py_data[n]['t_no'])[1] for n in tailles]

    ax.loglog(x, theta_no, 'o-', label='θ_NO (Python)', linewidth=2)
    ax.loglog(x, theta_bh, 's-', label='θ_BH (Python)', linewidth=2)
    ax.loglog(x, t_no, '^-', label='t_NO (Python)', linewidth=2)

    max_y = max(max(theta_no), max(theta_bh), max(t_no))
    for label, y_ref in refs.items():
        y_scaled = y_ref / y_ref[0] * max_y * 0.1
        ax.loglog(x, y_scaled, '--', alpha=0.5, label=label)

    ax.set_xlabel('n')
    ax.set_ylabel('Temps pire cas (ms)')
    ax.set_title('Python — Complexité (log-log)')
    ax.legend(fontsize=9)
    ax.grid(True, which='both', alpha=0.3)

    plt.suptitle('Identification de complexité — C++ vs Python', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, 'comparaison_loglog.png'), dpi=150)
    plt.close()
    print("[OK] comparaison_loglog.png")


def plot_total_time(cpp_data, py_data, tailles):
    """Graphique 5: Temps total (init + stepping) comparatif."""
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))

    x = np.array(tailles, dtype=float)

    # Total NO
    cpp_total_no = []
    py_total_no = []
    cpp_total_bh = []
    py_total_bh = []

    for n in tailles:
        c_no = stats(cpp_data[n]['theta_no'])[2] + stats(cpp_data[n]['t_no'])[2]
        p_no = stats(py_data[n]['theta_no'])[2] + stats(py_data[n]['t_no'])[2]
        cpp_total_no.append(c_no)
        py_total_no.append(p_no)

        c_bh = stats(cpp_data[n]['theta_bh'])[2] + stats(cpp_data[n]['t_bh'])[2]
        p_bh = stats(py_data[n]['theta_bh'])[2] + stats(py_data[n]['t_bh'])[2]
        cpp_total_bh.append(c_bh)
        py_total_bh.append(p_bh)

    ax.loglog(x, py_total_no, 'o-', label='Python NO total', linewidth=2, color='#3498db')
    ax.loglog(x, cpp_total_no, 'o--', label='C++ NO total', linewidth=2, color='#2980b9')
    ax.loglog(x, py_total_bh, 's-', label='Python BH total', linewidth=2, color='#e74c3c')
    ax.loglog(x, cpp_total_bh, 's--', label='C++ BH total', linewidth=2, color='#c0392b')

    ax.set_xlabel('n', fontsize=12)
    ax.set_ylabel('Temps total médian (ms)', fontsize=12)
    ax.set_title('Temps total (θ + t) — C++ vs Python', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, which='both', alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, 'comparaison_total.png'), dpi=150)
    plt.close()
    print("[OK] comparaison_total.png")


def generer_rapport(cpp_data, py_data, tailles):
    """Génère le rapport textuel des résultats."""
    print("\n" + "="*70)
    print("RAPPORT COMPARATIF C++ vs PYTHON")
    print("="*70)

    print(f"\n{'n':>6} | {'θ_NO Py (ms)':>12} | {'θ_NO C++ (ms)':>13} | {'Speedup':>8} | "
          f"{'θ_BH Py (ms)':>12} | {'θ_BH C++ (ms)':>13} | {'Speedup':>8}")
    print("-" * 90)

    for n in tailles:
        py_no = stats(py_data[n]['theta_no'])[2]
        cpp_no = stats(cpp_data[n]['theta_no'])[2]
        s_no = py_no / cpp_no if cpp_no > 0 else 0

        py_bh = stats(py_data[n]['theta_bh'])[2]
        cpp_bh = stats(cpp_data[n]['theta_bh'])[2]
        s_bh = py_bh / cpp_bh if cpp_bh > 0 else 0

        print(f"{n:>6} | {py_no:>12.3f} | {cpp_no:>13.3f} | {s_no:>7.1f}x | "
              f"{py_bh:>12.3f} | {cpp_bh:>13.3f} | {s_bh:>7.1f}x")

    print(f"\n{'n':>6} | {'t_NO Py (ms)':>12} | {'t_NO C++ (ms)':>13} | {'Speedup':>8} | "
          f"{'t_BH Py (ms)':>12} | {'t_BH C++ (ms)':>13} | {'Speedup':>8}")
    print("-" * 90)

    for n in tailles:
        py_t_no = stats(py_data[n]['t_no'])[2]
        cpp_t_no = stats(cpp_data[n]['t_no'])[2]
        s_t_no = py_t_no / cpp_t_no if cpp_t_no > 0 else 0

        py_t_bh = stats(py_data[n]['t_bh'])[2]
        cpp_t_bh = stats(cpp_data[n]['t_bh'])[2]
        s_t_bh = py_t_bh / cpp_t_bh if cpp_t_bh > 0 else 0

        print(f"{n:>6} | {py_t_no:>12.3f} | {cpp_t_no:>13.3f} | {s_t_no:>7.1f}x | "
              f"{py_t_bh:>12.3f} | {cpp_t_bh:>13.3f} | {s_t_bh:>7.1f}x")


def main():
    cpp_data = charger_csv(os.path.join(BENCH_DIR, 'benchmark_cpp.csv'))
    py_data = charger_csv(os.path.join(BENCH_DIR, 'benchmark_python.csv'))

    if not cpp_data or not py_data:
        print("Lancez d'abord: ./run_benchmarks.sh")
        sys.exit(1)

    tailles = sorted(set(cpp_data.keys()) & set(py_data.keys()))
    print(f"Tailles communes: {tailles}")

    plot_comparaison_init(cpp_data, py_data, tailles)
    plot_comparaison_stepping(cpp_data, py_data, tailles)
    plot_speedup(cpp_data, py_data, tailles)
    plot_loglog_compare(cpp_data, py_data, tailles)
    plot_total_time(cpp_data, py_data, tailles)
    generer_rapport(cpp_data, py_data, tailles)


if __name__ == '__main__':
    main()
