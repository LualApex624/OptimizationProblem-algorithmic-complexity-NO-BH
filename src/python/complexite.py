#!/usr/bin/env python3
"""
PARTIE 3 - ETUDE DE COMPLEXITE DU PROJET RECHERCHE OPERATIONNELLE

Mesure et analyse de la complexite des algorithmes de transport:
- Algorithme Nord-Ouest (theta_NO)
- Algorithme Balas-Hammer (theta_BH)
- Methode du marche-pied avec potentiel (tNO, tBH)

Utilisation:
    python3 complexite.py           # Execution de l'etude de complexite
"""

import time
import random
import json
import sys
import os
import algorithmes as algo

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RESULTS_DIR = os.path.join(ROOT_DIR, "results")
FIGURES_DIR = os.path.join(RESULTS_DIR, "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# ==========================================
# GENERATION DE PROBLÈMES ALEATOIRES
# ==========================================

def generer_probleme_aleatoire(n):
    """Genere un probleme de transport aleatoire de taille n x n.
    
    Selon les specifications du projet:
    1. Generer une matrice de coûts avec des valeurs aleatoires entre 1 et 100
    2. Generer une matrice temp avec des valeurs aleatoires entre 1 et 100
    3. Pi = somme des colonnes de temp pour la ligne i
    4. Cj = somme des lignes de temp pour la colonne j
    """
    couts = [[random.randint(1, 100) for _ in range(n)] for _ in range(n)]
    temp = [[random.randint(1, 100) for _ in range(n)] for _ in range(n)]
    
    provisions = [sum(temp[i][j] for j in range(n)) for i in range(n)]
    commandes = [sum(temp[i][j] for i in range(n)) for j in range(n)]
    
    return couts, provisions, commandes


# ==========================================
# MESURE DES TEMPS D'EXECUTION
# ==========================================

def mesurer_nord_ouest(provisions, commandes):
    """Mesure le temps d'execution de l'algorithme Nord-Ouest."""
    debut = time.perf_counter()
    prop = algo.algo_nord_ouest(provisions, commandes)
    fin = time.perf_counter()
    return fin - debut, prop


def mesurer_balas_hammer(couts, provisions, commandes):
    """Mesure le temps d'execution de l'algorithme Balas-Hammer."""
    debut = time.perf_counter()
    prop = algo.algo_balas_hammer(couts, provisions, commandes, silencieux=True)
    fin = time.perf_counter()
    return fin - debut, prop


def mesurer_marche_pied(couts, prop_initiale):
    """Mesure le temps d'execution du marche-pied complet avec potentiel."""
    import copy
    prop = copy.deepcopy(prop_initiale)
    n = len(couts)
    m = len(couts[0])
    debut = time.perf_counter()
    try:
        algo.marche_pied_complet(couts, prop, n, m, afficher=False)
    except Exception:
        pass
    fin = time.perf_counter()
    return fin - debut


# ==========================================
# GESTION DES CHECKPOINTS
# ==========================================

def charger_resultats_existants():
    """Charge les resultats sauvegardes depuis le fichier de checkpoint."""
    fichier_checkpoint = os.path.join(RESULTS_DIR, 'checkpoint_complexite.json')
    if os.path.exists(fichier_checkpoint):
        try:
            with open(fichier_checkpoint, 'r') as f:
                resultats = json.load(f)
            # Convertir les cles en entiers
            resultats = {int(k): v for k, v in resultats.items()}
            print(f"[INFO] Checkpoint charge depuis {fichier_checkpoint}")
            return resultats
        except Exception as e:
            print(f"[WARNING] Erreur lors du chargement du checkpoint: {e}")
            return {}
    else:
        print("[INFO] Aucun checkpoint trouve, demarrage d'une nouvelle etude")
        return {}


def generer_resume_checkpoint(resultats, fichier_resume=None):
    if fichier_resume is None:
        fichier_resume = os.path.join(RESULTS_DIR, 'resultats_complexite.json')
    """Genere le resume JSON des resultats de complexite."""
    donnees_resume = {}
    for n in sorted(resultats.keys()):
        theta_no = resultats[n].get('theta_no', [])
        theta_bh = resultats[n].get('theta_bh', [])
        t_marche_no = resultats[n].get('t_marche_no', [])
        t_marche_bh = resultats[n].get('t_marche_bh', [])

        no_max = max(theta_no) if theta_no else 0
        bh_max = max(theta_bh) if theta_bh else 0
        marche_no_max = max(t_marche_no) if t_marche_no else 0
        marche_bh_max = max(t_marche_bh) if t_marche_bh else 0

        donnees_resume[str(n)] = {
            'n': n,
            'iterations': len(theta_no),
            'theta_NO_pire_cas': no_max,
            'theta_BH_pire_cas': bh_max,
            'tNO_pire_cas': marche_no_max,
            'tBH_pire_cas': marche_bh_max,
            'total_NO_pire_cas': no_max + marche_no_max,
            'total_BH_pire_cas': bh_max + marche_bh_max,
        }

    try:
        with open(fichier_resume, 'w') as f:
            json.dump(donnees_resume, f, indent=2)
        print(f"[OK] Resume sauvegarde dans {fichier_resume}")
    except Exception as e:
        print(f"[ERREUR] Impossible de sauvegarder le resume: {e}")

    return donnees_resume


def sauvegarder_resultats(resultats):
    """Sauvegarde les resultats dans le fichier de checkpoint."""
    fichier_checkpoint = os.path.join(RESULTS_DIR, 'checkpoint_complexite.json')
    try:
        resultats_str = {str(k): v for k, v in resultats.items()}
        with open(fichier_checkpoint, 'w') as f:
            json.dump(resultats_str, f, indent=2)
        print(f"[OK] Checkpoint sauvegarde dans {fichier_checkpoint}")
        generer_resume_checkpoint(resultats)
    except Exception as e:
        print(f"[ERREUR] Impossible de sauvegarder le checkpoint: {e}")


def exporter_resultats_formules():
    """Exporte les resultats du checkpoint dans un format personnalise."""
    resultats = charger_resultats_existants()
    
    if not resultats:
        print("[ERREUR] Aucun checkpoint trouve")
        return
    
    return generer_resume_checkpoint(resultats)



# ==========================================
# ETUDE DE COMPLEXITE
# ==========================================

def etude_complexite_complete():
    """Effectue l'etude complete de complexite selon les specifications du projet.
    
    Mesure pour chaque taille n:
    - theta_NO(n): temps de l'algorithme Nord-Ouest
    - theta_BH(n): temps de l'algorithme Balas-Hammer  
    - tNO(n): temps du marche-pied avec Nord-Ouest
    - tBH(n): temps du marche-pied avec Balas-Hammer
    """
    
    tailles_n = [10, 40, 100, 400, 1000, 4000, 10000]  
    iterations = 100
     
    # Charger les resultats existants si disponibles
    resultats = charger_resultats_existants()
    
    print("="*70)
    print("ETUDE DE COMPLEXITE - PROBLÈMES DE TRANSPORT")
    print("="*70)
    print(f"Nombre d'iterations par taille: {iterations}")
    print(f"Tailles testees: {tailles_n}")
    print()
    
    for n in tailles_n:
        # Verifier si cette taille est deja completee
        if n in resultats and len(resultats[n]['theta_no']) == iterations:
            print(f"\n{'='*70}")
            print(f"TAILLE n = {n} - DEJA COMPLETEE")
            print(f"{'='*70}")
            continue
            
        print(f"\n{'='*70}")
        print(f"TAILLE n = {n}")
        print(f"{'='*70}")
        
        temps_no_list = resultats.get(n, {}).get('theta_no', [])
        temps_bh_list = resultats.get(n, {}).get('theta_bh', [])
        temps_marche_no_list = resultats.get(n, {}).get('t_marche_no', [])
        temps_marche_bh_list = resultats.get(n, {}).get('t_marche_bh', [])
        
        # Continuer depuis ou on s'est arrete
        start_iter = len(temps_no_list)
        
        for iter_num in range(start_iter, iterations):
            couts, provisions, commandes = generer_probleme_aleatoire(n)
            
            t_no, prop_no = mesurer_nord_ouest(provisions, commandes)
            temps_no_list.append(t_no)
            
            t_bh, prop_bh = mesurer_balas_hammer(couts, provisions, commandes)
            temps_bh_list.append(t_bh)
            
            t_marche_no = mesurer_marche_pied(couts, prop_no)
            temps_marche_no_list.append(t_marche_no)
            
            t_marche_bh = mesurer_marche_pied(couts, prop_bh)
            temps_marche_bh_list.append(t_marche_bh)
            
            if (iter_num + 1) % 10 == 0:
                print(f"  Iteration {iter_num + 1}/{iterations} completee")
        
        resultats[n] = {
            'theta_no': temps_no_list,
            'theta_bh': temps_bh_list,
            't_marche_no': temps_marche_no_list,
            't_marche_bh': temps_marche_bh_list,
        }
        
        sauvegarder_resultats(resultats)
        tailles_disponibles = [k for k in resultats.keys() if len(resultats[k]['theta_no']) == iterations]
        tailles_disponibles.sort()
        if tailles_disponibles:
            tracer_tous_les_plots(resultats, tailles_disponibles)
    
    return resultats, tailles_n


# ==========================================
# TRAÇAGE DES RESULTATS
# ==========================================


def _extraire_temps(resultats, n, cle_principale, cle_secondaire=None):
    """Retourne la série de temps en utilisant une clé principale ou un fallback."""
    if cle_principale in resultats[n]:
        return resultats[n][cle_principale]
    if cle_secondaire and cle_secondaire in resultats[n]:
        return resultats[n][cle_secondaire]
    return []


def tracer_nuages(resultats, tailles):
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    fig.suptitle('Nuages de points - 100 réalisations par taille n', fontsize=16, fontweight='bold')

    series = [
        ('theta_no', 'θ_NO(n)', 'steelblue', 0, 0),
        ('theta_bh', 'θ_BH(n)', 'darkorange', 0, 1),
        ('t_no', 't_NO(n)', 'seagreen', 0, 2),
        ('t_bh', 't_BH(n)', 'crimson', 1, 0),
    ]

    for cle, titre, couleur, i, j in series:
        ax = axes[i, j]
        cle_fallback = 't_marche_no' if cle == 't_no' else 't_marche_bh' if cle == 't_bh' else None
        for n in tailles:
            valeurs = _extraire_temps(resultats, n, cle, cle_fallback)
            x = [n] * len(valeurs)
            y = [v * 1000 for v in valeurs]
            ax.scatter(x, y, alpha=0.6, s=20, color=couleur)
        ax.set_xlabel('n')
        ax.set_ylabel('Temps (ms)')
        ax.set_title(titre)
        ax.grid(True, alpha=0.3)

    ax = axes[1, 1]
    for n in tailles:
        theta_no = _extraire_temps(resultats, n, 'theta_no')
        t_no = _extraire_temps(resultats, n, 't_no', 't_marche_no')
        totaux = [(theta_no[i] + t_no[i]) * 1000 for i in range(min(len(theta_no), len(t_no)))]
        x = [n] * len(totaux)
        ax.scatter(x, totaux, alpha=0.6, s=20, color='purple')
    ax.set_xlabel('n')
    ax.set_ylabel('Temps (ms)')
    ax.set_title('(θ_NO + t_NO)(n)')
    ax.grid(True, alpha=0.3)

    ax = axes[1, 2]
    for n in tailles:
        theta_bh = _extraire_temps(resultats, n, 'theta_bh')
        t_bh = _extraire_temps(resultats, n, 't_bh', 't_marche_bh')
        totaux = [(theta_bh[i] + t_bh[i]) * 1000 for i in range(min(len(theta_bh), len(t_bh)))]
        x = [n] * len(totaux)
        ax.scatter(x, totaux, alpha=0.6, s=20, color='saddlebrown')
    ax.set_xlabel('n')
    ax.set_ylabel('Temps (ms)')
    ax.set_title('(θ_BH + t_BH)(n)')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, 'plot1_nuages.png'))
    plt.close(fig)


