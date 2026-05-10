#include <iostream>
#include <vector>
#include <algorithm>
#include <numeric>
#include <random>
#include <chrono>
#include <fstream>
#include <sstream>
#include <cmath>
#include <queue>
#include <set>
#include <climits>
#include <cstring>

// Flattened matrix for cache-friendly access
struct Matrix {
    std::vector<int> data;
    int rows, cols;

    Matrix() : rows(0), cols(0) {}
    Matrix(int r, int c, int val = 0) : data(r * c, val), rows(r), cols(c) {}

    int& operator()(int i, int j) { return data[i * cols + j]; }
    const int& operator()(int i, int j) const { return data[i * cols + j]; }
};

struct Problem {
    int n, m;
    Matrix couts;
    std::vector<int> provisions;
    std::vector<int> commandes;
};

struct BenchResult {
    double theta_init;   // seconds
    double t_stepping;   // seconds
    long long cost_init;
    long long cost_final;
};

// ==========================================
// GENERATION DE PROBLEMES ALEATOIRES
// ==========================================

Problem generer_probleme_aleatoire(int n, std::mt19937& rng) {
    Problem p;
    p.n = n;
    p.m = n;
    p.couts = Matrix(n, n);
    p.provisions.resize(n, 0);
    p.commandes.resize(n, 0);

    std::uniform_int_distribution<int> dist(1, 100);

    for (int i = 0; i < n; ++i)
        for (int j = 0; j < n; ++j)
            p.couts(i, j) = dist(rng);

    // Generate temp matrix and derive provisions/commandes
    std::vector<int> temp(n * n);
    for (int i = 0; i < n * n; ++i)
        temp[i] = dist(rng);

    for (int i = 0; i < n; ++i)
        for (int j = 0; j < n; ++j) {
            p.provisions[i] += temp[i * n + j];
            p.commandes[j] += temp[i * n + j];
        }

    return p;
}

// ==========================================
// ALGORITHME NORD-OUEST
// ==========================================

Matrix algo_nord_ouest(const std::vector<int>& provisions, const std::vector<int>& commandes) {
    int n = provisions.size(), m = commandes.size();
    Matrix prop(n, m, 0);
    std::vector<int> prov(provisions), cmd(commandes);

    int i = 0, j = 0;
    while (i < n && j < m) {
        int flux = std::min(prov[i], cmd[j]);
        prop(i, j) = flux;
        prov[i] -= flux;
        cmd[j] -= flux;
        if (prov[i] == 0 && cmd[j] == 0) { ++i; ++j; }
        else if (prov[i] == 0) ++i;
        else ++j;
    }
    return prop;
}

// ==========================================
// ALGORITHME BALAS-HAMMER
// ==========================================

int penalite(const std::vector<int>& liste, const std::vector<bool>& actif, int taille) {
    int min1 = INT_MAX, min2 = INT_MAX;
    int count = 0;
    for (int k = 0; k < taille; ++k) {
        if (!actif[k]) continue;
        int v = liste[k];
        if (v < min1) { min2 = min1; min1 = v; }
        else if (v < min2) { min2 = v; }
        ++count;
    }
    if (count >= 2) return min2 - min1;
    if (count == 1) return min1;
    return -1;
}

