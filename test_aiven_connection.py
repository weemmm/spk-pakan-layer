"""
Skrip Uji Coba Koneksi Database Aiven MySQL
Gunakan skrip ini untuk memverifikasi kredensial Aiven MySQL sebelum melakukan deployment ke Streamlit Cloud.

Cara pakai:
python test_aiven_connection.py
"""

import sys
import os

# Tambahkan root path ke sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from config.db_connection import test_db_connection, get_db_config
from modules.db_manager import init_database_tables, get_bahan_pakan, get_nutrisi_acuan


def main():
    print("=" * 70)
    print("🔍 MEMERIKSA KONEKSI DATABASE MYSQL...")
    print("=" * 70)

    cfg = get_db_config()
    print(f"• Host     : {cfg['host']}")
    print(f"• Port     : {cfg['port']}")
    print(f"• User     : {cfg['user']}")
    print(f"• Database : {cfg['database']}")
    print(f"• SSL Mode : {'Disabled' if cfg['ssl_disabled'] else 'Enabled (Default Cloud)'}")
    print("-" * 70)

    sukses, pesan = test_db_connection()
    if sukses:
        print("✅ STATUS : BERHASIL TERHUBUNG!")
        print(f"   Detail : {pesan}")
        print("\n⏳ Menginisialisasi skema tabel & data awal (seeding)...")
        init_database_tables()
        
        df_bahan = get_bahan_pakan()
        list_nutrisi = get_nutrisi_acuan()
        print(f"✅ Tabel bahan_pakan : Terisi {len(df_bahan)} bahan baku aktif.")
        print(f"✅ Tabel nutrisi_acuan: Terisi {len(list_nutrisi)} fase standar nutrisi.")
        print("\n🚀 Database siap digunakan untuk deployment ke Streamlit Community Cloud!")
    else:
        print("❌ STATUS : GAGAL TERHUBUNG!")
        print(f"   Pesan  : {pesan}")
        print("\n💡 Tips Perbaikan:")
        print("1. Pastikan status Service Aiven MySQL di console.aiven.io sudah 'RUNNING' (berwarna hijau).")
        print("2. Periksa kembali Host, Port, User, Password, dan nama Database pada .env atau secrets.")
        print("3. Pastikan port (misal 10000-30000) tidak diblokir oleh firewall lokal.")
    print("=" * 70)


if __name__ == "__main__":
    main()