def tracer_pire_cas(resultats, tailles):
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))

    maxima_theta_no = []
    maxima_theta_bh = []
    maxima_t_no = []
    maxima_t_bh = []
    maxima_total_no = []
    maxima_total_bh = []

    for n in tailles:
        theta_no = _extraire_temps(resultats, n, 'theta_no')
        theta_bh = _extraire_temps(resultats, n, 'theta_bh')
        t_no = _extraire_temps(resultats, n, 't_no', 't_marche_no')
        t_bh = _extraire_temps(resultats, n, 't_bh', 't_marche_bh')

        tot_no = [(theta_no[i] + t_no[i]) * 1000 for i in range(min(len(theta_no), len(t_no)))]
        tot_bh = [(theta_bh[i] + t_bh[i]) * 1000 for i in range(min(len(theta_bh), len(t_bh)))]

        maxima_theta_no.append(max([v * 1000 for v in theta_no]) if theta_no else 0)
        maxima_theta_bh.append(max([v * 1000 for v in theta_bh]) if theta_bh else 0)
        maxima_t_no.append(max([v * 1000 for v in t_no]) if t_no else 0)
        maxima_t_bh.append(max([v * 1000 for v in t_bh]) if t_bh else 0)
        maxima_total_no.append(max(tot_no) if tot_no else 0)
        maxima_total_bh.append(max(tot_bh) if tot_bh else 0)

    ax.plot(tailles, maxima_theta_no, 'o-', label='θ_NO(n)', linewidth=2, markersize=8)
    ax.plot(tailles, maxima_theta_bh, 's-', label='θ_BH(n)', linewidth=2, markersize=8)
    ax.plot(tailles, maxima_t_no, '^-', label='t_NO(n)', linewidth=2, markersize=8)
    ax.plot(tailles, maxima_t_bh, 'v-', label='t_BH(n)', linewidth=2, markersize=8)
    ax.plot(tailles, maxima_total_no, 'D-', label='(θ_NO+t_NO)(n)', linewidth=2, markersize=8)
    ax.plot(tailles, maxima_total_bh, 'x-', label='(θ_BH+t_BH)(n)', linewidth=2, markersize=8)

    ax.set_xlabel('n', fontsize=12)
    ax.set_ylabel('Temps (ms)', fontsize=12)
    ax.set_title('Complexité dans le pire des cas (enveloppe supérieure)', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, 'plot2_pire_cas.png'))
    plt.close(fig)


