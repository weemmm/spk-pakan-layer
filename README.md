# Sistem Pendukung Keputusan (SPK) Formulasi Pakan Ayam Petelur (Layer)
## Berbasis Linear Programming (SciPy HiGHS), Streamlit, dan MySQL

Aplikasi ini merupakan implementasi Sistem Pendukung Keputusan untuk menentukan formulasi pakan ayam petelur berbiaya terendah (*Least-Cost Feed Formulation*) yang memenuhi standar kebutuhan nutrisi SNI / NRC untuk **Fase 1 (2% - 28 minggu)** dan **Fase 2 (28 minggu - afkir)**.

---

### 1. Fitur Utama
1. **Engine Linear Programming (SciPy HiGHS)**:
   - Fungsi Tujuan: Meminimalkan total biaya pembelian bahan baku per kg ($\min \sum c_j x_j$).
   - Kendala Nutrisi: Memenuhi batas minimum dan maksimum untuk 7 parameter nutrisi: Protein Kasar (PK), Lemak Kasar (LK), Serat Kasar (SK), Abu, Kalsium (Ca), Fosfor Tersedia (P), dan Energi Metabolis (EM).
   - Kendala Kesetaraan: Total proporsi bahan baku tepat 100% ($\sum x_j = 1.0$).
   - Batas Toleransi Bahan: Setiap bahan baku memiliki batas inklusi maksimum untuk menjaga kesehatan dan produktivitas ayam petelur.
2. **Antarmuka Interaktif Streamlit**:
   - Pemilihan fase produksi secara dinamis.
   - Tabel `st.data_editor` untuk memperbarui harga pasar bahan baku dan batas toleransi secara langsung.
   - Visualisasi distribusi ransum (Donut Chart interaktif).
   - Tabel evaluasi pemenuhan nutrisi (Aktual vs Target Acuan).
   - Penyimpanan riwayat formulasi ke database.
3. **Database Layer (MySQL Murni)**:
   - Terintegrasi langsung dengan database MySQL (`database.sql` / `spk_pakan_layer`).
   - Menyimpan seluruh master nutrisi acuan, katalog bahan baku pakan, dan riwayat formulasi berbasis JSON secara terpusat.

---

### 2. Struktur Proyek
```
Program/
├── .env                  # Konfigurasi koneksi MySQL
├── .env.example          # Template konfigurasi environment
├── database.sql          # Skema DDL dan data awal (seeding)
├── requirements.txt      # Daftar dependensi Python
├── app.py                # Aplikasi antarmuka utama (Streamlit)
├── config/
│   └── db_connection.py  # Koneksi & uji status database MySQL
├── modules/
│   ├── db_manager.py     # Data access layer (CRUD bahan, nutrisi, riwayat)
│   └── optimizer.py      # Solver optimasi Linear Programming (SciPy HiGHS)
├── tests/
│   └── test_optimizer.py # Unit test solver SciPy
└── README.md             # Dokumentasi teknis
```

---

### 3. Cara Menjalankan Aplikasi

1. **Jalankan Unit Test**:
   ```powershell
   .venv\Scripts\python.exe tests/test_optimizer.py
   ```

2. **Jalankan Aplikasi Web Streamlit**:
   ```powershell
   .venv\Scripts\streamlit.exe run app.py
   ```
   Aplikasi akan terbuka otomatis di browser pada alamat `http://localhost:8501`.

3. **Menghubungkan ke MySQL (Opsional)**:
   - Jalankan MySQL (misal melalui XAMPP atau MySQL Workbench).
   - Impor file `database.sql`:
     ```sql
     source database.sql;
     ```
   - Sesuaikan kredensial di file `.env` jika diperlukan.
