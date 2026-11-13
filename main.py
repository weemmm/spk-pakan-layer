import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import linprog
import io
import datetime

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(page_title="SPK Formulasi Pakan", layout="wide", page_icon="🐔")
st.title("🐔 Sistem Cerdas Formulasi Pakan Unggas (Smart-Feed)")
st.markdown("Optimalisasi Biaya dan Nutrisi Berbasis Algoritma *Linear Programming*")
st.divider()

# ==========================================
# 2. SIDEBAR: TARGET PRODUKSI
# ==========================================
st.sidebar.header("⚙️ Skala Produksi")
total_produksi = st.sidebar.number_input("Target Produksi Pakan (Kg):", min_value=1.0, value=1000.0, step=100.0)

st.subheader("🐣 1. Pilih Fase Pertumbuhan Ayam")
fase_ayam = st.selectbox(
    "Pilih fase untuk memuat standar nutrisi dan batas penggunaan bahan otomatis:",
    ("Starter (Awal)", "Grower (Pertumbuhan)", "Layer (Bertelur)"),
    index=2
)

# Standar Nutrisi
if "Starter" in fase_ayam:
    fase_key = 'Starter'
    target_default = [18.0, 2800.0, 0.9, 0.45, 5.0]
    target_max = [100.0, 4000.0, 1.1, 0.50, 5.0]
elif "Grower" in fase_ayam:
    fase_key = 'Grower'
    target_default = [15.0, 2700.0, 1.0, 0.35, 6.0]
    target_max = [100.0, 4000.0, 1.2, 0.40, 6.0]
else:
    fase_key = 'Layer'
    target_default = [16.4, 2750.0, 3.6, 0.33, 0.0] 
    target_max = [100.0, 4000.0, 4.0, 0.37, 7.0] 

# ==========================================
# 4. TABEL 1: MANAJEMEN BAHAN BAKU (UPDATE: ADA BATAS MINIMAL)
# ==========================================
st.divider()
st.subheader("📋 2. Manajemen Bahan Baku & Kandungan Nutrisi") 
st.caption("Jika Anda ingin MEMAKSA sistem menggunakan suatu bahan, ubah angka di kolom 'Batas Minimal' menjadi lebih dari 0.")

data_bahan = {
    'Bahan Pakan': ['Jagung', 'Dedak', 'Pollard', 'Minyak Sawit', 'Bungkil Kedelai', 'Tepung Ikan', 'MBM', 'Tepung Batu', 'DCP'],
    'Harga (Rp/Kg)': [3200, 1800, 2300, 10000, 6000, 7500, 7000, 800, 4000],
    'PK (%)': [8.0, 11.32, 12.68, 0.0, 46.5, 55.0, 43.0, 0.0, 0.0],
    'EM (Kkal)': [3300, 3100, 1300, 8700, 2550, 2830, 2375, 0, 0],
    'Ca (%)': [0.02, 0.07, 0.14, 0.0, 0.25, 7.19, 9.78, 38.0, 22.72],
    'P (%)': [0.28, 1.50, 1.15, 0.0, 0.63, 2.88, 4.50, 0.0, 17.68],
    'SK (%)': [2.2, 8.0, 15.0, 0.0, 5.6, 0.7, 2.46, 0.0, 0.0],
    # FITUR BARU: Batas Minimal (Default: 0.5% agar semua bahan masuk)
    'Batas Minimal (%)': [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5], 
    'Max_Starter (%)': [60, 10, 5, 5, 30, 7, 7, 5, 1], 
    'Max_Grower (%)': [60, 15, 15, 6, 30, 8, 7, 10, 2],
    'Max_Layer (%)': [70, 30, 30, 7, 40, 10, 7, 12, 3] 
}
df_bahan = pd.DataFrame(data_bahan)

kolom_aktif = ['Bahan Pakan', 'Harga (Rp/Kg)', 'PK (%)', 'EM (Kkal)', 'Ca (%)', 'P (%)', 'SK (%)', 'Batas Minimal (%)', f'Max_{fase_key} (%)']
df_bahan_view = df_bahan[kolom_aktif].rename(columns={f'Max_{fase_key} (%)': 'Batas Maksimal (%)'})

df_bahan_edited = st.data_editor(df_bahan_view, num_rows="dynamic", use_container_width=True)

# ==========================================
# 5. TABEL 2: TARGET NUTRISI
# ==========================================
st.divider()
st.subheader("🎯 3. Target Kebutuhan Nutrisi (Dapat Disesuaikan)")

data_target = {
    'Komponen Nutrisi': ['Protein Kasar (PK)', 'Energi Metabolis (EM)', 'Kalsium (Ca)', 'Fosfor (P)', 'Serat Kasar (SK)'],
    'Batas Minimal (>=)': target_default,
    'Batas Maksimal (<=)': target_max,
    'Satuan': ['%', 'Kkal', '%', '%', '%']
}
df_target = pd.DataFrame(data_target)
df_target_edited = st.data_editor(df_target, use_container_width=True)

# ==========================================
# 6. ALGORITMA LINEAR PROGRAMMING
# ==========================================
st.divider()