def tracer_ratio(resultats, tailles):
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))

    ratios = []
    for n in tailles:
        theta_no = _extraire_temps(resultats, n, 'theta_no')
        theta_bh = _extraire_temps(resultats, n, 'theta_bh')
        t_no = _extraire_temps(resultats, n, 't_no', 't_marche_no')
        t_bh = _extraire_temps(resultats, n, 't_bh', 't_marche_bh')

        tot_no = [(theta_no[i] + t_no[i]) for i in range(min(len(theta_no), len(t_no)))]
        tot_bh = [(theta_bh[i] + t_bh[i]) for i in range(min(len(theta_bh), len(t_bh)))]

        ratio = max(tot_no) / max(tot_bh) if tot_bh and max(tot_bh) > 0 else float('inf')
        ratios.append(ratio)

    x = list(range(len(tailles)))
    colors = ['seagreen' if r < 1 else 'crimson' for r in ratios]
    ax.bar(x, ratios, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    ax.axhline(y=1, color='black', linestyle='--', linewidth=2, label='Égalité')

    ax.set_xlabel('n', fontsize=12)
    ax.set_ylabel('Ratio', fontsize=12)
    ax.set_title('Ratio pire cas : (θ_NO + t_NO) / (θ_BH + t_BH)', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([str(n) for n in tailles])
    ax.grid(True, alpha=0.3, axis='y')
    ax.legend(fontsize=10)

    for xi, ratio in zip(x, ratios):
        ax.text(xi, ratio + 0.02, f'{ratio:.2f}', ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, 'plot3_ratio.png'))
    plt.close(fig)


def tracer_loglog(resultats, tailles):
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))

    x = np.array(tailles)
    series = {
        'θ_NO(n)': [max([v * 1000 for v in _extraire_temps(resultats, n, 'theta_no')]) if _extraire_temps(resultats, n, 'theta_no') else 0 for n in tailles],
        'θ_BH(n)': [max([v * 1000 for v in _extraire_temps(resultats, n, 'theta_bh')]) if _extraire_temps(resultats, n, 'theta_bh') else 0 for n in tailles],
        't_NO(n)': [max([v * 1000 for v in _extraire_temps(resultats, n, 't_no', 't_marche_no')]) if _extraire_temps(resultats, n, 't_no', 't_marche_no') else 0 for n in tailles],
        't_BH(n)': [max([v * 1000 for v in _extraire_temps(resultats, n, 't_bh', 't_marche_bh')]) if _extraire_temps(resultats, n, 't_bh', 't_marche_bh') else 0 for n in tailles],
    }

    series['(θ_NO+t_NO)(n)'] = [max([( _extraire_temps(resultats, n, 'theta_no')[i] + _extraire_temps(resultats, n, 't_no', 't_marche_no')[i]) * 1000 for i in range(min(len(_extraire_temps(resultats, n, 'theta_no')), len(_extraire_temps(resultats, n, 't_no', 't_marche_no'))))]) if min(len(_extraire_temps(resultats, n, 'theta_no')), len(_extraire_temps(resultats, n, 't_no', 't_marche_no'))) > 0 else 0 for n in tailles]
    series['(θ_BH+t_BH)(n)'] = [max([( _extraire_temps(resultats, n, 'theta_bh')[i] + _extraire_temps(resultats, n, 't_bh', 't_marche_bh')[i]) * 1000 for i in range(min(len(_extraire_temps(resultats, n, 'theta_bh')), len(_extraire_temps(resultats, n, 't_bh', 't_marche_bh'))))]) if min(len(_extraire_temps(resultats, n, 'theta_bh')), len(_extraire_temps(resultats, n, 't_bh', 't_marche_bh'))) > 0 else 0 for n in tailles]

    for label, y in series.items():
        if any(y):
            ax.plot(x, y, marker='o', label=label)

    refs = {
        'O(n)': lambda x: x,
        'O(n log n)': lambda x: x * np.log(x),
        'O(n²)': lambda x: x ** 2,
        'O(n³)': lambda x: x ** 3,
    }
    if x[0] > 0:
        max_actual = max(max(y) for y in series.values() if any(y)) or 1
        for label, func in refs.items():
            y_ref = func(x.astype(float))
            y_ref = y_ref / y_ref[0] * max_actual
            ax.plot(x, y_ref, linestyle='--', label=label)

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('n', fontsize=12)
    ax.set_ylabel('Temps (ms)', fontsize=12)
    ax.set_title('Identification de la complexité (log-log)', fontsize=14, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, which='both', alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, 'plot4_loglog.png'))
    plt.close(fig)


