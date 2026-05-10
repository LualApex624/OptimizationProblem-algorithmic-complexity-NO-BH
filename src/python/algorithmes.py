import math
from collections import deque

# ==========================================
# 1. LECTURE ET AFFICHAGE
# ==========================================

def charger_donnees(chemin_fichier):
    """Lit un fichier au format :
       n m
       c11 ... c1m p1
       ...
       cn1 ... cnm pn
       d1 ... dm
    """
    with open(chemin_fichier, 'r', encoding='utf-8') as f:
        contenu = f.read()

    mots = contenu.replace(',', ' ').split()
    valeurs = [int(m) for m in mots if m.lstrip('-').isdigit()]

    n, m = valeurs[0], valeurs[1]
    couts, provisions = [], []
    index = 2
    for _ in range(n):
        couts.append(valeurs[index: index + m])
        index += m
        provisions.append(valeurs[index])
        index += 1
    commandes = valeurs[index: index + m]
    return n, m, couts, provisions, commandes


def afficher_matrice(matrice, titres_lignes, titres_colonnes, nom="",
                     provisions=None, commandes=None):
    """Affiche une matrice avec colonnes a largeur fixe.
    
    Si provisions et commandes sont fournis, les affiche en derniere
    colonne / derniere ligne pour reproduire le tableau du sujet.
    """
    # Determiner la largeur optimale
    toutes_valeurs = []
    for ligne in matrice:
        for v in ligne:
            toutes_valeurs.append(v)
    if provisions:
        toutes_valeurs.extend(provisions)
    if commandes:
        toutes_valeurs.extend(commandes)
    toutes_valeurs.extend([len(s) for s in titres_colonnes])
    toutes_valeurs.extend([len(s) for s in titres_lignes])

    max_val_len = max(len(str(v)) for v in toutes_valeurs) if toutes_valeurs else 4
    W = max(max_val_len + 2, 8)   # largeur colonne
    L = max(max(len(s) for s in titres_lignes) + 2, 10) if titres_lignes else 10  # largeur label ligne

    print(f"\n--- {nom} ---")

    # En-tete
    cols = list(titres_colonnes)
    if provisions is not None:
        cols.append("Provisions")
        W_prov = max(W, 12)
    else:
        W_prov = W

    en_tete = " " * L
    for k, c in enumerate(cols):
        w = W_prov if (provisions is not None and k == len(cols) - 1) else W
        en_tete += f"{c:>{w}}"
    print(en_tete)
    print("-" * len(en_tete))

    for i, ligne in enumerate(matrice):
        row = f"{titres_lignes[i]:<{L}}"
        for j in range(len(ligne)):
            row += f"{ligne[j]:>{W}}"
        if provisions is not None:
            row += f"{provisions[i]:>{W_prov}}"
        print(row)

    # Ligne des commandes
    if commandes is not None:
        row = f"{'Commandes':<{L}}"
        for j in range(len(commandes)):
            row += f"{commandes[j]:>{W}}"
        print(row)

    print()


def calculer_cout_total(couts, proposition):
    return sum(
        couts[i][j] * proposition[i][j]
        for i in range(len(couts))
        for j in range(len(couts[0]))
    )


# ==========================================
# 2. PROPOSITIONS INITIALES
# ==========================================

def algo_nord_ouest(provisions, commandes):
    n, m = len(provisions), len(commandes)
    prop = [[0] * m for _ in range(n)]
    prov, cmd = provisions.copy(), commandes.copy()
    i, j = 0, 0
    while i < n and j < m:
        flux = min(prov[i], cmd[j])
        prop[i][j] = flux
        prov[i] -= flux
        cmd[j] -= flux
        if prov[i] == 0 and cmd[j] == 0:
            i += 1
            j += 1
        elif prov[i] == 0:
            i += 1
        else:
            j += 1
    return prop


def penalite(liste):
    """Ecart entre les deux plus petits couts actifs d'une ligne/colonne."""
    valeurs = sorted(v for v in liste if v is not None)
    if len(valeurs) >= 2:
        return valeurs[1] - valeurs[0]
    if len(valeurs) == 1:
        return valeurs[0]
    return -1


