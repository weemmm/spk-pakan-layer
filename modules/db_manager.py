import json
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
from mysql.connector import Error
from config.db_connection import get_db_connection

# ==============================================================================
# DATA DEFAULT STANDAR NUTRISI ACUAN & MASTER BAHAN BAKU (SESUAI SKRIPSI)
# ==============================================================================

DEFAULT_NUTRISI_ACUAN = [
    {
        "id": 1,
        "nama_fase": "Fase 1",
        "deskripsi": "2% - 28 minggu (Layer Fase Awal)",
        "pk_min": 17.20, "pk_max": 17.60,
        "lk_min": 2.50,  "lk_max": 7.00,
        "sk_min": 0.00,  "sk_max": 7.00,
        "abu_min": 10.00,"abu_max": 14.00,
        "ca_min": 3.25,  "ca_max": 4.00,
        "p_min": 0.37,   "p_max": 0.41,
        "em_min": 2750.00,"em_max": 2900.00
    },
    {
        "id": 2,
        "nama_fase": "Fase 2",
        "deskripsi": "28 minggu - afkir (Layer Fase Puncak/Akhir)",
        "pk_min": 16.40, "pk_max": 16.90,
        "lk_min": 2.50,  "lk_max": 7.00,
        "sk_min": 0.00,  "sk_max": 7.00,
        "abu_min": 10.00,"abu_max": 14.00,
        "ca_min": 3.60,  "ca_max": 4.00,
        "p_min": 0.33,   "p_max": 0.37,
        "em_min": 2750.00,"em_max": 2900.00
    }
]

DEFAULT_BAHAN_PAKAN = [
    {"id": 1, "kode_bahan": "JAGUNG",  "nama_bahan": "Jagung Kuning",             "kategori": "Sumber Energi",             "pk": 8.60,  "lk": 3.80,  "sk": 2.20,  "abu": 1.50,  "ca": 0.02, "p": 0.28, "em": 3350.0, "harga_per_kg": 6000.0,  "batas_min_layer": 0.0, "batas_maks_layer": 60.0},
    {"id": 2, "kode_bahan": "DEDAK",   "nama_bahan": "Dedak Padi",                "kategori": "Sumber Energi/Serat",       "pk": 12.00, "lk": 8.00,  "sk": 11.00, "abu": 10.50, "ca": 0.10, "p": 1.40, "em": 1630.0, "harga_per_kg": 3800.0,  "batas_min_layer": 0.0, "batas_maks_layer": 20.0},
    {"id": 3, "kode_bahan": "POLLARD", "nama_bahan": "Pollard Gandum",            "kategori": "Sumber Energi/Serat",       "pk": 15.00, "lk": 4.00,  "sk": 7.00,  "abu": 5.00,  "ca": 0.12, "p": 0.90, "em": 1900.0, "harga_per_kg": 4800.0,  "batas_min_layer": 0.0, "batas_maks_layer": 20.0},
    {"id": 4, "kode_bahan": "MINYAK",  "nama_bahan": "Minyak Nabati / Sawit",     "kategori": "Sumber Energi Murni",       "pk": 0.00,  "lk": 99.00, "sk": 0.00,  "abu": 0.00,  "ca": 0.00, "p": 0.00, "em": 8600.0, "harga_per_kg": 16000.0, "batas_min_layer": 0.0, "batas_maks_layer": 4.0},
    {"id": 5, "kode_bahan": "SBM",     "nama_bahan": "Bungkil Kedelai (SBM)",     "kategori": "Sumber Protein Nabati",     "pk": 44.00, "lk": 1.50,  "sk": 6.00,  "abu": 6.50,  "ca": 0.30, "p": 0.65, "em": 2240.0, "harga_per_kg": 8500.0,  "batas_min_layer": 0.0, "batas_maks_layer": 30.0},
    {"id": 6, "kode_bahan": "IKAN",    "nama_bahan": "Tepung Ikan",               "kategori": "Sumber Protein Hewani",     "pk": 55.00, "lk": 6.00,  "sk": 1.50,  "abu": 22.00, "ca": 5.50, "p": 3.00, "em": 2800.0, "harga_per_kg": 15000.0, "batas_min_layer": 0.0, "batas_maks_layer": 8.0},
    {"id": 7, "kode_bahan": "MBM",     "nama_bahan": "Meat and Bone Meal (MBM)",  "kategori": "Sumber Protein/Mineral Hewani", "pk": 50.00, "lk": 10.00, "sk": 2.50,  "abu": 28.00, "ca": 8.50, "p": 4.20, "em": 2500.0, "harga_per_kg": 11000.0, "batas_min_layer": 0.0, "batas_maks_layer": 8.0},
    {"id": 8, "kode_bahan": "BATU",    "nama_bahan": "Tepung Batu (CaCO3 / Grit)","kategori": "Sumber Kalsium",             "pk": 0.00,  "lk": 0.00,  "sk": 0.00,  "abu": 95.00, "ca": 38.00,"p": 0.02, "em": 0.0,    "harga_per_kg": 1000.0,  "batas_min_layer": 0.0, "batas_maks_layer": 10.0},
    {"id": 9, "kode_bahan": "DCP",     "nama_bahan": "DCP (Dicalcium Phosphate)", "kategori": "Sumber Kalsium & Fosfor",    "pk": 0.00,  "lk": 0.00,  "sk": 0.00,  "abu": 80.00, "ca": 24.00,"p": 18.00,"em": 0.0,    "harga_per_kg": 12000.0, "batas_min_layer": 0.0, "batas_maks_layer": 2.5}
]