def tracer_tous_les_plots(resultats, tailles):
    tracer_nuages(resultats, tailles)
    tracer_pire_cas(resultats, tailles)
    tracer_ratio(resultats, tailles)
    tracer_loglog(resultats, tailles)


def identifier_complexite(tailles, temps_max):
    """Identifie le type de complexite base sur l'enveloppe superieure.
    
    Teste: O(log n), O(n), O(n log n), O(n²), O(n³), O(k^n)
    Retourne le type ayant le meilleur R²
    """
    types_complexite = {
        'O(log n)': lambda n: np.log(n),
        'O(n)': lambda n: n,
        'O(n log n)': lambda n: n * np.log(n),
        'O(n²)': lambda n: n ** 2,
        'O(n³)': lambda n: n ** 3,
    }
    
    meilleur_type = None
    meilleur_r2 = -np.inf
    
    for nom, func in types_complexite.items():
        y_pred = np.array([func(n) for n in tailles])
        y_true = np.array(temps_max)
        
        y_pred_norm = y_pred / np.max(y_pred)
        y_true_norm = y_true / np.max(y_true)
        
        ss_res = np.sum((y_true_norm - y_pred_norm) ** 2)
        ss_tot = np.sum((y_true_norm - np.mean(y_true_norm)) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        if r2 > meilleur_r2:
            meilleur_r2 = r2
            meilleur_type = nom
    
    return meilleur_type, meilleur_r2






# ==========================================
# PROGRAMME PRINCIPAL
# ==========================================

def afficher_usage():
    """Affiche le message d'aide."""
    print("""
ETUDE DE COMPLEXITE - PROBLÈMES DE TRANSPORT

Usage:
    python3 complexite.py              # Execution complete (graphiques)
    python3 complexite.py --help       # Affiche cette aide
    """)


def run_complexite():
    """Lance l'etude complete de complexite, incluant l'identification et les graphiques."""
    print("\n" + "="*70)
    print("ANALYSE DE COMPLEXITE - PROBLÈMES DE TRANSPORT")
    print("="*70 + "\n")
    
    resultats, tailles_n = etude_complexite_complete()
    
    tailles_completees = [n for n in tailles_n if n in resultats and len(resultats[n]['theta_no']) == 100]
    
    if len(tailles_completees) == len(tailles_n):
        print("\n" + "="*70)
        print("IDENTIFICATION DES COMPLEXITES")
        print("="*70)
        
        maxima_no = [max(resultats[n]['theta_no']) for n in tailles_n]
        maxima_bh = [max(resultats[n]['theta_bh']) for n in tailles_n]
        maxima_marche_no = [max(resultats[n]['t_marche_no']) for n in tailles_n]
        maxima_marche_bh = [max(resultats[n]['t_marche_bh']) for n in tailles_n]
        
        type_no, r2_no = identifier_complexite(tailles_n, maxima_no)
        type_bh, r2_bh = identifier_complexite(tailles_n, maxima_bh)
        type_marche_no, r2_marche_no = identifier_complexite(tailles_n, maxima_marche_no)
        type_marche_bh, r2_marche_bh = identifier_complexite(tailles_n, maxima_marche_bh)
        
        print(f"\ntheta_NO(n)  : {type_no} (R² = {r2_no:.4f})")
        print(f"theta_BH(n)  : {type_bh} (R² = {r2_bh:.4f})")
        print(f"tNO(n)  : {type_marche_no} (R² = {r2_marche_no:.4f})")
        print(f"tBH(n)  : {type_marche_bh} (R² = {r2_marche_bh:.4f})")
        
        print("\n" + "="*70)
        print("GENERATION DES GRAPHIQUES FINAUX")
        print("="*70)
        
        tracer_tous_les_plots(resultats, tailles_n)
        
        generer_resume_checkpoint(resultats)
        print("\n" + "="*70)
        print("ETUDE TERMINEE")
        print("="*70)
    else:
        print("\n" + "="*70)
        print("ETUDE EN COURS")
        print("="*70)
        print(f"Tailles completees: {tailles_completees}")
        print(f"Tailles restantes: {[n for n in tailles_n if n not in tailles_completees]}")
        print("Relancer le programme pour continuer l'etude.")
        print("="*70)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg == '--help' or arg == '-h':
            afficher_usage()
            sys.exit(0)
        
        else:
            print(f"[ERREUR] Argument inconnu: {arg}")
            afficher_usage()
            sys.exit(1)
            
    run_complexite()