def algo_balas_hammer(couts, provisions, commandes, silencieux=False):
    n, m = len(provisions), len(commandes)
    prop = [[0] * m for _ in range(n)]
    prov, cmd = provisions.copy(), commandes.copy()
    actif = [[couts[i][j] for j in range(m)] for i in range(n)]
    etape = 1
    while sum(prov) > 0 and sum(cmd) > 0:
        pen_l = [penalite(actif[i]) if prov[i] > 0 else -1 for i in range(n)]
        pen_c = [penalite([actif[i][j] for i in range(n)]) if cmd[j] > 0 else -1 for j in range(m)]

        max_pl = max(pen_l)
        max_pc = max(pen_c)

        # Trouver toutes les lignes/colonnes de penalite maximale
        lignes_max = [i for i in range(n) if pen_l[i] == max_pl and max_pl >= 0]
        colonnes_max = [j for j in range(m) if pen_c[j] == max_pc and max_pc >= 0]
        if not silencieux:
            print(f"\n  Etape {etape}:")
            print(f"    Penalites lignes   : {pen_l}   -> max = {max_pl}", end="")
            if max_pl >= 0:
                noms = [f"P{i+1}" for i in lignes_max]
                print(f" ({', '.join(noms)})")
            else:
                print()
            print(f"    Penalites colonnes : {pen_c}  -> max = {max_pc}", end="")
            if max_pc >= 0:
                noms = [f"C{j+1}" for j in colonnes_max]
                print(f" ({', '.join(noms)})")
            else:
                print()

        if max_pl >= max_pc:
            i = pen_l.index(max_pl)
            valides = [(actif[i][k], k) for k in range(m) if actif[i][k] is not None and cmd[k] > 0]
            _, j = min(valides)
            if not silencieux:
                print(f"    -> Choisir ligne P{i + 1}, cout min = {actif[i][j]} a ({i + 1},{j + 1})")
        else:
            j = pen_c.index(max_pc)
            valides = [(actif[k][j], k) for k in range(n) if actif[k][j] is not None and prov[k] > 0]
            _, i = min(valides)
            if not silencieux:
                print(f"    -> Choisir colonne C{j + 1}, cout min = {actif[i][j]} a ({i + 1},{j + 1})")

        flux = min(prov[i], cmd[j])
        prop[i][j] = flux
        prov[i] -= flux
        cmd[j] -= flux
        if not silencieux:
            print(f"    -> Allouer {flux} a ({i + 1},{j + 1})")

        if prov[i] == 0:
            for k in range(m):
                actif[i][k] = None
        if cmd[j] == 0:
            for k in range(n):
                actif[k][j] = None

        etape += 1

    return prop


# ==========================================
# 3. MARCHE-PIED (STEPPING STONE)
# ==========================================

# ---------- BFS : Test d'acyclicite ----------

def _construire_graphe_biparti(base, n, m):
    """Construit un graphe biparti (listes d'adjacence) a partir de la base.
    
    Sommets 0..n-1 = fournisseurs (Pi)
    Sommets n..n+m-1 = clients (Cj)
    """
    adj = [[] for _ in range(n + m)]
    for (i, j) in base:
        adj[i].append(n + j)
        adj[n + j].append(i)
    return adj


def test_acyclique_bfs(base, n, m, afficher=True):
    """Test d'acyclicite par parcours en largeur (BFS).
    
    Retourne (est_acyclique, cycle_ou_None).
    Si un cycle est detecte, retourne les aretes du cycle.
    """
    adj = _construire_graphe_biparti(base, n, m)
    visite = [False] * (n + m)
    parent = [-1] * (n + m)

    for depart in range(n + m):
        if visite[depart]:
            continue
        # Verifier qu'il y a des aretes
        if not adj[depart]:
            visite[depart] = True
            continue

        file = deque([depart])
        visite[depart] = True
        parent[depart] = -1

        while file:
            u = file.popleft()
            for v in adj[u]:
                if not visite[v]:
                    visite[v] = True
                    parent[v] = u
                    file.append(v)
                elif v != parent[u]:
                    # Cycle detecte ! Reconstruire le cycle
                    cycle_aretes = _reconstruire_cycle_bfs(parent, u, v, n)
                    if afficher:
                        print(f"  *** Cycle detecte via BFS ***")
                        cycle_affiche = [(i + 1, j - n + 1) for (i, j) in cycle_aretes]
                        print(f"  Cycle : {cycle_affiche}")
                    return False, cycle_aretes

    return True, None