Matrix algo_balas_hammer(const Matrix& couts, const std::vector<int>& provisions,
                         const std::vector<int>& commandes) {
    int n = provisions.size(), m = commandes.size();
    Matrix prop(n, m, 0);
    std::vector<int> prov(provisions), cmd(commandes);

    std::vector<bool> row_active(n, true);
    std::vector<bool> col_active(m, true);
    // Active cost tracking: -1 means inactive
    Matrix actif(n, m);
    for (int i = 0; i < n; ++i)
        for (int j = 0; j < m; ++j)
            actif(i, j) = couts(i, j);

    int remaining = std::accumulate(prov.begin(), prov.end(), 0);

    std::vector<int> row_buf(m), col_buf(n);

    while (remaining > 0) {
        int max_pl = -1, max_pc = -1;
        int best_row = -1, best_col = -1;

        // Compute row penalties
        for (int i = 0; i < n; ++i) {
            if (!row_active[i]) continue;
            // Extract active costs in row i
            int min1 = INT_MAX, min2 = INT_MAX;
            int count = 0;
            for (int j = 0; j < m; ++j) {
                if (!col_active[j]) continue;
                int v = actif(i, j);
                if (v < min1) { min2 = min1; min1 = v; }
                else if (v < min2) { min2 = v; }
                ++count;
            }
            int pen;
            if (count >= 2) pen = min2 - min1;
            else if (count == 1) pen = min1;
            else pen = -1;

            if (pen > max_pl) { max_pl = pen; best_row = i; }
        }

        // Compute column penalties
        for (int j = 0; j < m; ++j) {
            if (!col_active[j]) continue;
            int min1 = INT_MAX, min2 = INT_MAX;
            int count = 0;
            for (int i = 0; i < n; ++i) {
                if (!row_active[i]) continue;
                int v = actif(i, j);
                if (v < min1) { min2 = min1; min1 = v; }
                else if (v < min2) { min2 = v; }
                ++count;
            }
            int pen;
            if (count >= 2) pen = min2 - min1;
            else if (count == 1) pen = min1;
            else pen = -1;

            if (pen > max_pc) { max_pc = pen; best_col = j; }
        }

        int i_sel, j_sel;
        if (max_pl >= max_pc) {
            i_sel = best_row;
            // Find min cost in this row among active columns
            int min_cost = INT_MAX;
            j_sel = -1;
            for (int j = 0; j < m; ++j) {
                if (!col_active[j]) continue;
                if (actif(i_sel, j) < min_cost) {
                    min_cost = actif(i_sel, j);
                    j_sel = j;
                }
            }
        } else {
            j_sel = best_col;
            // Find min cost in this column among active rows
            int min_cost = INT_MAX;
            i_sel = -1;
            for (int i = 0; i < n; ++i) {
                if (!row_active[i]) continue;
                if (actif(i, j_sel) < min_cost) {
                    min_cost = actif(i, j_sel);
                    i_sel = i;
                }
            }
        }

        if (i_sel < 0 || j_sel < 0) break;

        int flux = std::min(prov[i_sel], cmd[j_sel]);
        prop(i_sel, j_sel) = flux;
        prov[i_sel] -= flux;
        cmd[j_sel] -= flux;
        remaining -= flux;

        if (prov[i_sel] == 0) row_active[i_sel] = false;
        if (cmd[j_sel] == 0) col_active[j_sel] = false;
    }

    return prop;
}

// ==========================================
// MARCHE-PIED (STEPPING STONE)
// ==========================================

long long calculer_cout_total(const Matrix& couts, const Matrix& prop) {
    long long total = 0;
    int n = couts.rows, m = couts.cols;
    for (int i = 0; i < n; ++i)
        for (int j = 0; j < m; ++j)
            total += (long long)couts(i, j) * prop(i, j);
    return total;
}

struct Base {
    std::vector<std::pair<int,int>> cells;
    std::vector<std::vector<int>> row_cells; // for each row, list of columns in base
    std::vector<std::vector<int>> col_cells; // for each col, list of rows in base
    int n, m;

    Base(int n, int m) : n(n), m(m), row_cells(n), col_cells(m) {}

    void add(int i, int j) {
        cells.emplace_back(i, j);
        row_cells[i].push_back(j);
        col_cells[j].push_back(i);
    }

    void rebuild(const Matrix& prop) {
        cells.clear();
        for (auto& v : row_cells) v.clear();
        for (auto& v : col_cells) v.clear();
        for (int i = 0; i < n; ++i)
            for (int j = 0; j < m; ++j)
                if (prop(i, j) > 0) add(i, j);
    }
};

bool calculer_potentiels(const Matrix& couts, const Base& base, int n, int m,
                         std::vector<int>& u, std::vector<int>& v) {
    u.assign(n, INT_MIN);
    v.assign(m, INT_MIN);
    u[0] = 0;

    bool changed = true;
    int passes = 0;
    while (changed && passes < n + m) {
        changed = false;
        for (auto& [i, j] : base.cells) {
            if (u[i] != INT_MIN && v[j] == INT_MIN) {
                v[j] = couts(i, j) - u[i];
                changed = true;
            } else if (v[j] != INT_MIN && u[i] == INT_MIN) {
                u[i] = couts(i, j) - v[j];
                changed = true;
            }
        }
        ++passes;
    }

    // Fill remaining with 0
    for (int i = 0; i < n; ++i) if (u[i] == INT_MIN) u[i] = 0;
    for (int j = 0; j < m; ++j) if (v[j] == INT_MIN) v[j] = 0;
    return true;
}

