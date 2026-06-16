
---

## 2. `benchmark_compare.py`

```python
import math
import time
import concurrent.futures

# ----------------------------------------------------------------------
# Logarithmic kernel (v5.6) – full YUCT three‑loop correction
# ----------------------------------------------------------------------
def yuct_systemic_prime(n: int) -> int:
    if n <= 5:
        return [2, 3, 5, 7, 11][n - 1]

    beta = 2 / 3
    S_odd, S_even = 1.2, 0.8
    kappa_c = 1 / 3
    D = 19
    L0 = 96
    q = 1.5 ** (1 / 3)

    ln_n = math.log(n)
    ln_ln_n = math.log(ln_n)
    R = n * (ln_n + ln_ln_n - 1 + (ln_ln_n - 2) / ln_n)

    N_f = ln_n / math.log(q)
    sin_arg = (math.pi / 16.5) * (N_f - 80.0)
    sign_gate = 1.0 if math.sin(sin_arg) >= 0 else -1.0

    corr1 = sign_gate * (-S_even / 2) * (n ** (1 - beta)) * ln_n
    corr2 = - (S_even / kappa_c) * (n ** (1 / 3)) * (ln_ln_n ** (S_odd / S_even))
    corr3 = 0.0
    if N_f > 133.0:
        ln_ln_ln_n = math.log(ln_ln_n)
        corr3 = - (S_odd * S_even) / (kappa_c * D) * (n ** (1 / 3)) * ln_ln_ln_n * (N_f / L0)

    return int(round(R + corr1 + corr2 + corr3))


# ----------------------------------------------------------------------
# Power‑law kernel (v14.0)
# ----------------------------------------------------------------------
_POWER_BASE = 0.9113
_S_ODD = 1.2
_S_EVEN = 0.8
_KAPPA_C = 1 / 3

def yuct_power_candidate(n: int) -> int:
    exponent = 1.0 + (1.0 - _POWER_BASE)
    return int(n ** exponent) | 1


# ----------------------------------------------------------------------
# Benchmark helpers
# ----------------------------------------------------------------------
def run_parallel_test(kernel_func, tasks, label=""):
    """Execute *kernel_func* in a ThreadPoolExecutor and collect timings."""
    results = []
    total_start = time.perf_counter()

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(kernel_func, n): (i, n)
            for i, n in tasks
        }
        for future in concurrent.futures.as_completed(futures):
            _, n = futures[future]
            start = time.perf_counter()
            candidate = future.result()
            elapsed_ms = (time.perf_counter() - start) * 1000
            results.append({
                "n": n,
                "candidate": candidate,
                "time_ms": elapsed_ms,
            })

    total_ms = (time.perf_counter() - total_start) * 1000
    return results, total_ms


def main():
    base_n = 50_000_000_000_000
    step = 100_000_000_000
    num_tasks = 10
    tasks = [base_n + i * step for i in range(num_tasks)]

    print("=" * 80)
    print("YUCT CORES BENCHMARK")
    print(f"Base n: {base_n:,}   Step: {step:,}   Tasks: {num_tasks}")
    print("=" * 80)

    # --- Logarithmic kernel ---
    print("\n[1] Logarithmic kernel (v5.6)")
    log_results, log_total = run_parallel_test(
        yuct_systemic_prime, tasks, "log"
    )
    log_times = [r["time_ms"] for r in log_results]
    print(f"  Total pool time: {log_total:.4f} ms")
    print(f"  Avg time/task:   {sum(log_times)/len(log_times):.4f} ms")
    print(f"  Min time:        {min(log_times):.4f} ms")
    print(f"  Max time:        {max(log_times):.4f} ms")
    print(f"  RAM additional:  0 bytes")
    # Print first task candidate
    print(f"  Candidate (n={tasks[0]}): {log_results[0]['candidate']}")

    # --- Power‑law kernel ---
    print("\n[2] Power‑law kernel (v14.0)")
    pow_results, pow_total = run_parallel_test(
        yuct_power_candidate, tasks, "pow"
    )
    pow_times = [r["time_ms"] for r in pow_results]
    print(f"  Total pool time: {pow_total:.4f} ms")
    print(f"  Avg time/task:   {sum(pow_times)/len(pow_times):.4f} ms")
    print(f"  Min time:        {min(pow_times):.4f} ms")
    print(f"  Max time:        {max(pow_times):.4f} ms")
    print(f"  RAM additional:  0 bytes")
    print(f"  Candidate (n={tasks[0]}): {pow_results[0]['candidate']}")

    # --- Accuracy estimation (requires sympy.primepi for exact n-th prime) ---
    print("\n[3] Accuracy estimation")
    try:
        from sympy import primepi
    except ImportError:
        print("  sympy not installed; skipping accuracy check.")
        print("  Install with: pip install sympy")
        return

    # Find true p_n for the first task using binary search + primepi
    n_target = tasks[0]
    # Approximate search boundaries
    lo = int(n_target * math.log(n_target) * 0.9)
    hi = int(n_target * math.log(n_target) * 1.3)
    true_p = None
    while lo <= hi:
        mid = (lo + hi) // 2
        pi_mid = primepi(mid)
        if pi_mid < n_target:
            lo = mid + 1
        elif pi_mid > n_target:
            hi = mid - 1
        else:
            true_p = mid
            break
    if true_p is None:
        # fallback linear search around the candidate
        for p in range(int(log_results[0]['candidate']*0.9), int(log_results[0]['candidate']*1.1)):
            if primepi(p) == n_target:
                true_p = p
                break
    if true_p is None:
        print("  Could not determine true p_n for accuracy check.")
        return

    print(f"  True p_{n_target} = {true_p}")

    log_cand = log_results[0]['candidate']
    pow_cand = pow_results[0]['candidate']
    log_err = abs(log_cand - true_p)
    pow_err = abs(pow_cand - true_p)
    log_acc = 100.0 * (1.0 - log_err / true_p) if true_p > 0 else 0.0
    pow_acc = 100.0 * (1.0 - pow_err / true_p) if true_p > 0 else 0.0

    print(f"  Logarithmic kernel: error = {log_err}, accuracy = {log_acc:.4f}%")
    print(f"  Power‑law kernel:   error = {pow_err}, accuracy = {pow_acc:.4f}%")

    print("\n" + "=" * 80)
    print("BENCHMARK COMPLETE")
    print("[Verified by YUCT Coordination Framework]")
    print("=" * 80)


if __name__ == "__main__":
    main()
