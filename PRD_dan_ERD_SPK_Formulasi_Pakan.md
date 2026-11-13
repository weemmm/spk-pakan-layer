# DOKUMEN SPESIFIKASI KEBUTUHAN PRODUK (PRODUCT REQUIREMENT DOCUMENT - PRD)
## & PERANCANGAN BASIS DATA (ENTITY RELATIONSHIP DIAGRAM - ERD)

---

**Nama Sistem**: Sistem Pendukung Keputusan (SPK) Formulasi Pakan Ayam Petelur (*Least-Cost Feed Formulation*)  
**Metode Algoritma**: *Linear Programming* (SciPy HiGHS Solver)  
**Teknologi**: Python, Streamlit, Plotly, MySQL Database Server  
**Penyusun**: Wildan Mursalin Rizqia  
**Institusi**: Universitas Ahmad Dahlan (UAD)  
**Mata Kuliah / Bidang**: Metode Penelitian / Sistem Pendukung Keputusan  
**Versi Dokumen**: 1.0 (Final Draft)  
**Tanggal**: 22 Oktober 2026  

---

## DAFTAR ISI
1. [Ringkasan Eksekutif & Latar Belakang](#1-ringkasan-eksekutif--latar-belakang)
2. [Tujuan Produk & Indikator Keberhasilan (OKRs)](#2-tujuan-produk--indikator-keberhasilan-okrs)
3. [Profil Pengguna (User Persona) & Ruang Lingkup](#3-profil-pengguna-user-persona--ruang-lingkup)
4. [Formulasi Matematis Linear Programming](#4-formulasi-matematis-linear-programming)
5. [Kebutuhan Fungsional (Functional Requirements)](#5-kebutuhan-fungsional-functional-requirements)
6. [Kebutuhan Non-Fungsional (Non-Functional Requirements)](#6-kebutuhan-non-fungsional-non-functional-requirements)
7. [Arsitektur Sistem](#7-arsitektur-sistem)
8. [Perancangan Basis Data & ERD (Entity Relationship Diagram)](#8-perancangan-basis-data--erd-entity-relationship-diagram)
9. [Kamus Data (Data Dictionary)](#9-kamus-data-data-dictionary)
10. [Rencana Pengujian (Testing Plan) & Matriks Verifikasi](#10-rencana-pengujian-testing-plan--matriks-verifikasi)
    - [10.1 Matriks Benchmarking Algoritma (6 Skenario Skripsi)](#101-matriks-benchmarking-algoritma-6-skenario-skripsi)
    - [10.2 Matriks Black Box Testing (12 Skenario Pengujian Fungsional)](#102-matriks-black-box-testing-12-skenario-pengujian-fungsional)

---

## 1. Ringkasan Eksekutif & Latar Belakang

### 1.1 Latar Belakang
Industri peternakan ayam petelur (*layer*) menghadapi tantangan utama pada komponen biaya pakan ransum, yang berkontribusi sebesar **70% hingga 80%** dari total seluruh biaya operasional peternakan. Di sisi lain, harga bahan baku pakan lokal (seperti Jagung Kuning, Dedak Padi, Bungkil Kedelai, Tepung Ikan) bersifat fluktuatif di pasaran. 

Pemenuhan nutrisi ayam petelur harus memenuhi standar ketat acuan nasional (SNI) maupun internasional (NRC) untuk menjaga stabilitas produksi telur, kesehatan pencernaan, dan kualitas kerabang telur. Nutrisi tersebut mencakup:
- **Protein Kasar (PK)**
- **Lemak Kasar (LK)**
- **Serat Kasar (SK)**
- **Abu (Ash)**
- **Kalsium (Ca)**
- **Fosfor Tersedia (P)**
- **Energi Metabolis (EM)**

Kebutuhan nutrisi tersebut terbagi ke dalam fase pemeliharaan:
1. **Fase 1 (Umur 2% - 28 minggu)**: Fase bertelur awal di mana ayam masih bertumbuh sekaligus mulai berproduksi puncak, membutuhkan konsentrasi asam amino dan kalsium terukur.
2. **Fase 2 (Umur 28 minggu - Afkir)**: Fase produksi stabil hingga akhir, memerlukan asupan kalsium lebih tinggi demi kekuatan kerabang telur.

### 1.2 Permasalahan
Perhitungan ransum manual (seperti metode *Pearson Square* atau *Trial-and-Error*) memiliki kelemahan mendasar:
1. Tidak menjamin tercapainya biaya terendah (*least-cost solution*).
2. Sulit menyeimbangkan lebih dari 3 kendala nutrisi secara simultan.
3. Lambat merespons perubahan harga pasar bahan baku lokal harian/mingguan.

### 1.3 Solusi yang Ditawarkan
Membangun sebuah **Sistem Pendukung Keputusan (SPK)** terintegrasi berbasis web (*Streamlit*) yang mengimplementasikan metode optimasi **Linear Programming (metode HiGHS via SciPy)** dengan penyimpanan basis data relasional terpusat **MySQL Database Server**.

---

## 2. Tujuan Produk & Indikator Keberhasilan (OKRs)

### 2.1 Tujuan Produk
1. Memberikan rekomendasi persentase campuran bahan pakan ayam petelur yang meminimalkan total biaya per kg dan per sak (50 kg).
2. Memastikan seluruh 7 parameter nutrisi esensial terpenuhi dalam rentang toleransi standar SNI/NRC.
3. Menyediakan antarmuka interaktif yang memudahkan peternak/peneliti melakukan simulasi perubahan harga dan batas toleransi bahan baku (*batch update*).
4. Menyimpan riwayat formulasi untuk keperluan audit, perbandingan, dan evaluasi berkala.

### 2.2 Indikator Keberhasilan (Success Metrics)
- **Akurasi Formulasi**: 100% mematuhi batas nutrisi target dan batasan inklusi bahan baku.
- **Efisiensi Waktu**: Waktu eksekusi optimasi solver $\le 100\text{ ms}$.
- **Keandalan Sistem**: Integritas data terjamin 100% melalui transaksi ACID RDBMS MySQL dengan ketersediaan koneksi real-time.
- **User Usability**: Peternak dapat menjalankan simulasi formulasi dalam kurang dari 3 langkah navigasi.

---

## 3. Profil Pengguna (User Persona) & Ruang Lingkup

### 3.1 Profil Pengguna
1. **Peternak Mandiri / Formulator Ransum Layer**:
   - Karakteristik: Membutuhkan informasi takaran bahan nyata (kg/sak 50 kg dan kg/100 kg), biaya riil, serta kemudahan mengubah harga harian bahan baku.
2. **Peneliti / Akademisi Peternakan**:
   - Karakteristik: Menguji sensitivitas model, memodifikasi standar batasan nutrisi fase, mengevaluasi status ketercapaian nutrisi (Aktual vs Target Acuan).

### 3.2 Ruang Lingkup Proyek
| Kategori | Di Dalam Ruang Lingkup (In-Scope) | Di Luar Ruang Lingkup (Out-of-Scope) |
|---|---|---|
| **Hewan Ternak** | Ayam Petelur (*Layer*) Fase 1 dan Fase 2 | Broiler (Ayam Pedaging), Ruminansia (Sapi/Kambing) |
| **Metode Optimasi** | Linear Programming (Simplex / HiGHS interior point) | Non-linear Programming, Algoritma Genetika |
| **Bahan Baku** | 9 Bahan Baku Pokok Ransum Lokal (Jagung, Dedak, Pollard, Minyak Sawit, SBM, Tepung Ikan, MBM, Tepung Batu, DCP) + Custom CRUD | Pengadaan stok otomatis / integrasi e-commerce |
| **Platform** | Web Application lokal/intranet (Streamlit) | Mobile native apps (Android/iOS) |

---

## 4. Formulasi Matematis Linear Programming

Sistem memodelkan pencarian ransum sebagai permasalahan optimasi matematika linier terstruktur (*Least-Cost Feed Formulation*):

### 4.1 Variabel Keputusan (Decision Variables)
Misalkan $n$ adalah jumlah bahan baku yang dipilih aktif oleh pengguna.
$$x_j = \text{proporsi penggunaan bahan baku ke-} j \quad (j = 1, 2, \dots, n)$$

### 4.2 Fungsi Tujuan (Objective Function)
Meminimalkan total biaya pembelian bahan baku pakan per 1 kilogram ransum:
$$\min Z = \sum_{j=1}^{n} c_j \cdot x_j$$
*Keterangan:*  
$c_j$ = harga bahan baku ke-$j$ per kilogram (Rp/kg).

### 4.3 Kendala-Kendala (Constraints)
1. **Kendala Kesetaraan Proporsi Total (Equality Constraint)**:
   Total persentase seluruh bahan pakan harus tepat 100% (proporsi desimal = 1.0):
   $$\sum_{j=1}^{n} x_j = 1.0$$

2. **Kendala Batas Nutrisi (Nutrient Inequalities)**:
   Untuk setiap parameter nutrisi $k$ (PK, LK, SK, Abu, Ca, P, EM):
   - Batas Minimum:
     $$\sum_{j=1}^{n} a_{kj} \cdot x_j \ge \text{Target\_Min}_k \iff -\sum_{j=1}^{n} a_{kj} \cdot x_j \le -\text{Target\_Min}_k$$
   - Batas Maksimum:
     $$\sum_{j=1}^{n} a_{kj} \cdot x_j \le \text{Target\_Max}_k$$
   *Keterangan:*  
   $a_{kj}$ = kandungan nutrisi parameter ke-$k$ pada bahan baku ke-$j$.

3. **Kendala Batas Toleransi Penggunaan Bahan (Bounds)**:
   Mencegah keracunan atau gangguan pencernaan pada ayam petelur akibat kelebihan bahan tertentu:
   $$\frac{\text{Batas\_Min}_j}{100} \le x_j \le \frac{\text{Batas\_Maks}_j}{100}$$

---

## 5. Kebutuhan Fungsional (Functional Requirements)

| Kode FR | Modul / Fitur | Deskripsi Kebutuhan Fungsional |
|---|---|---|
| **FR-01** | **Koneksi Database MySQL** | Sistem terhubung langsung ke MySQL Database Server (`spk_pakan_layer`) sebagai RDBMS utama, menampilkan indikator status koneksi aktif pada antarmuka ([Database] MySQL Aktif), serta menangani eksepsi koneksi secara aman. |
| **FR-02** | **Pemilihan Fase Produksi** | Sistem menyediakan pilihan fase ayam petelur (Fase 1: 2%-28 minggu dan Fase 2: 28 minggu-afkir) yang secara dinamis memuat target acuan nutrisi standar (PK, LK, SK, Abu, Ca, P, EM). |
| **FR-03** | **Manajemen Simulasi Bahan** | Pengguna dapat mengaktifkan/menonaktifkan bahan baku secara selektif via checkbox tabel, mengubah harga pasar secara langsung (*in-place editor*), dan memodifikasi batas penggunaan maksimum. |
| **FR-04** | **Validasi & Solvabilitas LP** | Sebelum solver dijalankan, sistem melakukan validasi: <br>1. Jumlah bahan aktif minimal 2.<br>2. Tidak ada angka negatif pada harga, kandungan nutrisi, dan batas toleransi.<br>3. Total kapasitas batas maksimal bahan baku $\ge 100\%$. |
| **FR-05** | **Eksekusi Solver SciPy HiGHS** | Sistem menjalankan modul `scipy.optimize.linprog(method='highs')`. Jika solusi optimal ditemukan (*Optimal Found*), sistem menghasilkan proporsi bahan, biaya per kg, dan biaya per sak (50 kg). Jika solusi tidak ditemukan (*Infeasible*), sistem menampilkan diagnosa penyebab dan rekomendasi solutif. |
| **FR-06** | **Visualisasi & Evaluasi** | Sistem menampilkan hasil optimasi dalam bentuk: <br>1. Donut Chart interaktif (Plotly) proporsi bahan pakan.<br>2. Tabel konversi bobot (proporsi %, bobot per sak 50 kg, bobot per 100 kg, kontribusi biaya).<br>3. Tabel perbandingan pemenuhan nutrisi (Target Acuan vs Aktual Capaian beserta indikator status: *Sesuai*, *Kurang*, atau *Melebihi*). |
| **FR-07** | **Penyimpanan Riwayat** | Pengguna dapat menyimpan hasil formulasi yang telah diverifikasi ke basis data beserta catatan opsional. |
| **FR-08** | **CRUD Data Master Bahan** | Sistem menyediakan halaman khusus untuk menambah bahan baru, memperbarui nilai nutrisi secara massal (*batch update*), dan menghapus bahan baku. |
| **FR-09** | **CRUD Standar Nutrisi** | Sistem memungkinkan penyesuaian nilai batas min dan maks pada standar nutrisi acuan untuk setiap fase. |
| **FR-10** | **Manajemen Riwayat Formulasi** | Sistem menampilkan log riwayat optimasi sebelumnya, menampilkan rincian JSON komposisi dan capaian nutrisi, serta mendukung penghapusan riwayat tertentu. |

---

## 6. Kebutuhan Non-Fungsional (Non-Functional Requirements)

| Kategori | Spesifikasi Kebutuhan Non-Fungsional |
|---|---|
| **Performa & Latensi** | - Komputasi optimasi solver diselesaikan dalam rentang waktu $\le 100\text{ ms}$.<br>- Waktu muat awal halaman (*first contentful render*) $\le 2\text{ detik}$. |
| **Keandalan (Reliability)** | - Penanganan eksepsi koneksi basis data MySQL dan komputasi linier (*singular matrix / unbounded / infeasible solution*) secara terstruktur dengan umpan balik pesan informatif kepada pengguna.<br>- Menjaga konsistensi data dengan validasi tipe dan batas numerik sebelum eksekusi kueri transaksi ke basis data. |
| **Kegunaan (Usability)** | - Tampilan antarmuka bersih, responsif, dan menggunakan tipografi modern berskala (*clamped metrics*).<br>- Warna status informatif: Hijau (*Sesuai*), Merah (*Kurang*), Kuning (*Melebihi*). |
| **Portabilitas (Portability)** | - Dapat dijalankan di lingkungan Windows, Linux, maupun macOS yang mendukung Python 3.10+ dan browser berbasis Chromium/Firefox/Safari. |
| **Integritas Data** | - Kolom numerik kritis menggunakan presisi tinggi (`DECIMAL(5,2)`, `DECIMAL(7,2)`, `DECIMAL(10,2)`).<br>- Integritas referensial antar entitas dijaga menggunakan kunci asing (*Foreign Key with ON DELETE CASCADE*). |

---

## 7. Arsitektur Sistem

Arsitektur sistem dibangun dengan pola berlapis (*Layered Architecture*):

```
+-------------------------------------------------------------+
|                 PRESENTATION LAYER (UI)                     |
|           Streamlit Web Interface (app.py)                  |
|    - Interaktif Widgets (st.data_editor, st.metric)          |
|    - Visualisasi Plotly Charts (Donut & Breakdown)           |
|    - Indikator Status Database: [Database] MySQL Aktif       |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                  BUSINESS LOGIC LAYER                       |
|   1. Optimizer Module (modules/optimizer.py)                |
|      - Formulator Matriks LP (c, A_ub, b_ub, A_eq, b_eq)   |
|      - SciPy HiGHS Solver Engine                            |
|      - Evaluator Status Nutrisi & Diagnosa Infeasible       |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                 DATA ACCESS LAYER (DAL)                     |
|   2. Database Manager (modules/db_manager.py)               |
|      - Abstraksi Akses Data & Handler Validasi Numerik      |
|      - Konektor MySQL Murni (config/db_connection.py)       |
|      - Eksekusi Transaksi CRUD & Logging Riwayat Formulasi  |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                 PRIMARY STORAGE (RDBMS)                     |
|             MySQL Server (spk_pakan_layer)                  |
|   - nutrisi_acuan  |  bahan_pakan  |  riwayat_optimasi      |
+-------------------------------------------------------------+
```

---

## 8. Perancangan Basis Data & ERD (Entity Relationship Diagram)

### 8.1 Model Konseptual Hubungan Entitas
Basis data dirancang untuk mendukung operasional formulasi pakan secara efisien:
1. **Entitas `nutrisi_acuan`**: Menyimpan batas acuan fisiologis nutrisi ayam petelur menurut fase pertumbuhannya (1 to Many terhadap `riwayat_optimasi`).
2. **Entitas `bahan_pakan`**: Menyimpan katalog master bahan baku pakan beserta profil kimiawi 7 unsur nutrisi, harga beli, dan batas ambang biologis.
3. **Entitas `riwayat_optimasi`**: Menyimpan hasil historis komputasi formulasi pakan, mencakup relasi ke fase nutrisi acuan, ringkasan biaya, status solver, serta detail struktur formulasi dalam format JSON terstruktur.

### 8.2 Entity Relationship Diagram (Visual Mermaid)

```mermaid
erDiagram
    NUTRISI_ACUAN ||--o{ RIWAYAT_OPTIMASI : "menjadi acuan pada"
    
    NUTRISI_ACUAN {
        int id PK "Auto Increment"
        string nama_fase "Nama Fase (Fase 1 / Fase 2)"
        string deskripsi "Keterangan Umur Layer"
        decimal pk_min "Protein Kasar Min (%)"
        decimal pk_max "Protein Kasar Max (%)"
        decimal lk_min "Lemak Kasar Min (%)"
        decimal lk_max "Lemak Kasar Max (%)"
        decimal sk_min "Serat Kasar Min (%)"
        decimal sk_max "Serat Kasar Max (%)"
        decimal abu_min "Kadar Abu Min (%)"
        decimal abu_max "Kadar Abu Max (%)"
        decimal ca_min "Kalsium Min (%)"
        decimal ca_max "Kalsium Max (%)"
        decimal p_min "Fosfor Tersedia Min (%)"
        decimal p_max "Fosfor Tersedia Max (%)"
        decimal em_min "Energi Metabolis Min (Kkal/kg)"
        decimal em_max "Energi Metabolis Max (Kkal/kg)"
    }

    BAHAN_PAKAN {
        int id PK "Auto Increment"
        string kode_bahan UK "Kode Unik Bahan (misal: JAGUNG)"
        string nama_bahan "Nama Bahan Baku Lokal"
        string kategori "Kategori Nutrisi / Sumber"
        decimal pk "Protein Kasar (%)"
        decimal lk "Lemak Kasar (%)"
        decimal sk "Serat Kasar (%)"
        decimal abu "Abu (%)"
        decimal ca "Kalsium (%)"
        decimal p "Fosfor (%)"
        decimal em "Energi Metabolis (Kkal/kg)"
        decimal harga_per_kg "Harga Bahan Baku (Rp/kg)"
        decimal batas_min_layer "Batas Minimum Inklusi (%)"
        decimal batas_maks_layer "Batas Maksimum Inklusi (%)"
    }

    RIWAYAT_OPTIMASI {
        int id PK "Auto Increment"
        datetime tanggal "Waktu Eksekusi Formulasi"
        int fase_id FK "Relasi ke nutrisi_acuan.id"
        string nama_fase "Nama Fase saat Optimasi"
        decimal total_biaya_per_kg "Biaya Terendah Hasil LP (Rp/kg)"
        string status_solver "Status Penyelesaian HiGHS"
        json detail_komposisi "JSON Data Rincian Tiap Bahan Terpilih"
        json detail_nutrisi "JSON Data Evaluasi Capaian Nutrisi"
        text catatan "Catatan Pengguna"
    }
```

---

## 9. Kamus Data (Data Dictionary)

### 9.1 Tabel: `nutrisi_acuan`
- **Deskripsi**: Menyimpan standar kebutuhan nutrisi ayam petelur per fase produksi.
- **Kunci Utama**: `id`

| Nama Kolom | Tipe Data | Nullable | Nilai Default | Keterangan |
|---|---|:---:|:---:|---|
| `id` | `INT` | NO | AUTO_INCREMENT | Identifier unik fase nutrisi acuan |
| `nama_fase` | `VARCHAR(50)` | NO | - | Nama fase (contoh: 'Fase 1', 'Fase 2') |
| `deskripsi` | `VARCHAR(150)` | YES | NULL | Rentang umur ayam (misal: '2% - 28 minggu') |
| `pk_min` | `DECIMAL(5,2)` | NO | - | Batas minimal Protein Kasar (%) |
| `pk_max` | `DECIMAL(5,2)` | NO | - | Batas maksimal Protein Kasar (%) |
| `lk_min` | `DECIMAL(5,2)` | NO | - | Batas minimal Lemak Kasar (%) |
| `lk_max` | `DECIMAL(5,2)` | NO | - | Batas maksimal Lemak Kasar (%) |
| `sk_min` | `DECIMAL(5,2)` | NO | 0.00 | Batas minimal Serat Kasar (%) |
| `sk_max` | `DECIMAL(5,2)` | NO | - | Batas maksimal Serat Kasar (%) |
| `abu_min` | `DECIMAL(5,2)` | NO | - | Batas minimal kadar Abu (%) |
| `abu_max` | `DECIMAL(5,2)` | NO | - | Batas maksimal kadar Abu (%) |
| `ca_min` | `DECIMAL(5,2)` | NO | - | Batas minimal Kalsium (%) |
| `ca_max` | `DECIMAL(5,2)` | NO | - | Batas maksimal Kalsium (%) |
| `p_min` | `DECIMAL(5,2)` | NO | - | Batas minimal Fosfor Tersedia (%) |
| `p_max` | `DECIMAL(5,2)` | NO | - | Batas maksimal Fosfor Tersedia (%) |
| `em_min` | `DECIMAL(7,2)` | NO | 2750.00 | Batas minimal Energi Metabolis (Kkal/kg, sesuai Tabel 2.2 SNI/NRC: 2750 - 2900 Kkal/kg) |
| `em_max` | `DECIMAL(7,2)` | NO | 2900.00 | Batas maksimal Energi Metabolis (Kkal/kg, sesuai Tabel 2.2 SNI/NRC: 2750 - 2900 Kkal/kg) |

---

### 9.2 Tabel: `bahan_pakan`
- **Deskripsi**: Menyimpan data master bahan baku pakan lokal beserta profil nutrisi dan batas inklusi.
- **Kunci Utama**: `id` | **Kunci Unik**: `kode_bahan`

| Nama Kolom | Tipe Data | Nullable | Nilai Default | Keterangan |
|---|---|:---:|:---:|---|
| `id` | `INT` | NO | AUTO_INCREMENT | Identifier unik bahan baku |
| `kode_bahan` | `VARCHAR(20)` | NO | - | Kode unik bahan baku (contoh: 'JAGUNG', 'SBM') |
| `nama_bahan` | `VARCHAR(100)` | NO | - | Nama lengkap bahan baku pakan |
| `kategori` | `VARCHAR(50)` | YES | 'Bahan Baku Lokal' | Klasifikasi peran nutrisi (misal: 'Sumber Energi') |
| `pk` | `DECIMAL(5,2)` | NO | 0.00 | Kandungan Protein Kasar (%) |
| `lk` | `DECIMAL(5,2)` | NO | 0.00 | Kandungan Lemak Kasar (%) |
| `sk` | `DECIMAL(5,2)` | NO | 0.00 | Kandungan Serat Kasar (%) |
| `abu` | `DECIMAL(5,2)` | NO | 0.00 | Kandungan Abu (%) |
| `ca` | `DECIMAL(5,2)` | NO | 0.00 | Kandungan Kalsium (%) |
| `p` | `DECIMAL(5,2)` | NO | 0.00 | Kandungan Fosfor (%) |
| `em` | `DECIMAL(7,2)` | NO | 0.00 | Kandungan Energi Metabolis (Kkal/kg) |
| `harga_per_kg` | `DECIMAL(10,2)` | NO | - | Harga beli per kilogram (Rp/kg) |
| `batas_min_layer`| `DECIMAL(5,2)` | NO | 0.00 | Batas minimal pemakaian dalam ransum (%) |
| `batas_maks_layer`| `DECIMAL(5,2)`| NO | 100.00 | Batas maksimal pemakaian dalam ransum (%) |

---

### 9.3 Tabel: `riwayat_optimasi`
- **Deskripsi**: Menyimpan hasil eksekusi optimasi formulasi pakan ransum ayam petelur.
- **Kunci Utama**: `id` | **Kunci Tamu**: `fase_id` $\rightarrow$ `nutrisi_acuan(id)`

| Nama Kolom | Tipe Data | Nullable | Nilai Default | Keterangan |
|---|---|:---:|:---:|---|
| `id` | `INT` | NO | AUTO_INCREMENT | Identifier unik riwayat optimasi |
| `tanggal` | `DATETIME` | NO | CURRENT_TIMESTAMP | Tanggal dan waktu formulasi dihitung |
| `fase_id` | `INT` | NO | - | Kunci tamu merujuk ke tabel `nutrisi_acuan` |
| `nama_fase` | `VARCHAR(50)` | NO | - | Label nama fase saat formulasi dibuat |
| `total_biaya_per_kg` | `DECIMAL(10,2)` | NO | - | Nilai optimum fungsi tujuan $Z$ (Rp/kg) |
| `status_solver` | `VARCHAR(50)` | NO | - | Status luaran solver (misal: 'Optimal Solution Found (HiGHS)') |
| `detail_komposisi` | `JSON` | NO | - | Rincian array JSON: proporsi, persentase %, bobot sak 50 kg, bobot 100 kg, dan kontribusi biaya per bahan |
| `detail_nutrisi` | `JSON` | NO | - | Rincian array JSON: perbandingan nilai aktual vs nilai target min/max dan status kesesuaian |
| `catatan` | `TEXT` | YES | NULL | Catatan khusus formulasi dari pengguna |

---

## 10. Rencana Pengujian (Testing Plan) & Matriks Verifikasi

Pengujian sistem dilakukan dalam dua tingkatan utama sesuai dengan naskah Skripsi Bab IV: pengujian benchmarking akurasi algoritma *Linear Programming* (HiGHS) pada 6 skenario perlakuan formulasi, serta pengujian fungsionalitas perangkat lunak (*Black Box Testing*) mencakup 12 skenario operasional sistem secara menyeluruh.

### 10.1 Matriks Benchmarking Algoritma (6 Skenario Skripsi)
Pengujian algoritma dilakukan untuk memvalidasi performa solver SciPy HiGHS dalam mencari solusi *Least-Cost* pada berbagai kondisi pasar dan pembatasan biologis pakan layer:

| ID Skenario | Nama & Deskripsi Skenario | Parameter & Batasan Khusus | Status Solver | Biaya Formulasi (Rp/kg) | Ringkasan Komposisi Ransum Terpilih | Kesesuaian Standar Nutrisi |
|:---:|---|---|:---:|:---:|---|:---:|
| **Skenario 1** | **Fase 1 - Baseline Normal** | 9 Bahan Baku Default Aktif, Standar Fase 1 (PK 17.2-17.6%, Ca 3.25-4.00%, EM 2750-2900) | **Optimal** | **Rp6.225,89** | Jagung 60,00%, SBM 26,08%, Tepung Batu 8,30%, Dedak 4,69%, Minyak 0,92% | **100% Sesuai** |
| **Skenario 2** | **Fase 1 - Pembatasan SBM 25%** | Batas maksimal SBM diturunkan dari 30% menjadi 25% | **Optimal** | **Rp6.236,87** | Jagung 60,00%, SBM 25,00%, Tepung Batu 8,19%, Pollard 4,15%, Dedak 1,39%, Minyak 0,77%, MBM 0,50% | **100% Sesuai** |
| **Skenario 3** | **Fase 1 - Batas SBM 20%** | Batas maksimal SBM ditekan ekstrem menjadi 20% | **Infeasible** | **-** | Tidak ada kombinasi bahan aktif yang mampu memenuhi ambang batas minimum Protein Kasar (PK $\ge$ 17.20%) | **100% Valid (Terdeteksi Infeasible)** |
| **Skenario 4** | **Fase 2 - Baseline Normal** | 9 Bahan Baku Default Aktif, Standar Fase 2 (PK 16.4-16.9%, Ca 3.60-4.00%, EM 2750-2900) | **Optimal** | **Rp6.171,54** | Jagung 60,00%, SBM 23,84%, Tepung Batu 9,86%, Pollard 5,01%, Minyak 1,29% | **100% Sesuai** |
| **Skenario 5** | **Fase 2 - Jagung Naik Rp6.800** | Harga Jagung Kuning disimulasikan naik dari Rp6.000 menjadi Rp6.800/kg | **Optimal** | **Rp6.651,54** | Jagung 60,00%, SBM 23,84%, Tepung Batu 9,86%, Pollard 5,01%, Minyak 1,29% (Biaya naik tepat +Rp480/kg) | **100% Sesuai** |
| **Skenario 6** | **Fase 2 - Batas Batu 8%** | Batas maksimal Tepung Batu diturunkan dari 10% menjadi 8% | **Infeasible** | **-** | Tidak ada kombinasi yang mampu memenuhi batas minimum Kalsium (Ca $\ge$ 3.60%) pada ransum Fase 2 | **100% Valid (Terdeteksi Infeasible)** |

### 10.2 Matriks Black Box Testing (12 Skenario Pengujian Fungsional Antarmuka)
Pengujian *Black Box* dilakukan terhadap seluruh komponen antarmuka sistem, operasi basis data, akurasi komputasi solver, dan penanganan validasi guna membuktikan seluruh fungsi perangkat lunak 100% beroperasi sesuai spesifikasi:

| No. | Aspek Pengujian | Skenario Uji | Hasil yang Diharapkan | Hasil Pengujian (Pengamatan Riil Antarmuka) | Status |
|:---:|---|---|---|---|:---:|
| **1** | **Manajemen Basis Data** | Menginput data bahan baku baru lengkap dengan 7 parameter nutrisi dan batas pemakaian | Data berhasil tersimpan ke tabel MySQL `master_bahan` secara permanen | Data bahan baru terverifikasi masuk ke database MySQL dan langsung terdaftar pada katalog bahan | **Berhasil** |
| **2** | **Manajemen Basis Data** | Memperbarui harga pasar bahan baku dan menekan tombol simpan perubahan | Harga baru terbarui pada database MySQL dan digunakan pada kalkulasi berikutnya | Perubahan harga tersimpan di MySQL dan langsung memengaruhi koefisien fungsi tujuan $c$ solver | **Berhasil** |
| **3** | **Manajemen Basis Data** | Menghapus bahan baku yang tidak lagi digunakan di peternakan | Data bahan terhapus permanen dari basis data dan daftar tabel | Record bahan baku terhapus dari MySQL dan otomatis hilang dari tabel tampilan antarmuka | **Berhasil** |
| **4** | **Manajemen Basis Data** | Menyimpan hasil perhitungan formulasi ke riwayat formulasi | Riwayat formulasi tersimpan ke tabel `riwayat_formulasi` lengkap dengan waktu eksekusi | Data formulasi tersimpan dalam format JSON valid dan tampil pada halaman riwayat lengkap dengan timestamp | **Berhasil** |
| **5** | **Akurasi Solver** | Memilih Fase 1 dan menekan tombol optimasi formulasi pakan | Solver menghasilkan komposisi bahan optimal dengan total proporsi tepat 100% | Solusi optimal ditemukan (Rp6.225,89/kg), total akumulasi bahan tepat 100,00%, dan seluruh nutrisi terpenuhi | **Berhasil** |
| **6** | **Akurasi Solver** | Memilih Fase 2 dan menekan tombol optimasi formulasi pakan | Solver menghitung ulang formulasi sesuai matriks kendala nutrisi Fase 2 | Formulasi berhasil dihitung ulang (Rp6.171,54/kg) sesuai standar nutrisi Fase 2 (Kalsium $\ge 3.60\%$) | **Berhasil** |
| **7** | **Antarmuka & Seleksi** | Menonaktifkan checkbox bahan baku tertentu (misal: bahan hewani MBM/tepung ikan) | Solver hanya memproses bahan yang dicentang aktif tanpa melibatkan bahan non-aktif | Bahan non-aktif dikecualikan dari matriks keputusan LP dan proporsinya bernilai 0% | **Berhasil** |
| **8** | **Antarmuka & Seleksi** | Mengubah target kuantitas racikan (misal: 250 kg atau 500 kg) | Sistem menghitung berat riil tiap bahan dan total biaya secara proporsional | Tabel komposisi mengalikan proporsi dengan target bobot secara skalar dan menghitung subtotal biaya akurat | **Berhasil** |
| **9** | **Kesesuaian Tampilan** | Mengevaluasi tabel capaian nutrisi ransum | Tabel menampilkan perbandingan nutrisi terhadap standar dan status 'Memenuhi Standar' | Seluruh parameter nutrisi menampilkan angka kadar campuran, rentang acuan, dan badge status hijau 'Memenuhi Standar' | **Berhasil** |
| **10** | **Penanganan Validasi** | Memasukkan nilai harga beli atau nutrisi bernilai negatif pada form | Sistem menolak masukan dan menampilkan peringatan nilai tidak valid | Sistem memblokir eksekusi solver dan menampilkan pesan peringatan data tidak boleh bernilai negatif | **Berhasil** |
| **11** | **Penanganan Validasi** | Memilih kurang dari dua bahan baku aktif pada proses optimasi | Sistem menampilkan notifikasi bahwa jumlah bahan tidak mencukupi untuk diformulasikan | Muncul pesan peringatan antarmuka: *"Pilih minimal 2 bahan baku aktif"* dan eksekusi solver dicegat | **Berhasil** |
| **12** | **Penanganan Validasi** | Menyeleksi kombinasi bahan yang mustahil memenuhi nutrisi (kondisi infeasible) | Sistem menampilkan peringatan infeasible dan saran penambahan bahan tanpa crash | Antarmuka menampilkan panel peringatan infeasible beserta 3 rekomendasi solutif secara elegan tanpa crash | **Berhasil** |

---

## 11. Kesimpulan Dokumen
Dokumen PRD dan ERD ini merepresentasikan rancangan menyeluruh dari **Sistem Pendukung Keputusan Formulasi Pakan Ayam Petelur**. Dengan perpaduan model optimasi *Linear Programming* (SciPy HiGHS) yang teruji secara matematis dan skema basis data relasional ternormalisasi, sistem ini siap digunakan sebagai instrumen penelitian ilmiah maupun alat bantu komersial bagi peternak ayam petelur.
