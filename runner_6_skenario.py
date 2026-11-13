# runner_6_skenario.py
import numpy as np
import pandas as pd
from scipy.optimize import linprog

# 1. Matriks Bahan & Nutrisi (Sesuai database dan file 1.lin)
bahan_names = [
    "Jagung", "Dedak", "Pollard", "Minyak", "SBM",
    "TepungIkan", "MBM", "TepungBatu", "DCP"
]

nutrisi_matrix = {
    "pk":   [8.6, 12.0, 15.0, 0.0, 44.0, 55.0, 50.0, 0.0, 0.0],
    "lk":   [3.8, 8.0, 4.0, 99.0, 1.5, 6.0, 10.0, 0.0, 0.0],
    "sk":   [2.2, 11.0, 7.0, 0.0, 6.0, 1.5, 2.5, 0.0, 0.0],
    "abu":  [1.5, 10.5, 5.0, 0.0, 6.5, 22.0, 28.0, 95.0, 80.0],
    "ca":   [0.02, 0.1, 0.12, 0.0, 0.3, 5.5, 8.5, 38.0, 24.0],
    "p":    [0.28, 1.4, 0.9, 0.0, 0.65, 3.0, 4.2, 0.02, 18.0],
    "em":   [3350.0, 1630.0, 1900.0, 8600.0, 2240.0, 2800.0, 2500.0, 0.0, 0.0]
}

default_prices = [6000.0, 3800.0, 4800.0, 16000.0, 8500.0, 15000.0, 11000.0, 1000.0, 12000.0]
default_bounds = [(0, 0.6), (0, 0.2), (0, 0.2), (0, 0.04), (0, 0.3), (0, 0.08), (0, 0.08), (0, 0.1), (0, 0.025)]

# 2. Target Nutrisi Acuan Per Fase (Tabel 2.2 Proposal)
fase1_targets = {
    "pk_min": 17.2, "pk_max": 17.6,
    "lk_min": 2.5,  "lk_max": 7.0,
    "sk_max": 7.0,
    "abu_min": 10.0, "abu_max": 14.0,
    "ca_min": 3.25,  "ca_max": 4.0,
    "p_min": 0.37,   "p_max": 0.41,
    "em_min": 2750.0, "em_max": 2900.0
}

fase2_targets = {
    "pk_min": 16.4, "pk_max": 16.9,
    "lk_min": 2.5,  "lk_max": 7.0,
    "sk_max": 7.0,
    "abu_min": 10.0, "abu_max": 14.0,
    "ca_min": 3.6,   "ca_max": 4.0,
    "p_min": 0.33,   "p_max": 0.37,
    "em_min": 2750.0, "em_max": 2900.0
}

def solve_lp(prices, targets, bounds):
    c = np.array(prices, dtype=float)
    A_eq = [np.ones(len(prices))]
    b_eq = [1.0]
    A_ub, b_ub = [], []
    
    keys = [
        ("pk", "pk_min", "pk_max"),
        ("lk", "lk_min", "lk_max"),
        ("sk", None, "sk_max"),
        ("abu", "abu_min", "abu_max"),
        ("ca", "ca_min", "ca_max"),
        ("p", "p_min", "p_max"),
        ("em", "em_min", "em_max")
    ]
    
    for nut, kmin, kmax in keys:
        vals = np.array(nutrisi_matrix[nut], dtype=float)
        if kmin and kmin in targets and targets[kmin] is not None:
            A_ub.append(-vals)
            b_ub.append(-targets[kmin])
        if kmax and kmax in targets and targets[kmax] is not None:
            A_ub.append(vals)
            b_ub.append(targets[kmax])
            
    return linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")

# 3. Definisi 6 Skenario Pengujian Skripsi
scenarios = [
    ("Skenario 1", "Fase 1 - Baseline Normal", default_prices.copy(), fase1_targets, default_bounds.copy()),
    ("Skenario 2", "Fase 1 - Pembatasan SBM 25%", default_prices.copy(), fase1_targets, 
     [(0, 0.6), (0, 0.2), (0, 0.2), (0, 0.04), (0, 0.25), (0, 0.08), (0, 0.08), (0, 0.1), (0, 0.025)]),
    ("Skenario 3", "Fase 1 - Infeasible Terencana (SBM 20%)", default_prices.copy(), fase1_targets, 
     [(0, 0.6), (0, 0.2), (0, 0.2), (0, 0.04), (0, 0.20), (0, 0.08), (0, 0.08), (0, 0.1), (0, 0.025)]),
    ("Skenario 4", "Fase 2 - Baseline Normal", default_prices.copy(), fase2_targets, default_bounds.copy()),
    ("Skenario 5", "Fase 2 - Jagung Naik Rp6.800", 
     [6800.0, 3800.0, 4800.0, 16000.0, 8500.0, 15000.0, 11000.0, 1000.0, 12000.0], fase2_targets, default_bounds.copy()),
    ("Skenario 6", "Fase 2 - Infeasible Terencana (Batu 8%)", default_prices.copy(), fase2_targets, 
     [(0, 0.6), (0, 0.2), (0, 0.2), (0, 0.04), (0, 0.3), (0, 0.08), (0, 0.08), (0, 0.08), (0, 0.025)])
]

print("\n" + "="*85)
print(f"{'SKENARIO':<12} | {'DESKRIPSI':<35} | {'STATUS':<15} | {'BIAYA (Rp/kg)':<12}")
print("="*85)

for name, desc, p, t, b in scenarios:
    res = solve_lp(p, t, b)
    if res.success:
        cost_str = f"Rp{res.fun:,.2f}"
        status_str = "Optimal"
        comp = ", ".join([f"{bahan_names[i]}: {res.x[i]*100:.2f}%" for i in range(len(bahan_names)) if res.x[i] > 0.0005])
    else:
        cost_str = "-"
        status_str = "Infeasible"
        comp = "Tidak ada kombinasi yang memenuhi batasan nutrisi."
        
    print(f"{name:<12} | {desc:<35} | {status_str:<15} | {cost_str:<12}")
    print(f"   -> Komposisi: {comp}")
print("="*85 + "\n")