// Find cycle using BFS-based approach on the base graph
std::vector<std::pair<int,int>> trouver_cycle(const Base& base, int si, int sj, int n, int m) {
    // DFS alternating row/col from (si, sj)
    struct Frame {
        int i, j;
        bool horizontal; // next move direction
        int idx;         // iteration index in the neighbor list
    };

    // Build fast lookup: is (i,j) in base?
    // Use row_cells for lookup
    auto in_base = [&](int i, int j) -> bool {
        for (int c : base.row_cells[i])
            if (c == j) return true;
        return false;
    };

    // DFS with explicit stack
    std::vector<std::pair<int,int>> path;
    path.push_back({si, sj});

    // Try starting horizontal (same row)
    for (int start_dir = 0; start_dir < 2; ++start_dir) {
        path.resize(1);
        // Mark visited cells
        std::vector<std::vector<bool>> visited(n, std::vector<bool>(m, false));

        struct StackFrame {
            bool horizontal;
            int iter_idx;
        };
        std::vector<StackFrame> stack;

        bool first_horizontal = (start_dir == 0);

        // Find first neighbor
        auto get_neighbors = [&](int ci, int cj, bool horiz) -> std::vector<std::pair<int,int>>* {
            static std::vector<std::pair<int,int>> result;
            result.clear();
            if (horiz) {
                // Same row as (ci, cj), different column
                for (int col : base.row_cells[ci]) {
                    if (col == cj) continue;
                    if (visited[ci][col]) continue;
                    result.push_back({ci, col});
                }
            } else {
                // Same col as (ci, cj), different row
                for (int row : base.col_cells[cj]) {
                    if (row == ci) continue;
                    if (visited[row][cj]) continue;
                    result.push_back({row, cj});
                }
            }
            return &result;
        };

        // Initial expansion
        bool found = false;
        std::vector<std::pair<int,int>> neighbors_storage;

        // Use recursive DFS with iterative stack
        struct DFSState {
            int i, j;
            bool next_horiz;
            std::vector<std::pair<int,int>> neighbors;
            int idx;
        };

        std::vector<DFSState> dfs_stack;
        DFSState init;
        init.i = si; init.j = sj;
        init.next_horiz = !first_horizontal; // after first move
        // First move
        if (first_horizontal) {
            for (int col : base.row_cells[si]) {
                if (col == sj) continue;
                init.neighbors.push_back({si, col});
            }
        } else {
            for (int row : base.col_cells[sj]) {
                if (row == si) continue;
                init.neighbors.push_back({row, sj});
            }
        }
        init.idx = 0;
        dfs_stack.push_back(std::move(init));

        while (!dfs_stack.empty() && !found) {
            auto& top = dfs_stack.back();
            if (top.idx >= (int)top.neighbors.size()) {
                // Backtrack
                if (dfs_stack.size() > 1) {
                    auto& prev = dfs_stack[dfs_stack.size() - 2];
                    auto [pi, pj] = prev.neighbors[prev.idx - 1];
                    visited[pi][pj] = false;
                    path.pop_back();
                }
                dfs_stack.pop_back();
                continue;
            }

            auto [ni, nj] = top.neighbors[top.idx];
            ++top.idx;

            // Check if this closes the cycle
            bool closes = false;
            if (path.size() >= 3) {
                if (first_horizontal) {
                    // Alternating: H, V, H, V...
                    // Current level parity determines direction
                    bool cur_horiz = ((dfs_stack.size()) % 2 == 1) == first_horizontal;
                    if (!cur_horiz && nj == sj) closes = true;  // vertical move lands on start col
                    if (cur_horiz && ni == si) closes = true;   // horizontal move lands on start row
                } else {
                    bool cur_horiz = ((dfs_stack.size()) % 2 == 1) != first_horizontal;
                    if (!cur_horiz && nj == sj) closes = true;
                    if (cur_horiz && ni == si) closes = true;
                }
            }

            if (closes && path.size() >= 3) {
                path.push_back({ni, nj});
                found = true;
                break;
            }

            // Expand
            visited[ni][nj] = true;
            path.push_back({ni, nj});

            DFSState next;
            next.i = ni; next.j = nj;
            // Determine next direction
            bool cur_level_horiz;
            if (first_horizontal) cur_level_horiz = (dfs_stack.size() % 2 == 0);
            else cur_level_horiz = (dfs_stack.size() % 2 == 1);

            if (cur_level_horiz) {
                // Next is horizontal: same row
                for (int col : base.row_cells[ni]) {
                    if (col == nj) continue;
                    if (visited[ni][col]) continue;
                    next.neighbors.push_back({ni, col});
                }
            } else {
                // Next is vertical: same col
                for (int row : base.col_cells[nj]) {
                    if (row == ni) continue;
                    if (visited[row][nj]) continue;
                    next.neighbors.push_back({row, nj});
                }
            }

            // Also check if any neighbor closes the cycle
            next.idx = 0;
            dfs_stack.push_back(std::move(next));
        }

        if (found) return path;
    }

    return {}; // no cycle found
}