if st.button("🚀 HITUNG FORMULASI OPTIMAL", type="primary", use_container_width=True):
    with st.spinner(f"Menghitung kombinasi terbaik untuk {total_produksi:,.0f} Kg pakan..."):
        
        df_clean = df_bahan_edited.fillna(0)
        n = len(df_clean)
        c = df_clean['Harga (Rp/Kg)'].values 
        
        A_eq = [np.ones(n)]; b_eq = [1.0] 
        A_ub = []; b_ub = []

        min_pk = df_target_edited.loc[0, 'Batas Minimal (>=)']
        min_em = df_target_edited.loc[1, 'Batas Minimal (>=)']
        min_ca = df_target_edited.loc[2, 'Batas Minimal (>=)']
        max_ca = df_target_edited.loc[2, 'Batas Maksimal (<=)']
        min_p  = df_target_edited.loc[3, 'Batas Minimal (>=)']
        max_p  = df_target_edited.loc[3, 'Batas Maksimal (<=)']
        max_sk = df_target_edited.loc[4, 'Batas Maksimal (<=)']

        A_ub.append(-df_clean['PK (%)'].values); b_ub.append(-min_pk)
        A_ub.append(-df_clean['EM (Kkal)'].values); b_ub.append(-min_em)
        A_ub.append(-df_clean['Ca (%)'].values); b_ub.append(-min_ca)
        A_ub.append(df_clean['Ca (%)'].values);  b_ub.append(max_ca)
        A_ub.append(-df_clean['P (%)'].values);  b_ub.append(-min_p)
        A_ub.append(df_clean['P (%)'].values);   b_ub.append(max_p)
        A_ub.append(df_clean['SK (%)'].values);  b_ub.append(max_sk)

        # UPDATE LOGIKA: Membaca Batas Minimal dan Maksimal dari Tabel
        bounds = [(min_val/100, max_val/100) for min_val, max_val in zip(df_clean['Batas Minimal (%)'], df_clean['Batas Maksimal (%)'])]

        res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

        # ==========================================
        # 7. TAMPILAN HASIL (OUTPUT)
        # ==========================================
        if res.success:
            st.success("✅ BERHASIL! Kombinasi Formulasi Termurah Ditemukan.")
            
            hasil_list = []
            total_biaya = 0
            nutrisi_akhir = {'PK':0, 'EM':0, 'Ca':0, 'P':0, 'SK':0}

            for i in range(n):
                proporsi = res.x[i]
                if proporsi > 0.0001:
                    persentase = proporsi * 100
                    bobot_kg = proporsi * total_produksi
                    sub_biaya = bobot_kg * df_clean['Harga (Rp/Kg)'].iloc[i]

                    hasil_list.append({
                        "Bahan Pakan": df_clean['Bahan Pakan'].iloc[i],
                        "Persentase (%)": round(persentase, 2),
                        "Bobot (Kg)": round(bobot_kg, 2),
                        "Total Harga (Rp)": round(sub_biaya, 0)
                    })
                    total_biaya += sub_biaya
                    
                    nutrisi_akhir['PK'] += proporsi * df_clean['PK (%)'].iloc[i]
                    nutrisi_akhir['EM'] += proporsi * df_clean['EM (Kkal)'].iloc[i]
                    nutrisi_akhir['Ca'] += proporsi * df_clean['Ca (%)'].iloc[i]
                    nutrisi_akhir['P']  += proporsi * df_clean['P (%)'].iloc[i]
                    nutrisi_akhir['SK'] += proporsi * df_clean['SK (%)'].iloc[i]

            df_hasil = pd.DataFrame(hasil_list)

            res_col1, res_col2 = st.columns([2, 1])
            with res_col1:
                st.subheader(f"📋 Resep Pencampuran ({total_produksi:,.0f} Kg)")
                st.table(df_hasil.style.format({"Persentase (%)": "{:.2f}%", "Bobot (Kg)": "{:.2f} Kg", "Total Harga (Rp)": "Rp {:,.0f}"}))

            with res_col2:
                st.subheader("💰 Ringkasan Biaya")
                st.metric("Total Biaya", f"Rp {total_biaya:,.0f}")
                st.metric("Biaya per Kg", f"Rp {total_biaya/total_produksi:,.0f} / Kg")

            st.subheader("🔍 Bukti Pemenuhan Nutrisi")
            n1, n2, n3, n4, n5 = st.columns(5)
            n1.metric("Protein Kasar", f"{nutrisi_akhir['PK']:.2f} %")
            n2.metric("Energi", f"{nutrisi_akhir['EM']:.0f} Kkal")
            n3.metric("Kalsium", f"{nutrisi_akhir['Ca']:.2f} %")
            n4.metric("Fosfor", f"{nutrisi_akhir['P']:.2f} %")
            n5.metric("Serat Kasar", f"{nutrisi_akhir['SK']:.2f} %")

            # --- EXCEL DOWNLOAD ---
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_hasil.to_excel(writer, sheet_name='Resep_Formulasi', index=False)
                pd.DataFrame([nutrisi_akhir]).to_excel(writer, sheet_name='Cek_Nutrisi', index=False)
            st.download_button(label="📥 Download Laporan (Excel)", data=output.getvalue(), file_name=f"Laporan_Pakan_{fase_key}_{datetime.date.today()}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary")

        else:
            st.error("⚠️ GAGAL. Data tidak valid secara matematis. Terlalu banyak memaksakan 'Batas Minimal' yang tinggi dapat membuat nutrisi menjadi berlebih/bocor.")