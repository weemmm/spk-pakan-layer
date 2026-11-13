# PANDUAN DEPLOYMENT PRODUCTION (AIVEN MYSQL & STREAMLIT CLOUD)
## Sistem Pendukung Keputusan (SPK) Formulasi Pakan Ransum Ayam Petelur

Dokumen ini berisi panduan langkah-demi-langkah untuk mempublikasikan sistem ke lingkungan **Production Cloud** agar dapat diakses secara publik oleh peternak, peneliti, dan responden pengujian **System Usability Scale (SUS)**.

---

### ARSITEKTUR CLOUD PRODUCTION

```
+------------------------------------+        SSL / TLS Encrypted Connection
|   STREAMLIT COMMUNITY CLOUD        | --------------------------------------------+
|   (Front-End & Application Host)   |                                             |
|   - URL Publik: https://....app    |                                             v
|   - Konfigurasi via st.secrets     |                                +----------------------------+
+------------------------------------+                                |    AIVEN MANAGED MYSQL     |
                                                                      |    (Cloud Database Server) |
                                                                      |    - Host: mysql-...aiven. |
                                                                      |    - Port: 1xxxx-2xxxx     |
+------------------------------------+                                |    - User: avnadmin        |
|   RESPONDEN / PETERNAK             |                                |    - DB: defaultdb         |
|   (Uji Kuesioner SUS via Browser)  | -----------------------------> +----------------------------+
+------------------------------------+
```

---

### LANGKAH 1: SETUP DATABASE AIVEN MYSQL (CLOUD)

