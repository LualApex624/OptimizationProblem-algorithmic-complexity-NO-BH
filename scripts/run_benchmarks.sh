#!/bin/bash
# Run the full benchmark suite: compile C++, run C++ and Python benchmarks,
# then generate comparative graphs.
# Usage: ./scripts/run_benchmarks.sh [--quick]

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

MODE=${1:-"bench"}

echo "============================================"
echo " BENCHMARK COMPARATIF C++ vs Python"
echo " Transportation Problem"
echo "============================================"
echo ""

# 1. Compile C++
echo "[1/4] Compiling C++ (with -O3 -march=native)..."
cd "$ROOT_DIR/src/cpp"
make clean && make
cd "$ROOT_DIR"
echo ""

# 2. Run C++ benchmark
echo "[2/4] Running C++ benchmark..."
export BENCH_OUTPUT_DIR="$ROOT_DIR/benchmarks"
if [ "$MODE" = "--quick" ]; then
    "$ROOT_DIR/src/cpp/transport" bench-quick
else
    "$ROOT_DIR/src/cpp/transport" bench
fi
echo ""

# 3. Run Python benchmark
echo "[3/4] Running Python benchmark..."
if [ "$MODE" = "--quick" ]; then
    python3 "$ROOT_DIR/benchmarks/benchmark_python.py" --quick
else
    python3 "$ROOT_DIR/benchmarks/benchmark_python.py"
fi
echo ""

# 4. Generate comparative graphs
echo "[4/4] Generating comparative graphs..."
python3 "$ROOT_DIR/benchmarks/analyse_comparative.py"
echo ""

echo "============================================"
echo " Benchmarks complete!"
echo " Generated files:"
echo "   - benchmarks/benchmark_cpp.csv"
echo "   - benchmarks/benchmark_python.csv"
echo "   - results/figures/comparaison_*.png"
echo "============================================"
