import sys
import os
import algorithmes as algo


class Logger:
    """Redirige print() vers la console ET un fichier .txt simultanement."""
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "w", encoding="utf-8")

    def write(self, message):
        try:
            self.terminal.write(message)
        except UnicodeEncodeError:
            self.terminal.write(message.encode('ascii', 'replace').decode('ascii'))
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()


EQUIPE = "4"
GROUPE = "9"

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def main():
    os.makedirs(os.path.join(ROOT_DIR, "results", "traces"), exist_ok=True)

    print("=== PROJET RECHERCHE OPERATIONNELLE ===")
    print(f"Groupe : {GROUPE}  |  Equipe : {EQUIPE}")

    continuer = True
    while continuer:
        print("\n=== MENU PRINCIPAL ===")
        print("  1-12 : Numero du probleme a resoudre")
        print("  C    : Lancer l'etude de complexite")
        print("  Q    : Quitter le programme")
        
        choix = input("\nVotre choix : ").strip().upper()
        
        if choix == 'Q':
            continuer = False
            continue
            
        if choix == 'C':
            try:
                import complexite
                complexite.run_complexite()
            except ImportError as e:
                print(f"Erreur lors de l'import de l'etude de complexite : {e}")
            continue

        num_prob = choix
        fichier = os.path.join(ROOT_DIR, "data", "problems", f"probleme{num_prob}.txt")

        try:
            n, m, couts, prov, cmd = algo.charger_donnees(fichier)
        except FileNotFoundError:
            print(f"Fichier '{fichier}' introuvable.")
            continue
        except Exception as e:
            print(f"Erreur de lecture : {e}")
            continue

        print("\nAlgorithme de proposition initiale :")
        print("  1. Nord-Ouest")
        print("  2. Balas-Hammer")
        choix = input("Choix (1/2) : ").strip()

        methode = "no" if choix == "1" else "bh"
        nom_trace = os.path.join(ROOT_DIR, "results", "traces", f"{GROUPE}-{EQUIPE}-trace{num_prob}-{methode}.txt")

        sys.stdout = Logger(nom_trace)
        try:
            _resoudre(n, m, couts, prov, cmd, choix, methode, num_prob)
        finally:
            log = sys.stdout.log
            sys.stdout = sys.stdout.terminal
            log.close()

        print(f"\nTrace sauvegardee dans : {nom_trace}")

        rep = input("\nAutre probleme ? (o/n) : ").strip().lower()
        if rep != 'o':
            continuer = False


def _resoudre(n, m, couts, prov, cmd, choix, methode, num_prob):
    titres_l = [f"P{i + 1}" for i in range(n)]
    titres_c = [f"C{j + 1}" for j in range(m)]

    print(f"\n{'=' * 60}")
    print(f"  PROBLEME {num_prob}  —  Methode : {methode.upper()}")
    print(f"  Fournisseurs : {n}   Clients : {m}")
    print(f"{'=' * 60}")

    algo.afficher_matrice(couts, titres_l, titres_c, "TABLEAU DES COUTS",
                          provisions=prov, commandes=cmd)

    if choix == "1":
        print("\n--- Methode Nord-Ouest ---")
        prop = algo.algo_nord_ouest(prov, cmd)
    else:
        print("\n--- Methode Balas-Hammer ---")
        prop = algo.algo_balas_hammer(couts, prov, cmd)

    algo.afficher_matrice(prop, titres_l, titres_c, "PROPOSITION INITIALE",
                          provisions=prov, commandes=cmd)
    cout_initial = algo.calculer_cout_total(couts, prop)
    print(f"Cout initial : {cout_initial}")

    print(f"\n{'=' * 60}")
    print(f"  METHODE DU MARCHE-PIED AVEC POTENTIEL")
    print(f"{'=' * 60}")

    prop_opt, cout_opt = algo.marche_pied_complet(couts, prop, n, m, afficher=True)


if __name__ == "__main__":
    main()
