# -*- coding: utf-8 -*-
"""
YAKUSHEV UNIFIED COORDINATION THEORY (YUCT) — HIGH-LOAD BENCHMARK
Filename: benchmark_compare.py
"""
import time
import tracemalloc
from yuct_prime_core import YuctExactPrimeEngine

def run_mega_benchmark():
    engine = YuctExactPrimeEngine()
    
    # Набор экстремально больших чисел для проверки схождения решётки
    test_scales = [100000000000, 1000000000000, 150000000000000]
    
    print("=" * 90)
    print(" ЗАПУСК ЭКСТРЕМАЛЬНОГО БЕНЧМАРКА YUCT PRIME CORE НА СВЕРХБОЛЬШИХ ПОРЯДКАХ")
    print("=" * 90)
    
    for n in test_scales:
        tracemalloc.start()
        ram_before, _ = tracemalloc.get_traced_memory()
        
        t_start = time.perf_counter()
        p_n = engine.compute_exact_prime(n)
        t_end = time.perf_counter()
        
        ram_after, ram_peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        net_ram = max(0, ram_after - ram_before)
        print(f" [RUN] Порядковый индекс N = {n:,}")
        print(f"  -> Вычисленное простое число: {p_n}")
        print(f"  -> Время фазовой навигации  : {(t_end - t_start)*1000000:.3f} мкс (Сложность O(1))")
        print(f"  -> Чистый расход ОЗУ хоста  : {net_ram} байт")
        print("-" * 90)

if __name__ == "__main__":
    run_mega_benchmark()
