import sys
import os
import unittest
import pandas as pd

# Tambahkan root path ke sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.db_manager import (
    get_nutrisi_acuan,
    get_bahan_pakan,
    tambah_bahan_pakan,
    update_batch_bahan_pakan,
    hapus_bahan_pakan,
    update_nutrisi_acuan,
    simpan_riwayat_optimasi,
    get_riwayat_optimasi,
    hapus_riwayat_optimasi
)
from modules.optimizer import hitung_formulasi_pakan


class TestOptimizer(unittest.TestCase):

    def setUp(self):
        self.df_bahan = get_bahan_pakan()
        self.list_acuan = get_nutrisi_acuan()
        self.fase_1 = next(f for f in self.list_acuan if f["id"] == 1)
        self.fase_2 = next(f for f in self.list_acuan if f["id"] == 2)

    def test_fase_1_least_cost(self):
        """Uji optimasi Fase 1 menghasilkan solusi optimal Rp6.225,89 dan memenuhi total 100%"""
        hasil = hitung_formulasi_pakan(self.df_bahan, self.fase_1)
        self.assertTrue(hasil["success"], f"Optimasi Fase 1 gagal: {hasil.get('status_message')}")
        self.assertAlmostEqual(hasil["total_biaya_per_kg"], 6225.89, places=2)

        # Cek total proporsi harus tepat 100% (toleransi 0.1%)
        total_persen = sum(k["persentase"] for k in hasil["komposisi"])
        self.assertAlmostEqual(total_persen, 100.0, places=1)

        # Cek bahan utama yang terpilih sesuai proposal/skripsi
        komposisi_map = {k["kode_bahan"]: k["persentase"] for k in hasil["komposisi"]}
        self.assertAlmostEqual(komposisi_map.get("JAGUNG", 0.0), 60.00, places=1)
        self.assertAlmostEqual(komposisi_map.get("SBM", 0.0), 26.08, places=1)
        self.assertAlmostEqual(komposisi_map.get("BATU", 0.0), 8.30, places=1)
        self.assertAlmostEqual(komposisi_map.get("DEDAK", 0.0), 4.69, places=1)
        self.assertAlmostEqual(komposisi_map.get("MINYAK", 0.0), 0.92, places=1)

        # Cek bahwa tidak ada bahan yang melebihi batas maksimum
        for k in hasil["komposisi"]:
            self.assertLessEqual(k["persentase"], k["batas_maks"] + 1e-3, f"Bahan {k['nama_bahan']} melebihi batas maks")

        print(f"\n[PASS] Skenario 1 (Fase 1 Baseline) Optimal: Rp {hasil['total_biaya_per_kg']:,.2f}/kg ({hasil['execution_time_ms']} ms)")

    def test_fase_2_least_cost(self):
        """Uji optimasi Fase 2 menghasilkan solusi optimal Rp6.171,54"""
        hasil = hitung_formulasi_pakan(self.df_bahan, self.fase_2)
        self.assertTrue(hasil["success"], f"Optimasi Fase 2 gagal: {hasil.get('status_message')}")
        self.assertAlmostEqual(hasil["total_biaya_per_kg"], 6171.54, places=2)

        total_persen = sum(k["persentase"] for k in hasil["komposisi"])
        self.assertAlmostEqual(total_persen, 100.0, places=1)
        print(f"[PASS] Skenario 4 (Fase 2 Baseline) Optimal: Rp {hasil['total_biaya_per_kg']:,.2f}/kg ({hasil['execution_time_ms']} ms)")

    def test_infeasible_handling(self):
        """Uji kemampuan deteksi solver jika kendala mustahil dipenuhi (infeasible)"""
        df_rusak = self.df_bahan.copy()
        # Jika semua batas maksimal dipatok 5%, total bahan hanya bisa max 9 * 5% = 45%, tidak mungkin mencapai 100%
        df_rusak["batas_maks_layer"] = 5.0
        hasil = hitung_formulasi_pakan(df_rusak, self.fase_1)
        self.assertFalse(hasil["success"])
        self.assertIn("Infeasible", hasil["status_message"])
        self.assertIsNotNone(hasil.get("diagnosa"))
        print(f"[PASS] Infeasible Handling berhasil ditangani secara anggun dengan diagnosa terstruktur.")

    def test_negative_value_validation(self):
        """Uji validasi black box jika pengguna memasukkan nilai negatif"""
        df_negatif = self.df_bahan.copy()
        df_negatif.loc[0, "harga_per_kg"] = -5000.0
        hasil = hitung_formulasi_pakan(df_negatif, self.fase_1)
        self.assertFalse(hasil["success"])
        self.assertIn("negatif", hasil["status_message"].lower())
        print(f"[PASS] Validasi Nilai Negatif berhasil menolak data tidak valid.")

    def test_minimum_ingredients_validation(self):
        """Uji validasi jika bahan aktif kurang dari 2 jenis"""
        df_satu = self.df_bahan.iloc[:1].copy()
        hasil = hitung_formulasi_pakan(df_satu, self.fase_1)
        self.assertFalse(hasil["success"])
        self.assertIn("minimal 2", hasil["status_message"].lower())
        print(f"[PASS] Validasi Minimal 2 Bahan Aktif berhasil dicegat.")

    def test_crud_database_operations(self):
        """Uji fungsionalitas CRUD Tambah, Update, dan Hapus bahan baku serta Update Nutrisi Acuan di MySQL"""
        # 1. Tambah bahan baru
        sukses_tb, msg_tb = tambah_bahan_pakan(
            kode_bahan="UJI_TEST",
            nama_bahan="Bahan Uji Black Box",
            kategori="Uji Coba",
            harga_per_kg=5000.0,
            batas_maks_layer=10.0,
            pk=20.0, lk=5.0, sk=3.0, abu=4.0, ca=1.0, p=0.5, em=2500.0
        )
        self.assertTrue(sukses_tb, msg_tb)

        df_setelah_tambah = get_bahan_pakan()
        bahan_baru = df_setelah_tambah[df_setelah_tambah["kode_bahan"] == "UJI_TEST"]
        self.assertFalse(bahan_baru.empty, "Bahan baru tidak ditemukan setelah di-insert ke MySQL")
        bahan_id = int(bahan_baru.iloc[0]["id"])

        # 2. Update nutrisi acuan
        sukses_nt, msg_nt = update_nutrisi_acuan(
            fase_id=1,
            pk_min=17.2, pk_max=17.6,
            lk_min=2.5, lk_max=7.0,
            sk_max=7.0, abu_min=10.0, abu_max=14.0,
            ca_min=3.25, ca_max=4.0,
            p_min=0.37, p_max=0.41,
            em_min=2750.0, em_max=2900.0
        )
        self.assertTrue(sukses_nt, msg_nt)

        # 3. Hapus bahan uji
        sukses_hp, msg_hp = hapus_bahan_pakan(bahan_id)
        self.assertTrue(sukses_hp, msg_hp)

        df_setelah_hapus = get_bahan_pakan()
        self.assertTrue(df_setelah_hapus[df_setelah_hapus["id"] == bahan_id].empty, "Bahan uji harusnya sudah terhapus dari MySQL")
        print(f"[PASS] Pengujian CRUD Database MySQL (Insert, Update, Delete) Berhasil 100%.")

    def test_riwayat_optimasi_json_mysql(self):
        """Uji penyimpanan dan pembacaan riwayat formulasi berformat JSON ke tabel MySQL"""
        hasil = hitung_formulasi_pakan(self.df_bahan, self.fase_1)
        self.assertTrue(hasil["success"])

        komposisi_disimpan = []
        for item in hasil["komposisi"]:
            item_c = dict(item)
            item_c["kebutuhan_kg"] = round(item["proporsi_desimal"] * 100.0, 2)
            item_c["subtotal_biaya"] = round(item_c["kebutuhan_kg"] * item["harga_per_kg"], 2)
            komposisi_disimpan.append(item_c)

        catatan_uji = "Pengujian Unit Test Riwayat JSON MySQL"
        sukses_simpan, msg_simpan = simpan_riwayat_optimasi(
            fase_id=self.fase_1["id"],
            nama_fase=self.fase_1["nama_fase"],
            total_biaya_per_kg=hasil["total_biaya_per_kg"],
            status_solver=hasil["status_message"],
            detail_komposisi=komposisi_disimpan,
            detail_nutrisi=hasil["capaian_nutrisi"],
            catatan=catatan_uji
        )
        self.assertTrue(sukses_simpan, msg_simpan)

        # Ambil riwayat terbaru
        list_riwayat = get_riwayat_optimasi(limit=5)
        self.assertGreater(len(list_riwayat), 0)
        terbaru = list_riwayat[0]
        self.assertEqual(terbaru["catatan"], catatan_uji)
        self.assertIsInstance(terbaru["detail_komposisi"], list)
        self.assertIsInstance(terbaru["detail_nutrisi"], list)

        # Bersihkan record uji
        hapus_riwayat_optimasi(terbaru["id"])
        print(f"[PASS] Penyimpanan Riwayat JSON MySQL & Pembacaan kembali Berhasil 100%.")

    def test_6_skenario_benchmarking(self):
        """Uji 6 Skenario Matriks Benchmarking Algoritma Skripsi Bab IV"""
        # Skenario 1: Fase 1 Baseline Normal
        res1 = hitung_formulasi_pakan(self.df_bahan, self.fase_1)
        self.assertTrue(res1["success"])
        self.assertAlmostEqual(res1["total_biaya_per_kg"], 6225.89, places=2)

        # Skenario 2: Fase 1 Batas SBM 25%
        df_sk2 = self.df_bahan.copy()
        df_sk2.loc[df_sk2["kode_bahan"] == "SBM", "batas_maks_layer"] = 25.0
        res2 = hitung_formulasi_pakan(df_sk2, self.fase_1)
        self.assertTrue(res2["success"])
        self.assertAlmostEqual(res2["total_biaya_per_kg"], 6236.87, places=2)

        # Skenario 3: Fase 1 Batas SBM 20% (Infeasible)
        df_sk3 = self.df_bahan.copy()
        df_sk3.loc[df_sk3["kode_bahan"] == "SBM", "batas_maks_layer"] = 20.0
        res3 = hitung_formulasi_pakan(df_sk3, self.fase_1)
        self.assertFalse(res3["success"])
        self.assertIn("Infeasible", res3["status_message"])

        # Skenario 4: Fase 2 Baseline Normal
        res4 = hitung_formulasi_pakan(self.df_bahan, self.fase_2)
        self.assertTrue(res4["success"])
        self.assertAlmostEqual(res4["total_biaya_per_kg"], 6171.54, places=2)

        # Skenario 5: Fase 2 Jagung Naik Rp6.800
        df_sk5 = self.df_bahan.copy()
        df_sk5.loc[df_sk5["kode_bahan"] == "JAGUNG", "harga_per_kg"] = 6800.0
        res5 = hitung_formulasi_pakan(df_sk5, self.fase_2)
        self.assertTrue(res5["success"])
        self.assertAlmostEqual(res5["total_biaya_per_kg"], 6651.54, places=2)

        # Skenario 6: Fase 2 Batas Batu 8% (Infeasible)
        df_sk6 = self.df_bahan.copy()
        df_sk6.loc[df_sk6["kode_bahan"] == "BATU", "batas_maks_layer"] = 8.0
        res6 = hitung_formulasi_pakan(df_sk6, self.fase_2)
        self.assertFalse(res6["success"])
        self.assertIn("Infeasible", res6["status_message"])

        print(f"[PASS] Seluruh 6 Skenario Benchmarking Skripsi Bab IV Berhasil 100% Sesuai!")


if __name__ == "__main__":
    unittest.main()