1. Buka situs [Aiven Console](https://console.aiven.io/) dan buat akun (bisa login menggunakan akun Google/GitHub).
2. Setelah masuk ke halaman Dashboard, klik tombol **"Create Service"**.
3. Pilih layanan: **MySQL**.
4. Pilih Cloud Provider & Region:
   - Rekomendasi: **Google Cloud Platform (GCP)** atau **AWS**.
   - Region: Pilih lokasi terdekat (misal: **Singapore / `asia-southeast1`** atau **Jakarta / `asia-southeast2`** jika tersedia) untuk meminimalkan latensi.
5. Pilih Service Plan: Pilih opsi **Free Tier** (tersedia gratis dengan RAM dan storage yang cukup untuk pengujian skripsi).
6. Masukkan nama service (contoh: `mysql-spk-pakan`) lalu klik **"Create Service"**.
7. Tunggu status service berubah dari *REBUILDING* menjadi **RUNNING** (berwarna hijau).
8. Pada tab **Overview**, catat informasi koneksi berikut:
   - **Host** : `mysql-xxxxx-xxxx.aivencloud.com`
   - **Port** : Angka port unik (misal `12345` atau `25060`)
   - **User** : `avnadmin`
   - **Password** : Klik ikon mata untuk melihat dan menyalin password
   - **Database Name** : Secara default bernama `defaultdb` (dapat langsung digunakan).

---

### LANGKAH 2: UJI KONEKSI & INISIALISASI OTOMATIS DATASET

Sistem telah dilengkapi skrip otomatis `test_aiven_connection.py`. Anda dapat menguji kredensial Aiven sekaligus mengisi seluruh tabel dan master data secara otomatis dari komputer lokal sebelum melakukan deploy:

1. Buka file `.env` di komputer Anda, lalu ganti dengan kredensial Aiven yang baru dicatat:
   ```env
   DB_HOST=mysql-xxxxx-xxxx.aivencloud.com
   DB_PORT=25060
   DB_USER=avnadmin
   DB_PASSWORD=password_dari_aiven
   DB_NAME=defaultdb
   DB_SSL_DISABLED=false
   ```
2. Jalankan skrip verifikasi pada terminal PowerShell:
   ```powershell
   python test_aiven_connection.py
   ```
3. Skrip ini akan secara otomatis:
   - Menguji handshake jaringan dan enkripsi SSL ke Aiven.
   - Membuat tabel `nutrisi_acuan`, `bahan_pakan`, dan `riwayat_optimasi`.
   - Membuat view alias `master_bahan` dan `riwayat_formulasi`.
   - Mengisi 9 data master bahan pakan dan standar nutrisi Fase 1 & 2.
4. Jika output menampilkan tanda centang hijau (`✅ STATUS: BERHASIL TERHUBUNG!`), database cloud Anda telah siap 100%.

---

### LANGKAH 3: PUSH KODE PROGRAM KE GITHUB

Streamlit Community Cloud melakukan deployment langsung dari repositori GitHub.

1. Buka terminal di folder project ini:
   ```powershell
   # Inisialisasi git jika belum ada
   git init

   # Pastikan file .env dan virtual environment tidak ter-push (sudah dilindungi oleh .gitignore)
   git status

   # Tambahkan semua file proyek
   git add .

   # Buat commit perdana
   git commit -m "feat: SPK Formulasi Pakan Layer Production Ready for SUS Testing"
   ```

2. Buka akun [GitHub](https://github.com/) Anda dan buat repositori baru:
   - Repository Name: misal `spk-formulasi-pakan-layer`
   - Visibility: **Public** (agar gratis di Streamlit Cloud) atau **Private**.
   - *Jangan centang "Add a README file" atau .gitignore* (karena sudah ada di lokal).

3. Hubungkan repositori lokal ke GitHub dan lakukan push:
   ```powershell
   git branch -M main
   git remote add origin https://github.com/USERNAME_GITHUB_ANDA/spk-formulasi-pakan-layer.git
   git push -u origin main
   ```

---

### LANGKAH 4: DEPLOYMENT KE STREAMLIT COMMUNITY CLOUD

1. Kunjungi [Streamlit Community Cloud](https://share.streamlit.io/) dan login menggunakan akun GitHub Anda.
2. Klik tombol **"New app"** (atau "Create app").
3. Isi parameter aplikasi:
   - **Repository** : Pilih `USERNAME/spk-formulasi-pakan-layer`
   - **Branch**     : `main`
   - **Main file path** : `app.py`
   - **App URL** (Opsional) : Tentukan custom subdomain (contoh: `spk-pakan-layer-uad.streamlit.app`)
4. Klik tombol **"Advanced settings..."** sebelum menekan tombol deploy.
5. Pada tab **Secrets**, salin dan tempel format konfigurasi berikut (sesuaikan dengan akun Aiven Anda):
   ```toml
   [mysql]
   host = "mysql-xxxxx-xxxx.aivencloud.com"
   port = 25060
   user = "avnadmin"
   password = "password_aiven_anda"
   database = "defaultdb"
   ssl_disabled = false
   ```
6. Klik **"Save"**, lalu klik **"Deploy!"**.
7. Tunggu proses instalasi dependensi Python (`scipy`, `pandas`, `mysql-connector-python`, dll.) selama 1–2 menit hingga aplikasi aktif di browser.

---

### LANGKAH 5: VERIFIKASI AKHIR & PERSIAPAN UJI SUS

Setelah aplikasi tayang (*live*):
1. **Periksa Indikator Database**: Pada sidebar aplikasi di browser, pastikan badge berwarna hijau menampilkan:
   `[Database] MySQL Aktif`
2. **Uji Simulasi Sederhana**:
   - Pilih *Fase 1*.
   - Tekan tombol *Jalankan Optimasi Ransum (SciPy HiGHS)*.
   - Pastikan biaya terhitung **Rp6.225,89/kg**, grafik donut muncul, dan data berhasil disimpan ke riwayat.
3. **Bagikan URL ke Responden Pengujian SUS**:
   - Salin tautan publik aplikasi (misal: `https://spk-pakan-layer-uad.streamlit.app`).
   - Sertakan panduan singkat skenario tugas uji coba (misal: *"1. Pilih fase pakan, 2. Coba ubah harga jagung, 3. Klik hitung ransum, 4. Simpan riwayat"*).
   - Bagikan form kuesioner System Usability Scale (10 butir pertanyaan skala Likert 1–5 standar Brooke, 1996) kepada peternak dan praktisi pakan.