# ==============================================================================
# INISIALISASI TABEL BASIS DATA MYSQL MURNI
# ==============================================================================

def init_database_tables():
    """
    Memastikan struktur tabel dan view di database MySQL tersedia sesuai Kamus Data PRD Bagian 9.
    Menyisipkan data awal secara otomatis jika tabel masih kosong.
    """
    conn = get_db_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()

        # 1. Tabel nutrisi_acuan
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS `nutrisi_acuan` (
                `id` INT AUTO_INCREMENT PRIMARY KEY,
                `nama_fase` VARCHAR(50) NOT NULL,
                `deskripsi` VARCHAR(150),
                `pk_min` DECIMAL(5,2) NOT NULL COMMENT 'Protein Kasar Min (%)',
                `pk_max` DECIMAL(5,2) NOT NULL COMMENT 'Protein Kasar Max (%)',
                `lk_min` DECIMAL(5,2) NOT NULL COMMENT 'Lemak Kasar Min (%)',
                `lk_max` DECIMAL(5,2) NOT NULL COMMENT 'Lemak Kasar Max (%)',
                `sk_min` DECIMAL(5,2) NOT NULL DEFAULT 0.00 COMMENT 'Serat Kasar Min (%)',
                `sk_max` DECIMAL(5,2) NOT NULL COMMENT 'Serat Kasar Max (%)',
                `abu_min` DECIMAL(5,2) NOT NULL COMMENT 'Abu Min (%)',
                `abu_max` DECIMAL(5,2) NOT NULL COMMENT 'Abu Max (%)',
                `ca_min` DECIMAL(5,2) NOT NULL COMMENT 'Kalsium Min (%)',
                `ca_max` DECIMAL(5,2) NOT NULL COMMENT 'Kalsium Max (%)',
                `p_min` DECIMAL(5,2) NOT NULL COMMENT 'Fosfor Tersedia Min (%)',
                `p_max` DECIMAL(5,2) NOT NULL COMMENT 'Fosfor Tersedia Max (%)',
                `em_min` DECIMAL(7,2) NOT NULL COMMENT 'Energi Metabolis Min (Kkal/kg)',
                `em_max` DECIMAL(7,2) NOT NULL DEFAULT 2900.00 COMMENT 'Batas maksimal Energi Metabolis (Kkal/kg)'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)

        # Pastikan kolom em_max bertipe NOT NULL DEFAULT 2900.00
        try:
            cursor.execute("""
                ALTER TABLE `nutrisi_acuan` 
                MODIFY COLUMN `em_max` DECIMAL(7,2) NOT NULL DEFAULT 2900.00 COMMENT 'Batas maksimal Energi Metabolis (Kkal/kg)'
            """)
        except Exception:
            pass

        # 2. Tabel bahan_pakan
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS `bahan_pakan` (
                `id` INT AUTO_INCREMENT PRIMARY KEY,
                `kode_bahan` VARCHAR(20) NOT NULL UNIQUE,
                `nama_bahan` VARCHAR(100) NOT NULL,
                `kategori` VARCHAR(50) DEFAULT 'Bahan Baku Lokal',
                `pk` DECIMAL(5,2) NOT NULL DEFAULT 0.00 COMMENT 'Protein Kasar (%)',
                `lk` DECIMAL(5,2) NOT NULL DEFAULT 0.00 COMMENT 'Lemak Kasar (%)',
                `sk` DECIMAL(5,2) NOT NULL DEFAULT 0.00 COMMENT 'Serat Kasar (%)',
                `abu` DECIMAL(5,2) NOT NULL DEFAULT 0.00 COMMENT 'Abu (%)',
                `ca` DECIMAL(5,2) NOT NULL DEFAULT 0.00 COMMENT 'Kalsium (%)',
                `p` DECIMAL(5,2) NOT NULL DEFAULT 0.00 COMMENT 'Fosfor (%)',
                `em` DECIMAL(7,2) NOT NULL DEFAULT 0.00 COMMENT 'Energi Metabolis (Kkal/kg)',
                `harga_per_kg` DECIMAL(10,2) NOT NULL COMMENT 'Harga Beli (Rp/kg)',
                `batas_min_layer` DECIMAL(5,2) NOT NULL DEFAULT 0.00 COMMENT 'Batas Min Penggunaan (%)',
                `batas_maks_layer` DECIMAL(5,2) NOT NULL DEFAULT 100.00 COMMENT 'Batas Maksimal Penggunaan (%)'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)

        # 3. Tabel riwayat_optimasi
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS `riwayat_optimasi` (
                `id` INT AUTO_INCREMENT PRIMARY KEY,
                `tanggal` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `fase_id` INT NOT NULL,
                `nama_fase` VARCHAR(50) NOT NULL,
                `total_biaya_per_kg` DECIMAL(10,2) NOT NULL,
                `status_solver` VARCHAR(50) NOT NULL,
                `detail_komposisi` JSON NOT NULL COMMENT 'JSON array proporsi dan bobot per bahan',
                `detail_nutrisi` JSON NOT NULL COMMENT 'JSON perbandingan nutrisi target vs capaian',
                `catatan` TEXT,
                CONSTRAINT `fk_riwayat_fase` FOREIGN KEY (`fase_id`) REFERENCES `nutrisi_acuan` (`id`) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)

        # 4. View riwayat_formulasi & master_bahan (alias tabel resmi skripsi)
        cursor.execute("""
            CREATE OR REPLACE VIEW `riwayat_formulasi` AS 
            SELECT * FROM `riwayat_optimasi`;
        """)
        cursor.execute("""
            CREATE OR REPLACE VIEW `master_bahan` AS 
            SELECT * FROM `bahan_pakan`;
        """)

        # Cek dan isi data awal nutrisi_acuan jika kosong
        cursor.execute("SELECT COUNT(*) FROM `nutrisi_acuan`")
        if cursor.fetchone()[0] == 0:
            for f in DEFAULT_NUTRISI_ACUAN:
                cursor.execute("""
                    INSERT INTO `nutrisi_acuan` 
                    (id, nama_fase, deskripsi, pk_min, pk_max, lk_min, lk_max, sk_min, sk_max, abu_min, abu_max, ca_min, ca_max, p_min, p_max, em_min, em_max)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    f["id"], f["nama_fase"], f["deskripsi"],
                    f["pk_min"], f["pk_max"], f["lk_min"], f["lk_max"],
                    f["sk_min"], f["sk_max"], f["abu_min"], f["abu_max"],
                    f["ca_min"], f["ca_max"], f["p_min"], f["p_max"],
                    f["em_min"], f["em_max"]
                ))

        # Cek dan isi data awal bahan_pakan jika kosong
        cursor.execute("SELECT COUNT(*) FROM `bahan_pakan`")
        if cursor.fetchone()[0] == 0:
            for b in DEFAULT_BAHAN_PAKAN:
                cursor.execute("""
                    INSERT INTO `bahan_pakan` 
                    (id, kode_bahan, nama_bahan, kategori, pk, lk, sk, abu, ca, p, em, harga_per_kg, batas_min_layer, batas_maks_layer)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    b["id"], b["kode_bahan"], b["nama_bahan"], b["kategori"],
                    b["pk"], b["lk"], b["sk"], b["abu"], b["ca"], b["p"], b["em"],
                    b["harga_per_kg"], b["batas_min_layer"], b["batas_maks_layer"]
                ))

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