def _reconstruire_cycle_bfs(parent, u, v, n):
    """Reconstruit un cycle a partir du BFS ou u et v sont les 2 extremites."""
    chemin_u = []
    x = u
    while x != -1:
        chemin_u.append(x)
        x = parent[x]
    chemin_v = []
    x = v
    while x != -1:
        chemin_v.append(x)
        x = parent[x]
    set_u = set(chemin_u)
    ancetre = -1
    for x in chemin_v:
        if x in set_u:
            ancetre = x
            break

    # Construire le cycle
    cycle_sommets = []
    for x in chemin_u:
        cycle_sommets.append(x)
        if x == ancetre:
            break
    cycle_sommets.reverse()
    ajout = False
    for x in chemin_v:
        if x == ancetre:
            ajout = True
            continue
        if ajout:
            cycle_sommets.append(x)

    # Convertir en aretes (Pi, Cj)
    aretes = []
    for s in cycle_sommets:
        if s < n:
            # C'est un fournisseur, chercher le client adjacent dans le cycle
            pass
    # Retourner les sommets comme paires (i, j) pour les aretes de la base
    cycle_aretes = []
    for k in range(len(cycle_sommets)):
        s1 = cycle_sommets[k]
        s2 = cycle_sommets[(k + 1) % len(cycle_sommets)]
        if s1 < n:
            cycle_aretes.append((s1, s2))  # (Pi, n+Cj)
        else:
            cycle_aretes.append((s2, s1))  # (Pi, n+Cj)

    # Convertir n+j -> j
    aretes_resultat = []
    for (a, b) in cycle_aretes:
        i_four = a if a < n else b
        j_client = (b - n) if b >= n else (a - n)
        aretes_resultat.append((i_four, j_client))

    return aretes_resultat


# ---------- BFS : Test de connexite ----------

def test_connexe_bfs(base, n, m, afficher=True):
    """Test de connexite par parcours en largeur (BFS).
    
    Retourne (est_connexe, composantes_connexes).
    composantes_connexes = liste de listes de sommets.
    """
    adj = _construire_graphe_biparti(base, n, m)
    visite = [False] * (n + m)
    composantes = []

    for depart in range(n + m):
        if visite[depart]:
            continue
        # BFS
        composante = []
        file = deque([depart])
        visite[depart] = True
        while file:
            u = file.popleft()
            composante.append(u)
            for v in adj[u]:
                if not visite[v]:
                    visite[v] = True
                    file.append(v)
        composantes.append(composante)

    est_connexe = len(composantes) == 1

    if afficher:
        if est_connexe:
            print("  Proposition connexe : OUI")
        else:
            print(f"  Proposition connexe : NON ({len(composantes)} composantes)")
            for k, comp in enumerate(composantes):
                fournisseurs = [f"P{s+1}" for s in comp if s < n]
                clients = [f"C{s-n+1}" for s in comp if s >= n]
                print(f"    Composante {k+1} : {fournisseurs + clients}")

    return est_connexe, composantes


# ---------- Rendre connexe ----------