// Simplified cycle finder that matches the Python logic more closely
std::vector<std::pair<int,int>> trouver_cycle_v2(const Base& base, std::pair<int,int> depart, int n, int m) {
    int si = depart.first, sj = depart.second;

    // DFS alternating row/col
    std::vector<std::pair<int,int>> path;
    std::vector<std::vector<bool>> in_path(n, std::vector<bool>(m, false));

    std::function<bool(int, int, bool)> dfs = [&](int ci, int cj, bool next_horiz) -> bool {
        // Try to close cycle
        if (path.size() >= 4) {
            if (next_horiz && ci == si) return true;   // can go horizontal to start row -> but need start col
            if (!next_horiz && cj == sj) return true;  // can go vertical to start col
        }

        if ((int)path.size() > 2 * (n + m)) return false;

        if (next_horiz) {
            // Move horizontally: find cells in same row
            for (int col : base.row_cells[ci]) {
                if (in_path[ci][col]) continue;
                in_path[ci][col] = true;
                path.push_back({ci, col});
                if (dfs(ci, col, false)) return true;
                path.pop_back();
                in_path[ci][col] = false;
            }
        } else {
            // Move vertically: find cells in same column
            for (int row : base.col_cells[cj]) {
                if (in_path[row][cj]) continue;
                in_path[row][cj] = true;
                path.push_back({row, cj});
                if (dfs(row, cj, true)) return true;
                path.pop_back();
                in_path[row][cj] = false;
            }
        }
        return false;
    };

    // Start with horizontal move (same row as depart)
    path.push_back({si, sj});
    if (dfs(si, sj, true)) return path;

    // Try vertical first
    path.clear();
    path.push_back({si, sj});
    if (dfs(si, sj, false)) return path;

    return {};
}

void rendre_connexe(Base& base, const Matrix& couts, const Matrix& prop, int n, int m) {
    // BFS to find connected components
    std::vector<int> comp_id(n + m, -1);
    int num_comp = 0;

    for (int start = 0; start < n + m; ++start) {
        if (comp_id[start] >= 0) continue;
        // BFS
        std::queue<int> q;
        q.push(start);
        comp_id[start] = num_comp;
        while (!q.empty()) {
            int u = q.front(); q.pop();
            if (u < n) {
                for (int j : base.row_cells[u]) {
                    int v = n + j;
                    if (comp_id[v] < 0) { comp_id[v] = num_comp; q.push(v); }
                }
            } else {
                int col = u - n;
                for (int i : base.col_cells[col]) {
                    if (comp_id[i] < 0) { comp_id[i] = num_comp; q.push(i); }
                }
            }
        }
        ++num_comp;
    }

    if (num_comp <= 1) return;

    // Add cheapest edges between different components
    while (num_comp > 1) {
        int best_cost = INT_MAX, bi = -1, bj = -1;
        for (int i = 0; i < n; ++i)
            for (int j = 0; j < m; ++j) {
                if (prop(i, j) > 0) continue; // already in base
                bool already = false;
                for (int c : base.row_cells[i]) if (c == j) { already = true; break; }
                if (already) continue;
                if (comp_id[i] != comp_id[n + j] && couts(i, j) < best_cost) {
                    best_cost = couts(i, j);
                    bi = i; bj = j;
                }
            }
        if (bi < 0) break;

        base.add(bi, bj);
        // Merge components
        int old_comp = comp_id[n + bj];
        int new_comp = comp_id[bi];
        for (int k = 0; k < n + m; ++k)
            if (comp_id[k] == old_comp) comp_id[k] = new_comp;
        --num_comp;
    }
}