# Jalankan inisialisasi tabel MySQL saat modul pertama kali diimpor
init_database_tables()


# ==============================================================================
# OPERASI CRUD BAHAN PAKAN (READ, INSERT, UPDATE, DELETE) - MYSQL MURNI
# ==============================================================================

def get_bahan_pakan() -> pd.DataFrame:
    """
    Mengambil data seluruh bahan baku pakan dari database MySQL.
    Jika koneksi MySQL tidak tersedia, mengembalikan DataFrame data default agar aplikasi tidak crash.
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM bahan_pakan ORDER BY id ASC")
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            if rows:
                return pd.DataFrame(rows)
            else:
                # Jika tabel kosong, inisialisasi ulang
                init_database_tables()
                return pd.DataFrame(DEFAULT_BAHAN_PAKAN)
        except Exception:
            try:
                conn.close()
            except Exception:
                pass

    return pd.DataFrame(DEFAULT_BAHAN_PAKAN)


def tambah_bahan_pakan(
    kode_bahan: str,
    nama_bahan: str,
    kategori: str,
    harga_per_kg: float,
    batas_maks_layer: float,
    pk: float,
    lk: float,
    sk: float,
    abu: float,
    ca: float,
    p: float,
    em: float,
    batas_min_layer: float = 0.0
) -> Tuple[bool, str]:
    """
    Menambahkan bahan baku baru ke database MySQL dengan validasi data non-negatif.
    """
    numeric_vals = [harga_per_kg, batas_maks_layer, pk, lk, sk, abu, ca, p, em, batas_min_layer]
    if any(float(v) < 0 for v in numeric_vals):
        return False, "Nilai harga, batas, dan nutrisi tidak boleh bernilai negatif."

    if not nama_bahan.strip():
        return False, "Nama bahan baku tidak boleh kosong."

    kode = kode_bahan.strip().upper() if kode_bahan.strip() else nama_bahan[:6].strip().upper()

    conn = get_db_connection()
    if not conn:
        return False, "Gagal menambahkan bahan baku: Koneksi ke MySQL Server terputus."

    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO bahan_pakan 
            (kode_bahan, nama_bahan, kategori, pk, lk, sk, abu, ca, p, em, harga_per_kg, batas_min_layer, batas_maks_layer)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            kode, nama_bahan.strip(), kategori.strip(),
            float(pk), float(lk), float(sk), float(abu), float(ca), float(p), float(em),
            float(harga_per_kg), float(batas_min_layer), float(batas_maks_layer)
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return True, f"Bahan baku '{nama_bahan}' berhasil ditambahkan ke database MySQL."
    except Exception as e:
        try:
            conn.close()
        except Exception:
            pass
        return False, f"Gagal menambahkan bahan baku ke MySQL: {str(e)}"


def update_bahan_pakan(
    bahan_id: int,
    nama_bahan: str,
    kategori: str,
    harga_per_kg: float,
    batas_maks_layer: float,
    pk: float,
    lk: float,
    sk: float,
    abu: float,
    ca: float,
    p: float,
    em: float,
    batas_min_layer: float = 0.0
) -> Tuple[bool, str]:
    """
    Memperbarui data bahan baku di MySQL berdasarkan ID bahan.
    """
    numeric_vals = [harga_per_kg, batas_maks_layer, pk, lk, sk, abu, ca, p, em, batas_min_layer]
    if any(float(v) < 0 for v in numeric_vals):
        return False, "Nilai harga, batas, dan nutrisi tidak boleh bernilai negatif."

    conn = get_db_connection()
    if not conn:
        return False, "Gagal memperbarui data: Koneksi ke MySQL Server terputus."

    try:
        cursor = conn.cursor()
        query = """
            UPDATE bahan_pakan SET
                nama_bahan = %s, kategori = %s, harga_per_kg = %s, batas_maks_layer = %s,
                pk = %s, lk = %s, sk = %s, abu = %s, ca = %s, p = %s, em = %s, batas_min_layer = %s
            WHERE id = %s
        """
        cursor.execute(query, (
            nama_bahan, kategori, float(harga_per_kg), float(batas_maks_layer),
            float(pk), float(lk), float(sk), float(abu), float(ca), float(p), float(em),
            float(batas_min_layer), int(bahan_id)
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return True, f"Bahan baku ID {bahan_id} berhasil diperbarui di MySQL."
    except Exception as e:
        try:
            conn.close()
        except Exception:
            pass
        return False, f"Gagal memperbarui data di MySQL: {str(e)}"


def update_batch_bahan_pakan(df_updated: pd.DataFrame) -> Tuple[bool, str]:
    """
    Memperbarui seluruh data bahan pakan secara massal (batch update) ke MySQL.
    """
    conn = get_db_connection()
    if not conn:
        return False, "Gagal menyimpan perubahan: Koneksi ke MySQL Server terputus."

    try:
        cursor = conn.cursor()
        for _, row in df_updated.iterrows():
            query = """
                UPDATE bahan_pakan SET
                    nama_bahan = %s, kategori = %s, harga_per_kg = %s, batas_maks_layer = %s,
                    pk = %s, lk = %s, sk = %s, abu = %s, ca = %s, p = %s, em = %s
                WHERE id = %s
            """
            cursor.execute(query, (
                str(row["nama_bahan"]), str(row.get("kategori", "Bahan Baku Lokal")),
                float(row["harga_per_kg"]), float(row["batas_maks_layer"]),
                float(row["pk"]), float(row["lk"]), float(row["sk"]),
                float(row["abu"]), float(row["ca"]), float(row["p"]), float(row["em"]),
                int(row["id"])
            ))
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Seluruh perubahan data bahan baku berhasil disimpan ke MySQL."
    except Exception as e:
        try:
            conn.close()
        except Exception:
            pass
        return False, f"Gagal menyimpan perubahan batch ke MySQL: {str(e)}"


def hapus_bahan_pakan(bahan_id: int) -> Tuple[bool, str]:
    """
    Menghapus record bahan baku dari tabel bahan_pakan di MySQL.
    """
    conn = get_db_connection()
    if not conn:
        return False, "Gagal menghapus bahan: Koneksi ke MySQL Server terputus."

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM bahan_pakan WHERE id = %s", (int(bahan_id),))
        conn.commit()
        cursor.close()
        conn.close()
        return True, f"Bahan baku dengan ID {bahan_id} berhasil dihapus dari database MySQL."
    except Exception as e:
        try:
            conn.close()
        except Exception:
            pass
        return False, f"Gagal menghapus bahan baku dari MySQL: {str(e)}"


# ==============================================================================
# OPERASI CRUD NUTRISI ACUAN (READ & UPDATE) - MYSQL MURNI
# ==============================================================================

def get_nutrisi_acuan(fase_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Mengambil data standar kebutuhan nutrisi acuan dari MySQL.
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            if fase_id:
                cursor.execute("SELECT * FROM nutrisi_acuan WHERE id = %s", (int(fase_id),))
            else:
                cursor.execute("SELECT * FROM nutrisi_acuan ORDER BY id ASC")
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            if rows:
                return rows
        except Exception:
            try:
                conn.close()
            except Exception:
                pass

    if fase_id:
        return [row for row in DEFAULT_NUTRISI_ACUAN if row["id"] == fase_id]
    return DEFAULT_NUTRISI_ACUAN


def update_nutrisi_acuan(
    fase_id: int,
    pk_min: float,
    pk_max: float,
    lk_min: float,
    lk_max: float,
    sk_max: float,
    abu_min: float,
    abu_max: float,
    ca_min: float,
    ca_max: float,
    p_min: float,
    p_max: float,
    em_min: float,
    em_max: Optional[float] = 2900.0
) -> Tuple[bool, str]:
    """
    Memperbarui standar nutrisi acuan untuk fase tertentu di database MySQL.
    """
    em_max_val = float(em_max) if em_max is not None else 2900.0
    vals = [pk_min, pk_max, lk_min, lk_max, sk_max, abu_min, abu_max, ca_min, ca_max, p_min, p_max, em_min, em_max_val]
    if any(float(v) < 0 for v in vals):
        return False, "Nilai standar nutrisi acuan tidak boleh bernilai negatif."

    if pk_min > pk_max:
        return False, "Protein Kasar (PK) batas minimum tidak boleh lebih besar dari maksimum."
    if lk_min > lk_max:
        return False, "Lemak Kasar (LK) batas minimum tidak boleh lebih besar dari maksimum."
    if ca_min > ca_max:
        return False, "Kalsium (Ca) batas minimum tidak boleh lebih besar dari maksimum."
    if p_min > p_max:
        return False, "Fosfor (P) batas minimum tidak boleh lebih besar dari maksimum."
    if em_min > em_max_val:
        return False, "Energi Metabolis (EM) batas minimum tidak boleh lebih besar dari maksimum."

    conn = get_db_connection()
    if not conn:
        return False, "Gagal memperbarui standar acuan: Koneksi ke MySQL Server terputus."

    try:
        cursor = conn.cursor()
        query = """
            UPDATE nutrisi_acuan SET
                pk_min = %s, pk_max = %s, lk_min = %s, lk_max = %s, sk_max = %s,
                abu_min = %s, abu_max = %s, ca_min = %s, ca_max = %s, p_min = %s,
                p_max = %s, em_min = %s, em_max = %s
            WHERE id = %s
        """
        cursor.execute(query, (
            float(pk_min), float(pk_max), float(lk_min), float(lk_max), float(sk_max),
            float(abu_min), float(abu_max), float(ca_min), float(ca_max), float(p_min),
            float(p_max), float(em_min), em_max_val, int(fase_id)
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return True, f"Standar nutrisi acuan untuk Fase ID {fase_id} berhasil diperbarui di MySQL."
    except Exception as e:
        try:
            conn.close()
        except Exception:
            pass
        return False, f"Gagal memperbarui standar acuan di MySQL: {str(e)}"


# ==============================================================================
# OPERASI RIWAYAT FORMULASI / OPTIMASI - MYSQL MURNI
# ==============================================================================

def simpan_riwayat_optimasi(
    fase_id: int,
    nama_fase: str,
    total_biaya_per_kg: float,
    status_solver: str,
    detail_komposisi: List[Dict[str, Any]],
    detail_nutrisi: List[Dict[str, Any]],
    catatan: str = ""
) -> Tuple[bool, str]:
    """
    Menyimpan hasil perhitungan formulasi ke tabel riwayat_optimasi di database MySQL.
    Menuliskan detail_komposisi dan detail_nutrisi dalam format JSON yang valid.
    """
    try:
        komposisi_json = json.dumps(detail_komposisi, ensure_ascii=False)
        nutrisi_json = json.dumps(detail_nutrisi, ensure_ascii=False)
    except Exception as je:
        return False, f"Serialisasi JSON gagal: {str(je)}"

    conn = get_db_connection()
    if not conn:
        return False, "Gagal menyimpan riwayat: Koneksi ke MySQL Server terputus."

    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO riwayat_optimasi 
            (fase_id, nama_fase, total_biaya_per_kg, status_solver, detail_komposisi, detail_nutrisi, catatan)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            int(fase_id), str(nama_fase), float(total_biaya_per_kg),
            str(status_solver), komposisi_json, nutrisi_json, str(catatan)
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Hasil formulasi berhasil disimpan ke database MySQL."
    except Exception as e:
        try:
            conn.close()
        except Exception:
            pass
        return False, f"Gagal menyimpan riwayat formulasi ke MySQL: {str(e)}"


def get_riwayat_optimasi(limit: int = 30) -> List[Dict[str, Any]]:
    """
    Mengambil daftar riwayat formulasi tersimpan dari database MySQL.
    """
    conn = get_db_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM riwayat_optimasi ORDER BY id DESC LIMIT %s", (int(limit),))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        if rows:
            for r in rows:
                if isinstance(r.get("detail_komposisi"), str):
                    r["detail_komposisi"] = json.loads(r["detail_komposisi"])
                if isinstance(r.get("detail_nutrisi"), str):
                    r["detail_nutrisi"] = json.loads(r["detail_nutrisi"])
            return rows
    except Exception:
        try:
            conn.close()
        except Exception:
            pass

    return []


def hapus_riwayat_optimasi(riwayat_id: int) -> Tuple[bool, str]:
    """
    Menghapus riwayat formulasi dari tabel riwayat_optimasi di MySQL berdasarkan ID.
    """
    conn = get_db_connection()
    if not conn:
        return False, "Gagal menghapus riwayat: Koneksi ke MySQL Server terputus."

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM riwayat_optimasi WHERE id = %s", (int(riwayat_id),))
        conn.commit()
        cursor.close()
        conn.close()
        return True, f"Riwayat formulasi ID {riwayat_id} berhasil dihapus dari database MySQL."
    except Exception as e:
        try:
            conn.close()
        except Exception:
            pass
        return False, f"Gagal menghapus riwayat formulasi: {str(e)}"
