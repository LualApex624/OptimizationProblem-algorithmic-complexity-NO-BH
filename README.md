# Transportation Problem — Comparative Optimization Study

**Author:** YAO Paul-Alex |EFREI Paris — Operations Research

## Overview

Comparative study of two initialization algorithms (Nord-Ouest and Balas-Hammer) combined with the Stepping Stone optimization method for solving the transportation problem. Implemented in both **Python** and **C++** to analyze algorithmic complexity and cross-language performance.

## Project Structure

```
.
├── src/                        # Source code
│   ├── python/
│   │   ├── algorithmes.py      # Core algorithms (NO, BH, Stepping Stone)
│   │   ├── main.py             # Interactive solver with trace logging
│   │   └── complexite.py       # Standalone complexity study
│   └── cpp/
│       ├── transport.cpp       # Full C++ implementation
│       └── Makefile            # Build with -O3 -march=native
│
├── benchmarks/                 # Benchmark tooling and data
│   ├── benchmark_python.py     # Python benchmark runner
│   ├── analyse_comparative.py  # Graph generation (C++ vs Python)
│   ├── benchmark_python.csv    # Raw Python benchmark data
│   └── benchmark_cpp.csv       # Raw C++ benchmark data
│
├── data/
│   └── problems/               # 12 reference problem input files
│       ├── probleme1.txt
│       └── ...
│
├── results/
│   ├── traces/                 # Execution traces (12 problems x 2 methods)
│   └── figures/                # Generated comparison graphs (PNG)
│
├── report/
│   ├── rapport_final.tex       # LaTeX report (compile with pdflatex)
│   └── rapport_final.docx      # Google Docs compatible report
│
├── scripts/
│   └── run_benchmarks.sh       # Full benchmark pipeline (compile + run + graphs)
│
└── README.md
```

## Quick Start

### Solve a specific problem (interactive)

```bash
cd src/python
python3 main.py
```

### Run the full benchmark suite

```bash
chmod +x scripts/run_benchmarks.sh
./scripts/run_benchmarks.sh          # full run
./scripts/run_benchmarks.sh --quick  # quick run (fewer sizes/iterations)
```

### Compile C++ only

```bash
cd src/cpp
make
./transport solve ../../data/problems/probleme1.txt
```

### Generate comparative graphs only

```bash
python3 benchmarks/analyse_comparative.py
```

## Algorithms

| Algorithm | Phase | Complexity | Description |
|-----------|-------|------------|-------------|
| Nord-Ouest | Initialization | O(n) | North-West Corner — fast, naive |
| Balas-Hammer | Initialization | O(n³) | Vogel's Approximation — smarter, costlier |
| Stepping Stone | Optimization | O(n²)–O(n³) | Iterative pivot to reach optimality |

## Key Results

| n | C++ Speedup (θ_NO) | C++ Speedup (θ_BH) | C++ Speedup (t_NO) |
|---|---------------------|---------------------|---------------------|
| 10 | 26x | 34x | 15x |
| 40 | 37x | 72x | 40x |
| 100 | 37x | 95x | 43x |
| 400 | 39x | 111x | 10x |

## Requirements

- **Python 3.8+** with `numpy` and `matplotlib`
- **C++17** compiler (g++ or clang++)
- **Make** for C++ build