Matrix marche_pied_complet(const Matrix& couts, Matrix prop, int n, int m) {
    const int MAX_ITER = 10000;

    Base base(n, m);
    base.rebuild(prop);

    std::vector<int> u, v;

    for (int iter = 0; iter < MAX_ITER; ++iter) {
        // Ensure connectivity (handle degeneracy)
        if ((int)base.cells.size() < n + m - 1) {
            rendre_connexe(base, couts, prop, n, m);
        }

        // Compute potentials
        calculer_potentiels(couts, base, n, m, u, v);

        // Find most negative marginal cost
        int min_marg = 0;
        int ai = -1, aj = -1;

        // Build a fast lookup for base membership
        std::vector<std::vector<bool>> is_base(n, std::vector<bool>(m, false));
        for (auto& [i, j] : base.cells) is_base[i][j] = true;

        for (int i = 0; i < n; ++i) {
            for (int j = 0; j < m; ++j) {
                if (is_base[i][j]) continue;
                int marg = couts(i, j) - u[i] - v[j];
                if (marg < min_marg) {
                    min_marg = marg;
                    ai = i; aj = j;
                }
            }
        }

        if (ai < 0) break; // optimal

        // Find cycle
        base.add(ai, aj);
        auto cycle = trouver_cycle_v2(base, {ai, aj}, n, m);

        if (cycle.empty()) {
            // Remove the added cell and break
            base.row_cells[ai].pop_back();
            base.col_cells[aj].pop_back();
            base.cells.pop_back();
            break;
        }

        // Find delta (min of odd-indexed cells)
        int delta = INT_MAX;
        for (int k = 1; k < (int)cycle.size(); k += 2) {
            auto [ci, cj] = cycle[k];
            delta = std::min(delta, prop(ci, cj));
        }

        // Apply pivot
        for (int k = 0; k < (int)cycle.size(); ++k) {
            auto [ci, cj] = cycle[k];
            if (k % 2 == 0) prop(ci, cj) += delta;
            else prop(ci, cj) -= delta;
        }

        // Rebuild base
        base = Base(n, m);
        // Keep entering variable in base even if delta==0
        for (int i = 0; i < n; ++i)
            for (int j = 0; j < m; ++j)
                if (prop(i, j) > 0) base.add(i, j);

        // If entering cell has 0 flow (degenerate), add it
        if (prop(ai, aj) == 0) {
            bool found = false;
            for (int c : base.row_cells[ai]) if (c == aj) { found = true; break; }
            if (!found) base.add(ai, aj);
        }
    }

    return prop;
}

// ==========================================
// BENCHMARK
// ==========================================

BenchResult benchmark_nord_ouest(const Problem& p) {
    BenchResult r;

    auto t0 = std::chrono::high_resolution_clock::now();
    Matrix prop = algo_nord_ouest(p.provisions, p.commandes);
    auto t1 = std::chrono::high_resolution_clock::now();

    r.theta_init = std::chrono::duration<double>(t1 - t0).count();
    r.cost_init = calculer_cout_total(p.couts, prop);

    auto t2 = std::chrono::high_resolution_clock::now();
    Matrix opt = marche_pied_complet(p.couts, prop, p.n, p.m);
    auto t3 = std::chrono::high_resolution_clock::now();

    r.t_stepping = std::chrono::duration<double>(t3 - t2).count();
    r.cost_final = calculer_cout_total(p.couts, opt);

    return r;
}

BenchResult benchmark_balas_hammer(const Problem& p) {
    BenchResult r;

    auto t0 = std::chrono::high_resolution_clock::now();
    Matrix prop = algo_balas_hammer(p.couts, p.provisions, p.commandes);
    auto t1 = std::chrono::high_resolution_clock::now();

    r.theta_init = std::chrono::duration<double>(t1 - t0).count();
    r.cost_init = calculer_cout_total(p.couts, prop);

    auto t2 = std::chrono::high_resolution_clock::now();
    Matrix opt = marche_pied_complet(p.couts, prop, p.n, p.m);
    auto t3 = std::chrono::high_resolution_clock::now();

    r.t_stepping = std::chrono::duration<double>(t3 - t2).count();
    r.cost_final = calculer_cout_total(p.couts, opt);

    return r;
}

// ==========================================
// MAIN
// ==========================================

