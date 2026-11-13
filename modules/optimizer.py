import time
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from scipy.optimize import linprog


def hitung_formulasi_pakan(
    df_bahan: pd.DataFrame,
    target_nutrisi: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Menghitung formulasi pakan berbiaya minimum (Least-Cost Feed Formulation) untuk ayam petelur
    menggunakan Linear Programming scipy.optimize.linprog(method='highs').

    Args:
        df_bahan: DataFrame bahan baku (kolom wajib: nama_bahan, pk, lk, sk, abu, ca, p, em, harga_per_kg, batas_maks_layer)
        target_nutrisi: Dictionary standar kebutuhan nutrisi acuan

    Returns:
        Dictionary hasil optimasi:
        - success: bool
        - status_message: str
        - total_biaya_per_kg: float
        - total_biaya_per_sak: float (50 kg)
        - execution_time_ms: float
        - komposisi: List[Dict]
        - capaian_nutrisi: List[Dict]
        - diagnosa: Optional[str]
    """
    start_time = time.time()

    # 1. Validasi Kolom Wajib
    required_cols = ["nama_bahan", "pk", "lk", "sk", "abu", "ca", "p", "em", "harga_per_kg", "batas_maks_layer"]
    for col in required_cols:
        if col not in df_bahan.columns:
            return {
                "success": False,
                "status_message": f"Kolom wajib '{col}' tidak ditemukan pada tabel bahan baku.",
                "execution_time_ms": 0.0,
                "komposisi": [],
                "capaian_nutrisi": [],
                "diagnosa": f"Format data bahan baku tidak lengkap. Kolom {col} hilang."
            }

    # 2. Validasi Jumlah Bahan Terpilih
    n_bahan = len(df_bahan)
    if n_bahan < 2:
        return {
            "success": False,
            "status_message": "Bahan baku aktif minimal 2 jenis.",
            "execution_time_ms": 0.0,
            "komposisi": [],
            "capaian_nutrisi": [],
            "diagnosa": "Pilih minimal 2 jenis bahan baku yang dicentang aktif untuk membuat formulasi campuran pakan."
        }

    # 3. Validasi Nilai Non-Negatif (Skenario Black Box Testing)
    numeric_cols = ["pk", "lk", "sk", "abu", "ca", "p", "em", "harga_per_kg", "batas_maks_layer"]
    for col in numeric_cols:
        if (df_bahan[col].astype(float) < 0).any():
            return {
                "success": False,
                "status_message": f"Terdapat nilai negatif pada kolom '{col}'.",
                "execution_time_ms": 0.0,
                "komposisi": [],
                "capaian_nutrisi": [],
                "diagnosa": f"Data '{col}' tidak boleh bernilai negatif. Mohon periksa kembali input Anda."
            }

    # 4. Validasi Kapasitas Batas Maksimal (Total batas maks harus >= 100%)
    total_batas_maks = df_bahan["batas_maks_layer"].astype(float).sum()
    if total_batas_maks < 100.0:
        return {
            "success": False,
            "status_message": "Infeasible: Total batas maksimal bahan kurang dari 100%.",
            "execution_time_ms": 0.0,
            "komposisi": [],
            "capaian_nutrisi": [],
            "diagnosa": f"Total batas maksimal dari bahan yang dipilih hanya {total_batas_maks:.1f}%. Tidak mungkin mencapai total ransum 100%. Tambahkan bahan baku lain atau naikkan batas maksimal penggunaan bahan."
        }

    # 5. Koefisien Fungsi Tujuan (c): Minimalkan total biaya per kg
    c = df_bahan["harga_per_kg"].astype(float).values

    # 6. Batas Variabel (Bounds): 0 <= x_j <= batas_maks_layer / 100
    bounds = []
    for _, row in df_bahan.iterrows():
        b_min = float(row.get("batas_min_layer", 0.0)) / 100.0
        b_max = float(row.get("batas_maks_layer", 100.0)) / 100.0
        b_min = max(0.0, b_min)
        b_max = min(1.0, max(b_min, b_max))
        bounds.append((b_min, b_max))

    # 7. Kendala Kesetaraan (Equality): sum(x_j) = 1.0 (proporsi total 100%)
    A_eq = [np.ones(n_bahan)]
    b_eq = [1.0]

    # 8. Kendala Pertidaksamaan Nutrisi (Inequality): A_ub * x <= b_ub
    A_ub_list = []
    b_ub_list = []

    nutrisi_keys = [
        ("pk", "pk_min", "pk_max"),
        ("lk", "lk_min", "lk_max"),
        ("sk", "sk_min", "sk_max"),
        ("abu", "abu_min", "abu_max"),
        ("ca", "ca_min", "ca_max"),
        ("p", "p_min", "p_max"),
        ("em", "em_min", "em_max"),
    ]

    for nutrisi_col, key_min, key_max in nutrisi_keys:
        coeffs = df_bahan[nutrisi_col].astype(float).values
        val_min = target_nutrisi.get(key_min)
        val_max = target_nutrisi.get(key_max)

        # Kendala minimum: -coeffs * x <= -val_min
        if val_min is not None and not pd.isna(val_min) and float(val_min) > 0:
            A_ub_list.append(-coeffs)
            b_ub_list.append(-float(val_min))

        # Kendala maksimum: coeffs * x <= val_max
        if val_max is not None and not pd.isna(val_max) and float(val_max) > 0:
            A_ub_list.append(coeffs)
            b_ub_list.append(float(val_max))

    A_ub = np.array(A_ub_list) if A_ub_list else None
    b_ub = np.array(b_ub_list) if b_ub_list else None

    # 9. Eksekusi Solver SciPy HiGHS
    try:
        res = linprog(
            c=c,
            A_ub=A_ub,
            b_ub=b_ub,
            A_eq=A_eq,
            b_eq=b_eq,
            bounds=bounds,
            method="highs"
        )
    except Exception as e:
        return {
            "success": False,
            "status_message": f"Kesalahan saat menjalankan solver SciPy: {str(e)}",
            "execution_time_ms": 0.0,
            "komposisi": [],
            "capaian_nutrisi": [],
            "diagnosa": "Terjadi galat komputasi solver. Periksa kembali angka parameter input."
        }

    exec_time_ms = round((time.time() - start_time) * 1000, 2)

    # 10. Penanganan Hasil Infeasible / Unbounded
    if not res.success:
        diagnosa = "Kombinasi nutrisi target tidak tercapai (Infeasible). Saran penyesuaian:\n"
        diagnosa += "1. Tambahkan variasi bahan baku aktif (misalnya sumber protein nabati/hewani atau sumber energi).\n"
        diagnosa += "2. Pastikan bahan sumber kalsium (Tepung Batu/DCP) diaktifkan dengan batas maksimal mencukupi (minimal 8-10%).\n"
        diagnosa += "3. Longgarkan batas maksimal penggunaan pada bahan utama seperti Jagung Kuning atau Bungkil Kedelai."
        return {
            "success": False,
            "status_message": f"Infeasible: {res.message}",
            "execution_time_ms": exec_time_ms,
            "diagnosa": diagnosa,
            "komposisi": [],
            "capaian_nutrisi": []
        }

    # 11. Susun Hasil Solusi Optimal
    x_opt = res.x
    total_biaya = float(res.fun)

    komposisi = []
    for idx, (_, row) in enumerate(df_bahan.iterrows()):
        proporsi = float(x_opt[idx])
        persentase = proporsi * 100.0
        bobot_100kg = proporsi * 100.0
        harga = float(row["harga_per_kg"])
        biaya = proporsi * harga

        komposisi.append({
            "id": int(row.get("id", idx + 1)),
            "kode_bahan": str(row.get("kode_bahan", f"B{idx+1}")),
            "nama_bahan": str(row["nama_bahan"]),
            "kategori": str(row.get("kategori", "-")),
            "proporsi_desimal": round(proporsi, 6),
            "persentase": round(persentase, 2),
            "bobot_sak_50kg": round(proporsi * 50.0, 2),
            "bobot_kg_per_100kg": round(bobot_100kg, 2),
            "harga_per_kg": round(harga, 2),
            "kontribusi_biaya": round(biaya, 2),
            "batas_maks": float(row.get("batas_maks_layer", 100.0))
        })

    # Evaluasi Capaian Nutrisi
    capaian_nutrisi = []
    nutrisi_labels = [
        ("pk", "Protein Kasar (PK)", "%", "pk_min", "pk_max"),
        ("lk", "Lemak Kasar (LK)", "%", "lk_min", "lk_max"),
        ("sk", "Serat Kasar (SK)", "%", "sk_min", "sk_max"),
        ("abu", "Abu", "%", "abu_min", "abu_max"),
        ("ca", "Kalsium (Ca)", "%", "ca_min", "ca_max"),
        ("p", "Fosfor Tersedia (P)", "%", "p_min", "p_max"),
        ("em", "Energi Metabolis (EM)", "Kkal/kg", "em_min", "em_max"),
    ]

    for col, label, satuan, k_min, k_max in nutrisi_labels:
        nilai_aktual = float(np.sum(df_bahan[col].astype(float).values * x_opt))
        t_min = target_nutrisi.get(k_min)
        t_max = target_nutrisi.get(k_max)

        t_min_val = float(t_min) if t_min is not None and not pd.isna(t_min) else None
        t_max_val = float(t_max) if t_max is not None and not pd.isna(t_max) else None

        status = "Sesuai"
        tol = 1e-4
        if t_min_val is not None and nilai_aktual < (t_min_val - tol):
            status = "Kurang"
        elif t_max_val is not None and nilai_aktual > (t_max_val + tol):
            status = "Melebihi"

        capaian_nutrisi.append({
            "nutrisi": label,
            "satuan": satuan,
            "target_min": t_min_val if t_min_val is not None else "-",
            "target_max": t_max_val if t_max_val is not None else "-",
            "nilai_capaian": round(nilai_aktual, 2),
            "status": status
        })

    return {
        "success": True,
        "status_message": "Optimal Solution Found (HiGHS)",
        "total_biaya_per_kg": round(total_biaya, 2),
        "total_biaya_per_sak": round(total_biaya * 50.0, 2),
        "execution_time_ms": exec_time_ms,
        "komposisi": komposisi,
        "capaian_nutrisi": capaian_nutrisi,
        "diagnosa": None
    }
