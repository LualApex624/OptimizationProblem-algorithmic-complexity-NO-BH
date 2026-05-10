#!/usr/bin/env python3
"""
Benchmark Python pour comparaison avec C++.
Génère benchmark_python.csv avec les mêmes métriques.
"""
import time
import random
import csv
import sys
import os
import copy

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT_DIR, "src", "python"))
import algorithmes as algo

BENCH_DIR = os.path.dirname(os.path.abspath(__file__))


def generer_probleme_aleatoire(n, rng):
    couts = [[rng.randint(1, 100) for _ in range(n)] for _ in range(n)]
    temp = [[rng.randint(1, 100) for _ in range(n)] for _ in range(n)]
    provisions = [sum(temp[i][j] for j in range(n)) for i in range(n)]
    commandes = [sum(temp[i][j] for i in range(n)) for j in range(n)]
    return couts, provisions, commandes


def run_benchmark():
    tailles = [10, 40, 100, 400, 1000, 2000]
    iterations = 50

    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        tailles = [10, 40, 100, 400]
        iterations = 20

    if len(sys.argv) > 1 and sys.argv[1] == '--single':
        n_val = int(sys.argv[2]) if len(sys.argv) > 2 else 100
        iters = int(sys.argv[3]) if len(sys.argv) > 3 else 10
        tailles = [n_val]
        iterations = iters

    rng = random.Random(42)

    with open(os.path.join(BENCH_DIR, 'benchmark_python.csv'), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['n', 'iter', 'theta_no', 't_stepping_no', 'cost_init_no', 'cost_final_no',
                         'theta_bh', 't_stepping_bh', 'cost_init_bh', 'cost_final_bh'])

        print("=== Python Transport Problem Benchmark ===")
        print(f"Sizes: {tailles}")
        print(f"Iterations per size: {iterations}\n")

        for n in tailles:
            print(f"n={n} ({iterations} iterations)...", end='', flush=True)

            for it in range(iterations):
                couts, provisions, commandes = generer_probleme_aleatoire(n, rng)

                # Nord-Ouest
                t0 = time.perf_counter()
                prop_no = algo.algo_nord_ouest(provisions, commandes)
                t1 = time.perf_counter()
                theta_no = t1 - t0
                cost_init_no = algo.calculer_cout_total(couts, prop_no)

                t2 = time.perf_counter()
                try:
                    prop_no_copy = copy.deepcopy(prop_no)
                    opt_no, cost_final_no = algo.marche_pied_complet(couts, prop_no_copy, n, n, afficher=False)
                except Exception:
                    cost_final_no = -1
                t3 = time.perf_counter()
                t_stepping_no = t3 - t2

                # Balas-Hammer
                t0 = time.perf_counter()
                prop_bh = algo.algo_balas_hammer(couts, provisions, commandes, silencieux=True)
                t1 = time.perf_counter()
                theta_bh = t1 - t0
                cost_init_bh = algo.calculer_cout_total(couts, prop_bh)

                if n <= 2000:
                    t2 = time.perf_counter()
                    try:
                        prop_bh_copy = copy.deepcopy(prop_bh)
                        opt_bh, cost_final_bh = algo.marche_pied_complet(couts, prop_bh_copy, n, n, afficher=False)
                    except Exception:
                        cost_final_bh = -1
                    t3 = time.perf_counter()
                    t_stepping_bh = t3 - t2
                else:
                    t_stepping_bh = -1
                    cost_final_bh = -1

                writer.writerow([n, it, theta_no, t_stepping_no, cost_init_no, cost_final_no,
                                 theta_bh, t_stepping_bh, cost_init_bh, cost_final_bh])

                if (it + 1) % 10 == 0:
                    print(f" {it+1}", end='', flush=True)

            print(" done.")

    print("\nResults saved to benchmark_python.csv")


if __name__ == '__main__':
    run_benchmark()