void run_benchmark(int n, int iterations, std::mt19937& rng, std::ofstream& csv) {
    std::cout << "n=" << n << " (" << iterations << " iterations)..." << std::flush;

    for (int iter = 0; iter < iterations; ++iter) {
        Problem p = generer_probleme_aleatoire(n, rng);

        BenchResult r_no = benchmark_nord_ouest(p);

        BenchResult r_bh;
        if (n <= 2000) {
            r_bh = benchmark_balas_hammer(p);
        } else {
            // BH too slow for very large n, measure init only
            auto t0 = std::chrono::high_resolution_clock::now();
            Matrix prop_bh = algo_balas_hammer(p.couts, p.provisions, p.commandes);
            auto t1 = std::chrono::high_resolution_clock::now();
            r_bh.theta_init = std::chrono::duration<double>(t1 - t0).count();
            r_bh.cost_init = calculer_cout_total(p.couts, prop_bh);
            r_bh.t_stepping = -1;
            r_bh.cost_final = -1;
        }

        csv << n << ","
            << iter << ","
            << r_no.theta_init << ","
            << r_no.t_stepping << ","
            << r_no.cost_init << ","
            << r_no.cost_final << ","
            << r_bh.theta_init << ","
            << r_bh.t_stepping << ","
            << r_bh.cost_init << ","
            << r_bh.cost_final << "\n";

        if ((iter + 1) % 10 == 0)
            std::cout << " " << (iter + 1) << std::flush;
    }
    std::cout << " done.\n";
}

void print_usage() {
    std::cout << "Usage: transport [mode] [options]\n"
              << "Modes:\n"
              << "  bench              Run full benchmark suite (default)\n"
              << "  bench-quick        Quick benchmark (fewer iterations)\n"
              << "  solve <file>       Solve a specific problem file\n"
              << "  single <n>         Single benchmark for size n\n";
}

void solve_file(const std::string& filename) {
    std::ifstream f(filename);
    if (!f.is_open()) {
        std::cerr << "Cannot open: " << filename << "\n";
        return;
    }

    std::vector<int> vals;
    int v;
    while (f >> v) vals.push_back(v);

    int n = vals[0], m = vals[1];
    Matrix couts(n, m);
    std::vector<int> provisions(n), commandes(m);

    int idx = 2;
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < m; ++j)
            couts(i, j) = vals[idx++];
        provisions[i] = vals[idx++];
    }
    for (int j = 0; j < m; ++j)
        commandes[j] = vals[idx++];

    std::cout << "Problem: " << n << "x" << m << "\n";

    Matrix prop_no = algo_nord_ouest(provisions, commandes);
    long long cost_no = calculer_cout_total(couts, prop_no);
    std::cout << "Nord-Ouest initial cost: " << cost_no << "\n";

    Matrix opt_no = marche_pied_complet(couts, prop_no, n, m);
    std::cout << "Nord-Ouest optimal cost: " << calculer_cout_total(couts, opt_no) << "\n";

    Matrix prop_bh = algo_balas_hammer(couts, provisions, commandes);
    long long cost_bh = calculer_cout_total(couts, prop_bh);
    std::cout << "Balas-Hammer initial cost: " << cost_bh << "\n";

    Matrix opt_bh = marche_pied_complet(couts, prop_bh, n, m);
    std::cout << "Balas-Hammer optimal cost: " << calculer_cout_total(couts, opt_bh) << "\n";
}

int main(int argc, char* argv[]) {
    std::string mode = "bench";
    if (argc > 1) mode = argv[1];

    if (mode == "--help" || mode == "-h") {
        print_usage();
        return 0;
    }

    if (mode == "solve") {
        if (argc < 3) { std::cerr << "Specify a file.\n"; return 1; }
        solve_file(argv[2]);
        return 0;
    }

    // Benchmark mode
    std::vector<int> tailles;
    int iterations;

    if (mode == "bench-quick") {
        tailles = {10, 40, 100, 400};
        iterations = 20;
    } else if (mode == "single" && argc > 2) {
        tailles = {std::stoi(argv[2])};
        iterations = (argc > 3) ? std::stoi(argv[3]) : 10;
    } else {
        tailles = {10, 40, 100, 400, 1000, 2000};
        iterations = 50;
    }

    std::mt19937 rng(42);

    std::string csv_path = "benchmark_cpp.csv";
    const char* out_dir = std::getenv("BENCH_OUTPUT_DIR");
    if (out_dir) csv_path = std::string(out_dir) + "/benchmark_cpp.csv";
    std::ofstream csv(csv_path);
    csv << "n,iter,theta_no,t_stepping_no,cost_init_no,cost_final_no,"
        << "theta_bh,t_stepping_bh,cost_init_bh,cost_final_bh\n";

    std::cout << "=== C++ Transport Problem Benchmark ===\n";
    std::cout << "Sizes: ";
    for (int n : tailles) std::cout << n << " ";
    std::cout << "\nIterations per size: " << iterations << "\n\n";

    for (int n : tailles) {
        run_benchmark(n, iterations, rng, csv);
    }

    csv.close();
    std::cout << "\nResults saved to benchmark_cpp.csv\n";
    return 0;
}