def rendre_connexe(base, couts, n, m, afficher=True):
    """Ajoute des aretes fictives (flux=0) pour rendre le graphe connexe.
    
    Les aretes sont choisies par cout croissant.
    Retourne la base modifiee et la liste des aretes ajoutees.
    """
    aretes_ajoutees = []

    while True:
        est_connexe, composantes = test_connexe_bfs(base, n, m, afficher=False)
        if est_connexe:
            break

        # Identifier a quelle composante appartient chaque sommet
        comp_id = [-1] * (n + m)
        for k, comp in enumerate(composantes):
            for s in comp:
                comp_id[s] = k

        # Trouver les aretes candidates (hors base) entre composantes differentes
        candidates = []
        for i in range(n):
            for j in range(m):
                if (i, j) not in base:
                    if comp_id[i] != comp_id[n + j]:
                        candidates.append((couts[i][j], i, j))

        if not candidates:
            break

        # Trier par cout croissant
        candidates.sort()
        cout_min, i_best, j_best = candidates[0]
        base.add((i_best, j_best))
        aretes_ajoutees.append((i_best, j_best))

        if afficher:
            print(f"    Ajout arete fictive ({i_best+1},{j_best+1}) de cout {cout_min} pour rendre connexe")

    if afficher and aretes_ajoutees:
        est_connexe2, _ = test_connexe_bfs(base, n, m, afficher=True)

    return base, aretes_ajoutees


# ---------- Potentiels et marginaux ----------

def calculer_potentiels_et_marginaux(couts, prop, n=None, m=None, afficher=True,
                                     base_existante=None):
    """Retourne (u, v, couts_potentiels, marginaux, case_ameliorante, base).

    Effectue les tests BFS de connexite et d'acyclicite.
    Gere la degenerescence.
    Si base_existante est fourni, l'utiliser au lieu de reconstruire depuis prop.
    """
    if n is None:
        n = len(couts)
    if m is None:
        m = len(couts[0])

    # Construire la base : cases avec flux > 0 (ou utiliser la base fournie)
    if base_existante is not None:
        base = set(base_existante)
    else:
        base = set((i, j) for i in range(n) for j in range(m) if prop[i][j] > 0)

    if afficher:
        print(f"\n  Nombre d'aretes dans la base : {len(base)}  (attendu pour arbre : {n + m - 1})")

    est_acyclique, cycle_aretes = test_acyclique_bfs(base, n, m, afficher=afficher)

    if not est_acyclique and cycle_aretes:
        # Maximiser sur le cycle pour le supprimer
        if afficher:
            print("  -> Maximisation sur le cycle detecte pour le supprimer")
        # On enleve l'arete du cycle avec le plus petit flux
        min_flux = float('inf')
        arete_suppr = None
        for (i, j) in cycle_aretes:
            if (i, j) in base and prop[i][j] < min_flux:
                min_flux = prop[i][j]
                arete_suppr = (i, j)
        if arete_suppr and min_flux == 0:
            base.discard(arete_suppr)
            if afficher:
                print(f"    Arete supprimee : ({arete_suppr[0]+1},{arete_suppr[1]+1})")
        elif arete_suppr:
            # Veritable maximisation
            prop, _ = ameliorer_proposition_sur_cycle_base(prop, cycle_aretes, base)
            # Reconstruire la base
            base = set((i, j) for i in range(n) for j in range(m) if prop[i][j] > 0)

    est_connexe, composantes = test_connexe_bfs(base, n, m, afficher=afficher)

    aretes_ajoutees = []
    if not est_connexe:
        base, aretes_ajoutees = rendre_connexe(base, couts, n, m, afficher=afficher)

    u, v = [None] * n, [None] * m
    u[0] = 0

    changed = True
    while changed:
        changed = False
        for (i, j) in base:
            if u[i] is not None and v[j] is None:
                v[j] = couts[i][j] - u[i]
                changed = True
            elif v[j] is not None and u[i] is None:
                u[i] = couts[i][j] - v[j]
                changed = True

    u = [0 if x is None else x for x in u]
    v = [0 if x is None else x for x in v]

    couts_potentiels = [[u[i] + v[j] for j in range(m)] for i in range(n)]
    marginaux = [[None] * m for _ in range(n)]
    min_marg, case_amel = 0, None

    for i in range(n):
        for j in range(m):
            if (i, j) in base:
                marginaux[i][j] = 0  # Par definition, 0 sur la base
            else:
                marg = couts[i][j] - u[i] - v[j]
                marginaux[i][j] = marg
                if marg < min_marg:
                    min_marg = marg
                    case_amel = (i, j)

    return u, v, couts_potentiels, marginaux, case_amel, base, aretes_ajoutees


