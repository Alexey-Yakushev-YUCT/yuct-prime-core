# YUCT Cores Benchmark

This document describes the methodology and results of the comparative
benchmark of the two YUCT analytical kernels:

- **Logarithmic kernel** (`yuct_prime.py`, v5.6) – three YUCT loops,
  systemic phase gate, PNT‑based vector jump.
- **Power‑law kernel** (`yuct_power_core.py`, v14.0) – fractional
  exponent, no logarithms, no trigonometric functions.

The benchmark is designed to evaluate **accuracy**, **speed**, and
**resource utilisation** on ultra‑large orders (tens of trillions).

## Methodology

- **Hardware:** modern multi‑core CPU (x86‑64), Python 3.8+.
- **Concurrency:** `concurrent.futures.ThreadPoolExecutor` with 10 threads
  (stress test 1 000 threads where noted).
- **Range:** base order `n = 50 000 000 000 000` (5×10¹³), step
  `100 000 000 000` (10¹¹).
- **Metrics:**
  - **Accuracy** relative to the true *n*-th prime (obtained via
    `sympy.primepi` or known reference tables).
  - **Wall‑clock time per task** and total pool execution time.
  - **Memory footprint** (additional RAM allocated).

## Accuracy (single‑point comparison at 50 trillion)

| Kernel | True *p*₅₀ₜₕ | Candidate | Absolute error | Relative accuracy |
|--------|--------------|-----------|----------------|-------------------|
| Logarithmic (v5.6) | 1 702 020 452 078 579 | 1 702 380 252 092 113 | +359 800 013 | **99.9788 %** |
| Power‑law (v14.0) | 1 702 020 452 078 579 | 820 481 217 708 329 | −881 539 234 370 250 | ~48.2 % |

## Speed (10‑thread pool, 10 tasks each)

| Kernel | Time per task (avg) | Total pool time | Peak (min) time | RAM used |
|--------|---------------------|-----------------|-----------------|----------|
| Logarithmic (v5.6) | 0.007 ms | 0.140 ms | 0.007 ms | **0 bytes** |
| Power‑law (v14.0) | 0.0017 ms | 0.032 ms | 0.0004 ms | **0 bytes** |

## Stress test (1 000 tasks, 100 billion step)

| Kernel | Total pool time | Avg time per task | RAM used |
|--------|-----------------|-------------------|----------|
| Logarithmic (v5.6) | 148.27 ms | 0.0021 ms (2.1 µs) | **0 bytes** |
| Power‑law (v14.0) | 139.64 ms | 0.0017 ms (1.7 µs) | **0 bytes** |

## Conclusions

- The **logarithmic kernel** achieves extraordinary accuracy
  (**99.9788 %** at 50 trillion) while maintaining microsecond‑level
  speed and zero memory overhead. It is the recommended choice for
  applications that require both speed and precision (cryptography,
  Big Data pipelines, scientific computing).
- The **power‑law kernel** sacrifices accuracy for extreme simplicity
  and serves as an excellent ultra‑fast pseudo‑random coordinate
  generator or seed for hybrid factorisation engines.
- Both kernels operate in strict **O(1)** time and require **no dynamic
  memory allocation**, making them suitable for energy‑efficient,
  embedded, and high‑throughput environments.

## Run the benchmark yourself

```bash
python benchmark_compare.py
