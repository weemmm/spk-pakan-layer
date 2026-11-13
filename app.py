import streamlit as st
import pandas as pd
import plotly.express as px
from config.db_connection import test_db_connection
from modules.db_manager import (
    get_nutrisi_acuan,
    get_bahan_pakan,
    tambah_bahan_pakan,
    update_batch_bahan_pakan,
    hapus_bahan_pakan,
    update_nutrisi_acuan,
    simpan_riwayat_optimasi,
    get_riwayat_optimasi
)
from modules.optimizer import hitung_formulasi_pakan

# 1. Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="SPK Formulasi Pakan Ayam Petelur",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Styling CSS Formal, Bersih, dan Skala Metrik Tanpa Terpotong
st.markdown("""
<style>
    /* Tipografi Global */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        font-size: 15px;
        color: #1E293B;
    }

    /* Penyesuaian Streamlit Metric agar tidak terpotong pada zoom 100% */
    div[data-testid="stMetric"] {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 0.65rem 0.85rem;
    }
    div[data-testid="stMetricLabel"] p {
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        color: #475569 !important;
        margin-bottom: 0.2rem !important;
        white-space: normal !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: clamp(14px, 1.15vw, 17px) !important;
        font-weight: 700 !important;
        color: #0F172A !important;
        white-space: normal !important;
        word-break: break-word !important;
        line-height: 1.25 !important;
    }

    /* Banner Judul Formal & Padat */
    .app-header {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 5px solid #0F766E;
        border-radius: 8px;
        padding: 1rem 1.4rem;
        margin-bottom: 1.2rem;
    }
    .app-header-title {
        font-size: 1.55rem;
        font-weight: 700;
        color: #0F172A;
        margin: 0;
        line-height: 1.3;
        letter-spacing: -0.3px;
    }
    .app-header-subtitle {
        font-size: 0.9rem;
        color: #64748B;
        margin-top: 0.3rem;
        margin-bottom: 0;
    }

    /* Container Card Formal */
    .clean-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 1.15rem 1.3rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
        margin-bottom: 1.1rem;
    }
    .card-header-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 0.2rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .card-header-desc {
        font-size: 0.88rem;
        color: #64748B;
        margin-bottom: 0.85rem;
    }

    /* Tombol Utama Hijau Korporat Padat */
    div.stButton > button[kind="primary"] {
        background-color: #0F766E !important;
        color: #FFFFFF !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        padding: 0.65rem 1.4rem !important;
        border-radius: 8px !important;
        border: none !important;
        width: 100% !important;
        box-shadow: 0 2px 6px rgba(15, 118, 110, 0.2) !important;
        transition: background-color 0.15s ease !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #115E59 !important;
    }

    /* Card Ringkasan Hasil */
    .result-summary-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 0.9rem 1rem;
        text-align: center;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .result-summary-card.highlight {
        background: #F0FDF4;
        border: 1px solid #86EFAC;
    }
    .summary-val {
        font-size: 1.45rem;
        font-weight: 700;
        color: #0F172A;
        margin: 0.2rem 0;
    }
    .summary-val.primary {
        color: #0F766E;
    }
    .summary-lbl {
        font-size: 0.78rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Kotak Peringatan Infeasible */
    .infeasible-box {
        background: #FFFBEB;
        border: 1px solid #FDE68A;
        border-left: 4px solid #D97706;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        color: #78350F;
        margin: 1rem 0;
    }
    .infeasible-box h4 {
        margin: 0 0 0.4rem 0;
        color: #92400E;
        font-size: 1rem;
        font-weight: 700;
    }
    .infeasible-box ul {
        margin: 0.4rem 0 0 1.1rem;
        padding: 0;
    }
    .infeasible-box li {
        margin-bottom: 0.25rem;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)


def main():
    # Inisialisasi Session State
    if "hasil_optimasi" not in st.session_state:
        st.session_state.hasil_optimasi = None
    if "fase_terpilih" not in st.session_state:
        st.session_state.fase_terpilih = 1

    # Sidebar Navigasi Formal
    with st.sidebar:
        st.markdown("#### **SPK Formulasi Pakan**")
        st.caption("Sistem Pendukung Keputusan Ransum Ayam Petelur")

        menu = st.radio(
            "Menu Utama:",
            [
                "Formulasi Pakan",
                "Data Master Bahan Baku",
                "Standar Nutrisi Acuan",
                "Riwayat Formulasi"
            ],
            index=0
        )

        st.markdown("---")
        # Status Koneksi Database
        db_ok, db_msg = test_db_connection()
        if db_ok:
            st.markdown(
                """
                <div style='background:#F0FDF4; border:1px solid #BBF7D0; padding:8px 12px; border-radius:6px;'>
                    <span style='color:#166534; font-weight:600; font-size:0.85rem;'>[Database] MySQL Aktif</span><br>
                    <span style='color:#14532D; font-size:0.75rem;'>Terhubung langsung ke server database MySQL.</span>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """
                <div style='background:#FEF2F2; border:1px solid #FECACA; padding:8px 12px; border-radius:6px;'>
                    <span style='color:#991B1B; font-weight:600; font-size:0.85rem;'>[Database] MySQL Terputus</span><br>
                    <span style='color:#7F1D1D; font-size:0.75rem;'>MySQL offline. Pastikan MySQL Server aktif.</span>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("---")
        st.caption("Modul Metode Penelitian • SciPy HiGHS")

    # Render Halaman Berdasarkan Menu
    if menu == "Formulasi Pakan":
        render_halaman_formulasi()
    elif menu == "Data Master Bahan Baku":
        render_halaman_bahan()
    elif menu == "Standar Nutrisi Acuan":
        render_halaman_nutrisi()
    elif menu == "Riwayat Formulasi":
        render_halaman_riwayat()


# ==============================================================================
# HALAMAN 1: FORMULASI PAKAN (FOKUS OPERASIONAL & KEPUTUSAN BAHAN)
# ==============================================================================
def render_halaman_formulasi():
    st.markdown("""
    <div class="app-header">
        <h2 class="app-header-title">Formulasi Ransum Pakan Ayam Petelur</h2>
        <p class="app-header-subtitle">Tentukan fase ayam petelur, pilih bahan baku yang ingin dipakai, dan jalankan optimasi berbiaya minimum (Least-Cost Feed Formulation).</p>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # CARD 1: Pilihan Fase Produksi & Standar Nutrisi Acuan
    # -------------------------------------------------------------------------
    st.markdown("""
    <div class="clean-card">
        <div class="card-header-title">1. Fase Produksi & Standar Nutrisi Acuan</div>
        <div class="card-header-desc">Pilih fase umur ayam petelur untuk memuat batas kebutuhan nutrisi yang dijadikan acuan solver.</div>
    """, unsafe_allow_html=True)

    list_fase = get_nutrisi_acuan()
    fase_dict = {
        f["id"]: f"{f['nama_fase']} ({f['deskripsi']})" for f in list_fase
    }

    fase_id = st.selectbox(
        "Fase Produksi:",
        options=list(fase_dict.keys()),
        format_func=lambda x: fase_dict[x],
        index=0,
        label_visibility="collapsed"
    )

    target_fase = next((f for f in list_fase if f["id"] == fase_id), list_fase[0])

    # Tampilan Metrik Nutrisi Target Tanpa Elipsis
    st.markdown("<div style='margin-top: 6px;'></div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(
            label="Protein Kasar (PK)",
            value=f"{target_fase['pk_min']:.2f}% - {target_fase['pk_max']:.2f}%"
        )
    with c2:
        st.metric(
            label="Energi Metabolis (EM)",
            value=f"Min {int(target_fase['em_min'])} Kkal/kg"
        )
    with c3:
        st.metric(
            label="Kalsium (Ca)",
            value=f"{target_fase['ca_min']:.2f}% - {target_fase['ca_max']:.2f}%"
        )
    with c4:
        st.metric(
            label="Fosfor Tersedia (P)",
            value=f"{target_fase['p_min']:.2f}% - {target_fase['p_max']:.2f}%"
        )

    with st.expander("Parameter Tambahan (Lemak Kasar, Serat Kasar, Abu)"):
        e1, e2, e3 = st.columns(3)
        e1.write(f"• **Lemak Kasar (LK):** {target_fase['lk_min']:.2f}% - {target_fase['lk_max']:.2f}%")
        e2.write(f"• **Serat Kasar (SK):** Maks {target_fase['sk_max']:.2f}%")
        e3.write(f"• **Abu:** {target_fase['abu_min']:.2f}% - {target_fase['abu_max']:.2f}%")

    st.markdown("</div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # CARD 2: Seleksi Bahan Baku & Penyesuaian Harga Simulasi
    # -------------------------------------------------------------------------
    st.markdown("""
    <div class="clean-card">
        <div class="card-header-title">2. Pemilihan Bahan Baku & Harga Simulasi</div>
        <div class="card-header-desc">Centang bahan baku yang <b>ingin digunakan</b> (Aktif) atau kosongkan jika tidak tersedia. Anda juga dapat menyesuaikan harga pasar untuk simulasi saat ini.</div>
    """, unsafe_allow_html=True)

    # Ambil data master terkini dari database
    df_bahan_db = get_bahan_pakan()

    if "gunakan" not in df_bahan_db.columns:
        df_bahan_db.insert(0, "gunakan", True)

    kolom_formulasi = [
        "gunakan", "nama_bahan", "kategori", "harga_per_kg", "batas_maks_layer",
        "pk", "lk", "sk", "abu", "ca", "p", "em"
    ]
    df_editor = df_bahan_db[kolom_formulasi].copy()

    # Tabel Formulasi: Fokus seleksi Aktif, Harga simulasi, dan Batas toleransi
    edited_data = st.data_editor(
        df_editor,
        use_container_width=True,
        num_rows="fixed",
        column_config={
            "gunakan": st.column_config.CheckboxColumn("Aktif", help="Centang untuk menyertakan bahan ini dalam optimasi formulasi"),
            "nama_bahan": st.column_config.TextColumn("Bahan Baku", disabled=True),
            "kategori": st.column_config.TextColumn("Kategori", disabled=True),
            "harga_per_kg": st.column_config.NumberColumn(
                "Harga Pasar (Rp/kg)", min_value=0.0, step=100.0, format="Rp %d", help="Harga pasar yang berlaku saat ini"
            ),
            "batas_maks_layer": st.column_config.NumberColumn(
                "Batas Maks (%)", min_value=0.0, max_value=100.0, step=0.5, format="%.1f%%", help="Toleransi maksimal bahan dalam campuran pakan"
            ),
            "pk": st.column_config.NumberColumn("PK (%)", disabled=True, format="%.2f%%"),
            "lk": st.column_config.NumberColumn("LK (%)", disabled=True, format="%.2f%%"),
            "sk": st.column_config.NumberColumn("SK (%)", disabled=True, format="%.2f%%"),
            "abu": st.column_config.NumberColumn("Abu (%)", disabled=True, format="%.2f%%"),
            "ca": st.column_config.NumberColumn("Ca (%)", disabled=True, format="%.2f%%"),
            "p": st.column_config.NumberColumn("P (%)", disabled=True, format="%.2f%%"),
            "em": st.column_config.NumberColumn("EM (Kkal)", disabled=True, format="%d"),
        },
        hide_index=True
    )

    jumlah_aktif = int(edited_data["gunakan"].sum())
    total_bahan = len(edited_data)
    st.caption(f"Status Bahan: **{jumlah_aktif}** dari **{total_bahan}** bahan baku aktif dipilih untuk ransum. *(Untuk menambah, mengubah nutrisi dasar, atau menghapus bahan baku permanen, silakan buka menu **Data Master Bahan Baku**)*.")

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # Tombol Eksekusi Optimasi Full-Width
    btn_optimasi = st.button("Jalankan Optimasi Ransum (SciPy HiGHS)", type="primary")

    if btn_optimasi:
        df_aktif = edited_data[edited_data["gunakan"] == True].copy()

        if len(df_aktif) < 2:
            st.warning("Peringatan: Harap centang minimal 2 bahan baku aktif untuk membuat formulasi ransum.")
            st.session_state.hasil_optimasi = None
        else:
            with st.spinner("Memproses penyelesaian Linear Programming..."):
                hasil = hitung_formulasi_pakan(df_aktif, target_fase)
                st.session_state.hasil_optimasi = hasil
                st.session_state.fase_terpilih = fase_id

    st.markdown("</div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # CARD 3 & CARD 4: Hasil Optimasi & Evaluasi Nutrisi
    # -------------------------------------------------------------------------
    hasil = st.session_state.hasil_optimasi
    if hasil:
        # Penanganan Kasus Infeasible (Black Box Validation)
        if not hasil["success"]:
            st.markdown(f"""
            <div class="infeasible-box">
                <h4>Status: Formulasi Tidak Menemukan Solusi Layak (Infeasible)</h4>
                <p>Kombinasi nutrisi target tidak dapat tercapai dengan bahan dan batasan yang aktif saat ini.</p>
                <b>Saran Penyesuaian Formula:</b>
                <ul>
                    <li><b>Aktifkan Bahan Baku Tambahan:</b> Centang bahan baku lain seperti sumber protein (SBM/Tepung Ikan) atau sumber energi (Jagung/Dedak).</li>
                    <li><b>Pastikan Sumber Kalsium Aktif:</b> Centang <i>Tepung Batu</i> atau <i>DCP</i> dengan batas maksimal yang cukup (minimal 8% - 10%).</li>
                    <li><b>Longgarkan Batas Maksimal:</b> Naikkan batas maksimal bahan baku utama jika batasan saat ini terlalu ketat.</li>
                </ul>
                <p style="margin-top: 6px; font-size: 0.85rem; color: #92400E;"><i>Keterangan Solver: {hasil['status_message']}</i></p>
            </div>
            """, unsafe_allow_html=True)
            return

        # JIKA SOLUSI OPTIMAL DITEMUKAN:
        st.markdown("""
        <div class="clean-card">
            <div class="card-header-title">3. Hasil Rekomendasi Ransum Pakan</div>
            <div class="card-header-desc">Komposisi campuran pakan berbiaya terendah yang mematuhi seluruh batasan nutrisi standar.</div>
        """, unsafe_allow_html=True)

        # 1. Form Input Target Total Racikan (Dinamis)
        col_target1, col_target2 = st.columns([1.2, 2.0])
        with col_target1:
            target_kg = st.number_input(
                "Target Total Racikan (kg):",
                min_value=1.0,
                value=100.0,
                step=10.0,
                help="Masukkan total berat pakan yang ingin diracik"
            )
        with col_target2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            st.caption(f"Skala takaran bahan dan total biaya di bawah ini disesuaikan secara dinamis untuk peracikan **{target_kg:,.1f} kg** pakan.")

        # Perhitungan Skalar Pasca-Optimasi (Linear Programming tetap di skala 100% / per kg)
        biaya_per_kg = float(hasil["total_biaya_per_kg"])
        total_biaya_racikan = biaya_per_kg * target_kg

        # 2. Penyesuaian Metrik Kartu Ringkasan Biaya
        r1, r2, r3, r4 = st.columns(4)
        with r1:
            st.markdown(f"""
            <div class="result-summary-card highlight">
                <div class="summary-lbl">Biaya Dasar per Kg</div>
                <div class="summary-val primary">Rp {biaya_per_kg:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        with r2:
            st.markdown(f"""
            <div class="result-summary-card">
                <div class="summary-lbl">Total Biaya Racikan ({target_kg:,.0f} kg)</div>
                <div class="summary-val">Rp {total_biaya_racikan:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        with r3:
            st.markdown(f"""
            <div class="result-summary-card">
                <div class="summary-lbl">Total Berat Racikan</div>
                <div class="summary-val" style="color:#0F766E;">{target_kg:,.1f} kg</div>
            </div>
            """, unsafe_allow_html=True)
        with r4:
            st.markdown(f"""
            <div class="result-summary-card">
                <div class="summary-lbl">Status Solver</div>
                <div class="summary-val" style="color:#475569; font-size:1.15rem;">Optimal ({hasil['execution_time_ms']} ms)</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        # 3. Penyesuaian Kolom Tabel Hasil Ransum Dinamis & Diagram Donut
        col_tabel, col_grafik = st.columns([1.45, 1.0])

        df_komposisi = pd.DataFrame(hasil["komposisi"]).copy()
        # Hitung kebutuhan bahan riil berdasarkan target_kg
        df_komposisi["kebutuhan_kg"] = (df_komposisi["proporsi_desimal"] * target_kg).round(2)
        df_komposisi["subtotal_biaya"] = (df_komposisi["kebutuhan_kg"] * df_komposisi["harga_per_kg"]).round(2)

        df_tampil = df_komposisi[[
            "nama_bahan", "persentase", "kebutuhan_kg", "harga_per_kg", "subtotal_biaya"
        ]].copy()

        # Tambahkan baris TOTAL di akhir tabel
        baris_total = pd.DataFrame([{
            "nama_bahan": "TOTAL KESELURUHAN",
            "persentase": round(df_tampil["persentase"].sum(), 2),
            "kebutuhan_kg": round(target_kg, 2),
            "harga_per_kg": None,
            "subtotal_biaya": round(total_biaya_racikan, 2)
        }])
        df_tabel_final = pd.concat([df_tampil, baris_total], ignore_index=True)

        with col_tabel:
            st.markdown(f"###### Takaran Komposisi Campuran Bahan ({target_kg:,.1f} kg)")
            st.dataframe(
                df_tabel_final,
                column_config={
                    "nama_bahan": "Bahan Baku",
                    "persentase": st.column_config.NumberColumn("Proporsi Optimal (%)", format="%.2f %%"),
                    "kebutuhan_kg": st.column_config.NumberColumn("Kebutuhan Bahan (kg)", format="%.2f kg"),
                    "harga_per_kg": st.column_config.NumberColumn("Harga Satuan (Rp/kg)", format="Rp %d"),
                    "subtotal_biaya": st.column_config.NumberColumn("Subtotal Biaya (Rp)", format="Rp %.2f"),
                },
                use_container_width=True,
                hide_index=True
            )

            # Tombol Unduh Laporan CSV
            csv_racikan = df_tabel_final.to_csv(index=False).encode('utf-8')
            nama_file_csv = f"laporan_racikan_{target_fase['nama_fase'].replace(' ', '_').lower()}_{int(target_kg)}kg.csv"
            st.download_button(
                label="Unduh Laporan Racikan Ini (CSV)",
                data=csv_racikan,
                file_name=nama_file_csv,
                mime="text/csv",
                use_container_width=True
            )

        with col_grafik:
            st.markdown("###### Distribusi Komposisi Bahan Pakan")
            df_terpakai = df_komposisi[df_komposisi["persentase"] > 0.05].copy()

            corporate_palette = [
                "#0F766E", "#0D9488", "#14B8A6", "#0284C7",
                "#38BDF8", "#F59E0B", "#FBBF24", "#64748B", "#475569"
            ]

            fig = px.pie(
                df_terpakai,
                values="persentase",
                names="nama_bahan",
                hole=0.55,
                color_discrete_sequence=corporate_palette
            )
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate="<b>%{label}</b><br>Proporsi: %{value:.2f}%<extra></extra>"
            )
            fig.update_layout(
                margin=dict(t=5, b=5, l=5, r=5),
                height=290,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # ---------------------------------------------------------------------
        # CARD 4: Evaluasi Nutrisi vs Target
        # ---------------------------------------------------------------------
        st.markdown("""
        <div class="clean-card">
            <div class="card-header-title">4. Evaluasi Kualitas Nutrisi Ransum</div>
            <div class="card-header-desc">Pemeriksaan pemenuhan kadar nutrisi ransum hasil campuran terhadap standar kebutuhan acuan.</div>
        """, unsafe_allow_html=True)

        df_nutrisi = pd.DataFrame(hasil["capaian_nutrisi"])

        def format_status_indonesia(s):
            if s == "Sesuai":
                return "Memenuhi Standar"
            elif s == "Kurang":
                return "Di Bawah Batas Minimum"
            elif s == "Melebihi":
                return "Melebihi Batas Maksimum"
            return s

        df_nutrisi["Status Evaluasi"] = df_nutrisi["status"].apply(format_status_indonesia)

        st.dataframe(
            df_nutrisi[[
                "nutrisi", "satuan", "target_min", "target_max",
                "nilai_capaian", "Status Evaluasi"
            ]],
            column_config={
                "nutrisi": "Parameter Nutrisi",
                "satuan": "Satuan",
                "target_min": "Batas Min",
                "target_max": "Batas Maks",
                "nilai_capaian": st.column_config.NumberColumn("Kadar Campuran", format="%.2f"),
                "Status Evaluasi": st.column_config.TextColumn("Status Pemenuhan"),
            },
            use_container_width=True,
            hide_index=True
        )

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # 4. Simpan Formulasi ke Database Riwayat (Sertakan target_kg & total_biaya_racikan)
        c_simpan, c_input = st.columns([1, 2.5])
        with c_input:
            catatan_user = st.text_input(
                "Catatan Formulasi:",
                placeholder="Misal: Uji coba racikan 250 kg untuk stok mingguan",
                label_visibility="collapsed"
            )
        with c_simpan:
            if st.button("Simpan Rekod Formulasi ke Database", use_container_width=True):
                # Siapkan detail komposisi yang memuat skala target_kg
                komposisi_disimpan = []
                for item in hasil["komposisi"]:
                    item_copy = dict(item)
                    item_copy["target_total_kg"] = float(target_kg)
                    item_copy["kebutuhan_kg"] = round(float(item["proporsi_desimal"]) * target_kg, 2)
                    item_copy["subtotal_biaya"] = round(item_copy["kebutuhan_kg"] * float(item["harga_per_kg"]), 2)
                    komposisi_disimpan.append(item_copy)

                catatan_lengkap = f"[Target: {target_kg:,.1f} kg | Total: Rp {total_biaya_racikan:,.2f}] " + (catatan_user if catatan_user else "")

                sukses_rw, pesan_rw = simpan_riwayat_optimasi(
                    fase_id=target_fase["id"],
                    nama_fase=target_fase["nama_fase"],
                    total_biaya_per_kg=biaya_per_kg,
                    status_solver=hasil["status_message"],
                    detail_komposisi=komposisi_disimpan,
                    detail_nutrisi=hasil["capaian_nutrisi"],
                    catatan=catatan_lengkap
                )
                if sukses_rw:
                    st.toast("Formulasi berhasil disimpan ke database riwayat.", icon="✅")
                    st.success(pesan_rw)
                else:
                    st.error(pesan_rw)

        st.markdown("</div>", unsafe_allow_html=True)


# ==============================================================================
# HALAMAN 2: MASTER BAHAN PAKAN (PUSAT CRUD MASTER DATA LENGKAP)
# ==============================================================================
def render_halaman_bahan():
    st.markdown("""
    <div class="app-header">
        <h2 class="app-header-title">Data Master Bahan Baku Pakan (Pusat CRUD)</h2>
        <p class="app-header-subtitle">Kelola daftar bahan baku, ubah kandungan nutrisi master, tambah bahan baru, dan hapus bahan dari database.</p>
    </div>
    """, unsafe_allow_html=True)

    df_bahan = get_bahan_pakan()

    # 1. Tabel Editor Master Data (Bisa Edit Seluruh Nutrisi & Harga Master)
    st.markdown("""
    <div class="clean-card">
        <div class="card-header-title">1. Edit Data Master Bahan Baku & Nilai Nutrisi</div>
        <div class="card-header-desc">Klik langsung pada sel tabel untuk mengubah nilai nutrisi, harga dasar, atau batas maksimal. Tekan tombol simpan di bawah untuk mengeksekusi UPDATE ke database.</div>
    """, unsafe_allow_html=True)

    kolom_master = [
        "id", "kode_bahan", "nama_bahan", "kategori", "harga_per_kg",
        "batas_maks_layer", "pk", "lk", "sk", "abu", "ca", "p", "em"
    ]
    df_editor_master = df_bahan[kolom_master].copy()

    edited_master = st.data_editor(
        df_editor_master,
        use_container_width=True,
        num_rows="fixed",
        column_config={
            "id": st.column_config.NumberColumn("ID", disabled=True),
            "kode_bahan": st.column_config.TextColumn("Kode Bahan", disabled=True),
            "nama_bahan": st.column_config.TextColumn("Nama Bahan Baku"),
            "kategori": st.column_config.TextColumn("Kategori"),
            "harga_per_kg": st.column_config.NumberColumn("Harga Dasar (Rp/kg)", min_value=0.0, step=100.0, format="Rp %d"),
            "batas_maks_layer": st.column_config.NumberColumn("Batas Maks (%)", min_value=0.0, max_value=100.0, step=0.5, format="%.1f%%"),
            "pk": st.column_config.NumberColumn("PK (%)", min_value=0.0, max_value=100.0, step=0.1, format="%.2f%%"),
            "lk": st.column_config.NumberColumn("LK (%)", min_value=0.0, max_value=100.0, step=0.1, format="%.2f%%"),
            "sk": st.column_config.NumberColumn("SK (%)", min_value=0.0, max_value=100.0, step=0.1, format="%.2f%%"),
            "abu": st.column_config.NumberColumn("Abu (%)", min_value=0.0, max_value=100.0, step=0.1, format="%.2f%%"),
            "ca": st.column_config.NumberColumn("Ca (%)", min_value=0.0, max_value=100.0, step=0.05, format="%.2f%%"),
            "p": st.column_config.NumberColumn("P (%)", min_value=0.0, max_value=100.0, step=0.05, format="%.2f%%"),
            "em": st.column_config.NumberColumn("EM (Kkal)", min_value=0.0, step=50.0, format="%d"),
        },
        hide_index=True
    )

    if st.button("Simpan Perubahan ke Database Master", type="primary", use_container_width=True):
        cols_check = ["harga_per_kg", "batas_maks_layer", "pk", "lk", "sk", "abu", "ca", "p", "em"]
        has_negative = False
        for col in cols_check:
            if (edited_master[col].astype(float) < 0).any():
                has_negative = True
                break

        if has_negative:
            st.error("Gagal menyimpan: Terdapat nilai negatif pada tabel bahan baku. Semua angka harus >= 0.")
        else:
            sukses_upd, pesan_upd = update_batch_bahan_pakan(edited_master)
            if sukses_upd:
                st.toast("Perubahan data master berhasil disimpan ke database!", icon="✅")
                st.success(pesan_upd)
                st.rerun()
            else:
                st.error(pesan_upd)

    st.markdown("</div>", unsafe_allow_html=True)

    # 2. Formulir Tambah Bahan Baku Baru (INSERT)
    st.markdown("""
    <div class="clean-card">
        <div class="card-header-title">2. Tambah Bahan Baku Baru (INSERT)</div>
        <div class="card-header-desc">Tambahkan bahan pakan lokal baru ke dalam database master untuk digunakan dalam formulasi.</div>
    """, unsafe_allow_html=True)

    with st.form("form_tambah_master"):
        t_c1, t_c2, t_c3 = st.columns(3)
        with t_c1:
            t_nama = st.text_input("Nama Bahan Baku (Wajib)*", placeholder="Contoh: Tepung Maggot BSF")
            t_kode = st.text_input("Kode Bahan (Opsional)", placeholder="Contoh: MAGGOT")
            t_kategori = st.selectbox("Kategori Bahan", ["Sumber Protein Hewani", "Sumber Protein Nabati", "Sumber Energi", "Sumber Mineral", "Bahan Baku Lokal"])
            t_harga = st.number_input("Harga Beli (Rp/kg)", min_value=0.0, value=7500.0, step=100.0)
        with t_c2:
            t_maks = st.number_input("Batas Maksimal Penggunaan (%)", min_value=0.1, max_value=100.0, value=15.0, step=0.5)
            t_pk = st.number_input("Protein Kasar / PK (%)", min_value=0.0, max_value=100.0, value=40.0, step=0.1)
            t_lk = st.number_input("Lemak Kasar / LK (%)", min_value=0.0, max_value=100.0, value=12.0, step=0.1)
            t_sk = st.number_input("Serat Kasar / SK (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.1)
        with t_c3:
            t_abu = st.number_input("Kadar Abu (%)", min_value=0.0, max_value=100.0, value=8.0, step=0.1)
            t_ca = st.number_input("Kalsium / Ca (%)", min_value=0.0, max_value=100.0, value=3.0, step=0.05)
            t_p = st.number_input("Fosfor / P (%)", min_value=0.0, max_value=100.0, value=1.5, step=0.05)
            t_em = st.number_input("Energi Metabolis / EM (Kkal/kg)", min_value=0.0, value=2600.0, step=50.0)

        submit_tambah = st.form_submit_button("Simpan Bahan Baku Baru ke Database")
        if submit_tambah:
            if not t_nama.strip():
                st.error("Nama bahan baku wajib diisi.")
            else:
                sukses_tb, pesan_tb = tambah_bahan_pakan(
                    kode_bahan=t_kode,
                    nama_bahan=t_nama,
                    kategori=t_kategori,
                    harga_per_kg=t_harga,
                    batas_maks_layer=t_maks,
                    pk=t_pk, lk=t_lk, sk=t_sk, abu=t_abu,
                    ca=t_ca, p=t_p, em=t_em
                )
                if sukses_tb:
                    st.toast("Bahan baku baru berhasil ditambahkan!", icon="✅")
                    st.success(pesan_tb)
                    st.rerun()
                else:
                    st.error(pesan_tb)

    st.markdown("</div>", unsafe_allow_html=True)

    # 3. Hapus Bahan Baku (DELETE)
    st.markdown("""
    <div class="clean-card">
        <div class="card-header-title">3. Hapus Bahan Baku (DELETE)</div>
        <div class="card-header-desc">Hapus bahan baku dari database master secara permanen jika tidak lagi digunakan dalam peternakan.</div>
    """, unsafe_allow_html=True)

    hapus_options = {row["id"]: f"{row['nama_bahan']} (Kode: {row['kode_bahan']}, ID: {row['id']})" for _, row in df_bahan.iterrows()}
    bahan_hapus_id = st.selectbox("Pilih Bahan Baku yang Akan Dihapus:", options=list(hapus_options.keys()), format_func=lambda x: hapus_options[x])

    if st.button("Hapus Bahan Baku Terpilih dari Database", type="secondary"):
        sukses_hp, pesan_hp = hapus_bahan_pakan(bahan_hapus_id)
        if sukses_hp:
            st.toast("Bahan baku berhasil dihapus dari database.", icon="🗑️")
            st.success(pesan_hp)
            st.rerun()
        else:
            st.error(pesan_hp)

    st.markdown("</div>", unsafe_allow_html=True)


# ==============================================================================
# HALAMAN 3: STANDAR KEBUTUHAN NUTRISI ACUAN (VIEW & EDIT)
# ==============================================================================
def render_halaman_nutrisi():
    st.markdown("""
    <div class="app-header">
        <h2 class="app-header-title">Standar Kebutuhan Nutrisi Acuan</h2>
        <p class="app-header-subtitle">Standar nutrisi ransum ayam petelur berdasarkan metodologi penelitian (Fase 1 dan Fase 2).</p>
    </div>
    """, unsafe_allow_html=True)

    list_fase = get_nutrisi_acuan()
    df_fase = pd.DataFrame(list_fase)

    st.markdown("""
    <div class="clean-card">
        <div class="card-header-title">Tabel Batas Nutrisi Berdasarkan Fase</div>
        <div class="card-header-desc">Batas minimum dan batas maksimum zat makanan yang harus dipenuhi oleh ransum campuran.</div>
    """, unsafe_allow_html=True)

    st.dataframe(
        df_fase[[
            "nama_fase", "deskripsi", "pk_min", "pk_max", "lk_min", "lk_max",
            "sk_max", "abu_min", "abu_max", "ca_min", "ca_max", "p_min", "p_max", "em_min"
        ]],
        column_config={
            "nama_fase": "Fase",
            "deskripsi": "Tahap Umur",
            "pk_min": st.column_config.NumberColumn("PK Min", format="%.2f%%"),
            "pk_max": st.column_config.NumberColumn("PK Max", format="%.2f%%"),
            "lk_min": st.column_config.NumberColumn("LK Min", format="%.2f%%"),
            "lk_max": st.column_config.NumberColumn("LK Max", format="%.2f%%"),
            "sk_max": st.column_config.NumberColumn("SK Max", format="%.2f%%"),
            "abu_min": st.column_config.NumberColumn("Abu Min", format="%.2f%%"),
            "abu_max": st.column_config.NumberColumn("Abu Max", format="%.2f%%"),
            "ca_min": st.column_config.NumberColumn("Ca Min", format="%.2f%%"),
            "ca_max": st.column_config.NumberColumn("Ca Max", format="%.2f%%"),
            "p_min": st.column_config.NumberColumn("P Min", format="%.2f%%"),
            "p_max": st.column_config.NumberColumn("P Max", format="%.2f%%"),
            "em_min": st.column_config.NumberColumn("EM Min (Kkal)", format="%d"),
        },
        use_container_width=True,
        hide_index=True
    )

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # Form Edit Standar Nutrisi Acuan
    with st.expander("Edit Standar Nutrisi Acuan ke Database"):
        fase_edit_id = st.selectbox(
            "Pilih Fase yang Akan Diedit:",
            options=[f["id"] for f in list_fase],
            format_func=lambda x: next(f"{f['nama_fase']} - {f['deskripsi']}" for f in list_fase if f["id"] == x)
        )
        fase_data = next(f for f in list_fase if f["id"] == fase_edit_id)

        with st.form("form_edit_nutrisi_master"):
            f_c1, f_c2, f_c3 = st.columns(3)
            with f_c1:
                pk_min_in = st.number_input("PK Min (%)", value=float(fase_data['pk_min']), min_value=0.0, max_value=100.0, step=0.1)
                pk_max_in = st.number_input("PK Maks (%)", value=float(fase_data['pk_max']), min_value=0.0, max_value=100.0, step=0.1)
                lk_min_in = st.number_input("LK Min (%)", value=float(fase_data['lk_min']), min_value=0.0, max_value=100.0, step=0.1)
                lk_max_in = st.number_input("LK Maks (%)", value=float(fase_data['lk_max']), min_value=0.0, max_value=100.0, step=0.1)
            with f_c2:
                sk_max_in = st.number_input("SK Maks (%)", value=float(fase_data['sk_max']), min_value=0.0, max_value=100.0, step=0.1)
                abu_min_in = st.number_input("Abu Min (%)", value=float(fase_data['abu_min']), min_value=0.0, max_value=100.0, step=0.1)
                abu_max_in = st.number_input("Abu Maks (%)", value=float(fase_data['abu_max']), min_value=0.0, max_value=100.0, step=0.1)
                ca_min_in = st.number_input("Ca Min (%)", value=float(fase_data['ca_min']), min_value=0.0, max_value=100.0, step=0.05)
            with f_c3:
                ca_max_in = st.number_input("Ca Maks (%)", value=float(fase_data['ca_max']), min_value=0.0, max_value=100.0, step=0.05)
                p_min_in = st.number_input("P Min (%)", value=float(fase_data['p_min']), min_value=0.0, max_value=100.0, step=0.01)
                p_max_in = st.number_input("P Maks (%)", value=float(fase_data['p_max']), min_value=0.0, max_value=100.0, step=0.01)
                em_min_in = st.number_input("EM Min (Kkal/kg)", value=float(fase_data['em_min']), min_value=0.0, step=50.0)

            simpan_nutrisi_btn = st.form_submit_button("Simpan Perubahan Standar Nutrisi ke Database")
            if simpan_nutrisi_btn:
                sukses_nt, pesan_nt = update_nutrisi_acuan(
                    fase_id=fase_edit_id,
                    pk_min=pk_min_in, pk_max=pk_max_in,
                    lk_min=lk_min_in, lk_max=lk_max_in,
                    sk_max=sk_max_in, abu_min=abu_min_in, abu_max=abu_max_in,
                    ca_min=ca_min_in, ca_max=ca_max_in,
                    p_min=p_min_in, p_max=p_max_in,
                    em_min=em_min_in, em_max=float(fase_data.get('em_max') or 2900.0)
                )
                if sukses_nt:
                    st.toast("Standar nutrisi acuan berhasil diperbarui!", icon="✅")
                    st.success(pesan_nt)
                    st.rerun()
                else:
                    st.error(pesan_nt)

    st.markdown("</div>", unsafe_allow_html=True)


# ==============================================================================
# HALAMAN 4: RIWAYAT FORMULASI
# ==============================================================================
def render_halaman_riwayat():
    st.markdown("""
    <div class="app-header">
        <h2 class="app-header-title">Riwayat Formulasi Ransum Pakan</h2>
        <p class="app-header-subtitle">Arsip hasil perhitungan formulasi pakan yang telah disimpan ke dalam database.</p>
    </div>
    """, unsafe_allow_html=True)

    riwayat = get_riwayat_optimasi(limit=30)
    if not riwayat:
        st.info("Belum ada riwayat formulasi tersimpan. Silakan jalankan perhitungan ransum dan klik simpan pada halaman Formulasi Pakan.")
        return

    for item in riwayat:
        with st.expander(f"{item['tanggal']} | {item['nama_fase']} — Biaya: Rp {float(item['total_biaya_per_kg']):,.2f}/kg ({item['status_solver']})"):
            c1, c2 = st.columns([1.2, 1.0])
            with c1:
                st.markdown("**Komposisi Campuran:**")
                df_k = pd.DataFrame(item["detail_komposisi"])
                if "kebutuhan_kg" in df_k.columns and "subtotal_biaya" in df_k.columns:
                    kolom_hist = ["nama_bahan", "persentase", "kebutuhan_kg", "harga_per_kg", "subtotal_biaya"]
                    config_hist = {
                        "nama_bahan": "Bahan Baku",
                        "persentase": st.column_config.NumberColumn("Proporsi (%)", format="%.2f%%"),
                        "kebutuhan_kg": st.column_config.NumberColumn("Kebutuhan (kg)", format="%.2f kg"),
                        "harga_per_kg": st.column_config.NumberColumn("Harga (Rp)", format="Rp %d"),
                        "subtotal_biaya": st.column_config.NumberColumn("Subtotal Biaya", format="Rp %.2f"),
                    }
                else:
                    kolom_hist = ["nama_bahan", "persentase", "bobot_kg_per_100kg", "harga_per_kg"]
                    config_hist = {
                        "nama_bahan": "Bahan",
                        "persentase": st.column_config.NumberColumn("Proporsi (%)", format="%.2f%%"),
                        "bobot_kg_per_100kg": st.column_config.NumberColumn("Kg / 100 kg", format="%.2f kg"),
                        "harga_per_kg": st.column_config.NumberColumn("Harga (Rp)", format="Rp %d"),
                    }
                st.dataframe(
                    df_k[kolom_hist],
                    column_config=config_hist,
                    use_container_width=True,
                    hide_index=True
                )
            with c2:
                st.markdown("**Evaluasi Nutrisi:**")
                df_n = pd.DataFrame(item["detail_nutrisi"])
                st.dataframe(
                    df_n[["nutrisi", "nilai_capaian", "status"]],
                    column_config={
                        "nutrisi": "Nutrisi",
                        "nilai_capaian": st.column_config.NumberColumn("Kadar Ransum", format="%.2f"),
                        "status": "Status"
                    },
                    use_container_width=True,
                    hide_index=True
                )
            if item.get("catatan"):
                st.caption(f"Catatan: {item['catatan']}")


if __name__ == "__main__":
    main()