# ---------- Recherche de cycle pour amelioration ----------

def trouver_cycle(base, depart, n, m):
    """DFS alterne ligne/colonne depuis `depart` pour trouver un cycle elementaire.

    base    : ensemble des cases de base (incluant les eventuelles cases fictives).
    depart  : case entrante (hors base).
    Retourne la liste ordonnee des cases du cycle, ou None si introuvable.
    """
    bases = list(base)

    def dfs(chemin, visite, next_dir):
        curr = chemin[-1]

        # Tentative de fermeture du cycle vers depart
        if len(chemin) >= 4:
            if next_dir == 'H' and curr[0] == depart[0]:
                return chemin
            if next_dir == 'V' and curr[1] == depart[1]:
                return chemin

        if len(chemin) > 2 * (n + m):
            return None

        for node in bases:
            if node in visite:
                continue
            if next_dir == 'H' and node[0] == curr[0]:
                visite.add(node)
                res = dfs(chemin + [node], visite, 'V')
                if res:
                    return res
                visite.discard(node)
            elif next_dir == 'V' and node[1] == curr[1]:
                visite.add(node)
                res = dfs(chemin + [node], visite, 'H')
                if res:
                    return res
                visite.discard(node)
        return None

    # Premier mouvement horizontal (meme ligne que depart)
    for node in bases:
        if node[0] == depart[0]:
            res = dfs([depart, node], {node}, 'V')
            if res:
                return res

    # Premier mouvement vertical (meme colonne que depart)
    for node in bases:
        if node[1] == depart[1]:
            res = dfs([depart, node], {node}, 'H')
            if res:
                return res

    return None


def ameliorer_proposition(prop, cycle, afficher=True):
    """Deplace delta unites le long du cycle (+delta positions paires, -delta impaires).
    
    Affiche les conditions pour chaque case et l'arete supprimee.
    """
    cases_neg = [cycle[k] for k in range(1, len(cycle), 2)]
    delta = min(prop[i][j] for i, j in cases_neg)

    if afficher:
        print(f"  Conditions sur le cycle :")
        for k, (i, j) in enumerate(cycle):
            signe = "+" if k % 2 == 0 else "-"
            val = prop[i][j]
            print(f"    ({i+1},{j+1}) : {signe} delta  (valeur actuelle = {val})")
        print(f"  -> delta = {delta}")

    aretes_supprimees = []
    for k, (i, j) in enumerate(cycle):
        if k % 2 == 0:
            prop[i][j] += delta
        else:
            prop[i][j] -= delta
            if prop[i][j] == 0:
                aretes_supprimees.append((i, j))

    if afficher and aretes_supprimees:
        for (i, j) in aretes_supprimees:
            print(f"  Arete supprimee : ({i+1},{j+1})")

    return prop, delta


def ameliorer_proposition_sur_cycle_base(prop, cycle_aretes, base):
    """Maximisation sur un cycle interne a la base (pour gerer la degenerescence)."""
    # Trouver le min des flux sur les aretes impaires
    min_flux = float('inf')
    arete_suppr = None
    for k, (i, j) in enumerate(cycle_aretes):
        if k % 2 == 1 and (i, j) in base:
            if prop[i][j] < min_flux:
                min_flux = prop[i][j]
                arete_suppr = (i, j)

    if arete_suppr is None or min_flux == float('inf'):
        # Enlever simplement une arete a flux 0
        for (i, j) in cycle_aretes:
            if prop[i][j] == 0 and (i, j) in base:
                base.discard((i, j))
                return prop, 0
        return prop, 0

    for k, (i, j) in enumerate(cycle_aretes):
        if k % 2 == 0:
            prop[i][j] += min_flux
        else:
            prop[i][j] -= min_flux

    return prop, min_flux


# ---------- Boucle complete du marche-pied ----------

