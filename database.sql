-- ==========================================================
-- Database Schema: Sistem Pendukung Keputusan (SPK)
-- Formulasi Pakan Ayam Petelur (Least Cost Feed Formulation)
-- Berbasis Linear Programming (SciPy HiGHS)
-- ==========================================================

CREATE DATABASE IF NOT EXISTS `spk_pakan_layer` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `spk_pakan_layer`;

-- 1. Tabel Standar Kebutuhan Nutrisi Acuan
DROP TABLE IF EXISTS `riwayat_optimasi`;
DROP TABLE IF EXISTS `bahan_pakan`;
DROP TABLE IF EXISTS `nutrisi_acuan`;

CREATE TABLE `nutrisi_acuan` (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Seed Data Nutrisi Acuan (Fase 1 dan Fase 2 Ayam Petelur)
INSERT INTO `nutrisi_acuan` 
(`id`, `nama_fase`, `deskripsi`, `pk_min`, `pk_max`, `lk_min`, `lk_max`, `sk_min`, `sk_max`, `abu_min`, `abu_max`, `ca_min`, `ca_max`, `p_min`, `p_max`, `em_min`, `em_max`) 
VALUES
(1, 'Fase 1', '2% - 28 minggu (Layer Fase Awal)', 17.20, 17.60, 2.50, 7.00, 0.00, 7.00, 10.00, 14.00, 3.25, 4.00, 0.37, 0.41, 2750.00, 2900.00),
(2, 'Fase 2', '28 minggu - afkir (Layer Fase Puncak/Akhir)', 16.40, 16.90, 2.50, 7.00, 0.00, 7.00, 10.00, 14.00, 3.60, 4.00, 0.33, 0.37, 2750.00, 2900.00);


-- 2. Tabel Master Bahan Pakan Lokal
CREATE TABLE `bahan_pakan` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `kode_bahan` VARCHAR(20) NOT NULL UNIQUE,
    `nama_bahan` VARCHAR(100) NOT NULL,
    `kategori` VARCHAR(50) DEFAULT 'Bahan Baku Lokal',
    `pk` DECIMAL(5,2) NOT NULL COMMENT 'Protein Kasar (%)',
    `lk` DECIMAL(5,2) NOT NULL COMMENT 'Lemak Kasar (%)',
    `sk` DECIMAL(5,2) NOT NULL COMMENT 'Serat Kasar (%)',
    `abu` DECIMAL(5,2) NOT NULL COMMENT 'Abu (%)',
    `ca` DECIMAL(5,2) NOT NULL COMMENT 'Kalsium (%)',
    `p` DECIMAL(5,2) NOT NULL COMMENT 'Fosfor (%)',
    `em` DECIMAL(7,2) NOT NULL COMMENT 'Energi Metabolis (Kkal/kg)',
    `harga_per_kg` DECIMAL(10,2) NOT NULL COMMENT 'Harga Beli (Rp/kg)',
    `batas_min_layer` DECIMAL(5,2) NOT NULL DEFAULT 0.00 COMMENT 'Batas Min Penggunaan (%)',
    `batas_maks_layer` DECIMAL(5,2) NOT NULL COMMENT 'Batas Maksimal Penggunaan (%)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Seed Data 9 Bahan Pakan Lokal Unggas Layer
INSERT INTO `bahan_pakan` 
(`id`, `kode_bahan`, `nama_bahan`, `kategori`, `pk`, `lk`, `sk`, `abu`, `ca`, `p`, `em`, `harga_per_kg`, `batas_min_layer`, `batas_maks_layer`) 
VALUES
(1, 'JAGUNG', 'Jagung Kuning', 'Sumber Energi', 8.60, 3.80, 2.20, 1.50, 0.02, 0.28, 3350.00, 6000.00, 0.00, 60.00),
(2, 'DEDAK', 'Dedak Padi', 'Sumber Energi/Serat', 12.00, 8.00, 11.00, 10.50, 0.10, 1.40, 1630.00, 3800.00, 0.00, 20.00),
(3, 'POLLARD', 'Pollard Gandum', 'Sumber Energi/Serat', 15.00, 4.00, 7.00, 5.00, 0.12, 0.90, 1900.00, 4800.00, 0.00, 20.00),
(4, 'MINYAK', 'Minyak Nabati / Sawit', 'Sumber Energi Murni', 0.00, 99.00, 0.00, 0.00, 0.00, 0.00, 8600.00, 16000.00, 0.00, 4.00),
(5, 'SBM', 'Bungkil Kedelai (SBM)', 'Sumber Protein Nabati', 44.00, 1.50, 6.00, 6.50, 0.30, 0.65, 2240.00, 8500.00, 0.00, 30.00),
(6, 'IKAN', 'Tepung Ikan', 'Sumber Protein Hewani', 55.00, 6.00, 1.50, 22.00, 5.50, 3.00, 2800.00, 15000.00, 0.00, 8.00),
(7, 'MBM', 'Meat and Bone Meal (MBM)', 'Sumber Protein/Mineral Hewani', 50.00, 10.00, 2.50, 28.00, 8.50, 4.20, 2500.00, 11000.00, 0.00, 8.00),
(8, 'BATU', 'Tepung Batu (CaCO3 / Grit)', 'Sumber Kalsium', 0.00, 0.00, 0.00, 95.00, 38.00, 0.02, 0.00, 1000.00, 0.00, 10.00),
(9, 'DCP', 'DCP (Dicalcium Phosphate)', 'Sumber Kalsium & Fosfor', 0.00, 0.00, 0.00, 80.00, 24.00, 18.00, 0.00, 12000.00, 0.00, 2.50);


-- 3. Tabel Riwayat Optimasi
CREATE TABLE `riwayat_optimasi` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `tanggal` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `fase_id` INT NOT NULL,
    `nama_fase` VARCHAR(50) NOT NULL,
    `total_biaya_per_kg` DECIMAL(10,2) NOT NULL,
    `status_solver` VARCHAR(50) NOT NULL,
    `detail_komposisi` JSON NOT NULL COMMENT 'JSON array persentase dan bobot tiap bahan',
    `detail_nutrisi` JSON NOT NULL COMMENT 'JSON perbandingan nutrisi target vs capaian',
    `catatan` TEXT,
    CONSTRAINT `fk_riwayat_fase` FOREIGN KEY (`fase_id`) REFERENCES `nutrisi_acuan` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