def marche_pied_complet(couts, prop, n, m, afficher=True):
    """Execute la boucle complete du marche-pied avec potentiel.
    
    Retourne la proposition optimale et son cout.
    """
    titres_l = [f"P{i + 1}" for i in range(n)]
    titres_c = [f"C{j + 1}" for j in range(m)]

    iteration = 0
    MAX_ITERATIONS = 500  # securite
    base_a_passer = None  # None = reconstruire depuis prop, sinon utiliser cette base

    while iteration < MAX_ITERATIONS:
        if afficher:
            print(f"\n{'─' * 50}")
            print(f"  ITERATION {iteration}")
            print(f"{'─' * 50}")

        # Afficher proposition actuelle
        cout_actuel = calculer_cout_total(couts, prop)
        if afficher:
            afficher_matrice(prop, titres_l, titres_c, "PROPOSITION DE TRANSPORT")
            print(f"  Cout de transport total : {cout_actuel}")
            print()

        # Test de degenerescence + potentiels
        u, v, couts_pot, marginaux, case_amel, base, aretes_ajoutees = \
            calculer_potentiels_et_marginaux(couts, prop, n, m, afficher=afficher,
                                             base_existante=base_a_passer)
        base_a_passer = None  # reset pour la prochaine iteration

        if afficher:
            print(f"\n  Potentiels U (fournisseurs) : {u}")
            print(f"  Potentiels V (clients)      : {v}")
            afficher_matrice(couts_pot, titres_l, titres_c, "TABLE DES COUTS POTENTIELS")
            afficher_matrice(marginaux, titres_l, titres_c, "TABLE DES COUTS MARGINAUX")

        if case_amel is None:
            if afficher:
                print(f"\n*** SOLUTION OPTIMALE atteinte a l'iteration {iteration} ***")
                print(f"Cout total optimal : {cout_actuel}")
                afficher_matrice(prop, titres_l, titres_c, "ALLOCATION FINALE")
            return prop, cout_actuel

        i_a, j_a = case_amel
        if afficher:
            print(f"  Meilleure arete ameliorante : ({i_a + 1},{j_a + 1})"
                  f"  (cout marginal = {marginaux[i_a][j_a]})")

        # Ajout de l'arete ameliorante a la base pour trouver le cycle
        cycle = trouver_cycle(base, case_amel, n, m)

        if cycle is None:
            if afficher:
                print("  ATTENTION : aucun cycle trouve. Arret.")
            return prop, cout_actuel

        cycle_affiche = [(i + 1, j + 1) for i, j in cycle]
        if afficher:
            print(f"  Cycle : {cycle_affiche}")

        prop, delta = ameliorer_proposition(prop, cycle, afficher=afficher)

        if delta == 0:
            if afficher:
                print("  Pivot degenere (delta = 0).")
            # Ajouter l'arete ameliorante dans la base
            base.add(case_amel)
            # Retirer une arete a flux 0 parmi les positions impaires du cycle
            # (celles qui subissaient -delta) pour garantir la progression
            arete_retiree = False
            for k in range(1, len(cycle), 2):
                ci, cj = cycle[k]
                if prop[ci][cj] == 0 and (ci, cj) in base and (ci, cj) != case_amel:
                    base.discard((ci, cj))
                    if afficher:
                        print(f"  -> Retrait de l'arete ({ci+1},{cj+1}) a flux 0 de la base")
                    arete_retiree = True
                    break
            if not arete_retiree:
                # Retirer n'importe quelle arete fictive ajoutee
                if aretes_ajoutees:
                    for (ii, jj) in aretes_ajoutees:
                        if (ii, jj) in base and (ii, jj) != case_amel:
                            base.discard((ii, jj))
                            if afficher:
                                print(f"  -> Retrait arete fictive ({ii+1},{jj+1})")
                            arete_retiree = True
                            break
            # Passer la base modifiee a la prochaine iteration
            base_a_passer = base
            iteration += 1
            continue

        cout_actuel = calculer_cout_total(couts, prop)
        if afficher:
            print(f"  Deplacement de {delta} unites sur le cycle.")
            print(f"  Nouveau cout : {cout_actuel}")

        iteration += 1

    if afficher:
        print(f"\n  Nombre maximal d'iterations atteint ({MAX_ITERATIONS}).")

    return prop, calculer_cout_total(couts, prop)
