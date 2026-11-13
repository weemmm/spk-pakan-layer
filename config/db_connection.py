import os
from typing import Optional, Tuple, Dict, Any
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

# Load local environment variables jika ada file .env
load_dotenv()


def get_db_config() -> Dict[str, Any]:
    """
    Mengambil konfigurasi koneksi database MySQL secara fleksibel.
    Prioritas:
    1. Streamlit Secrets (st.secrets) jika berjalan di Streamlit Community Cloud
    2. Environment variables (os.getenv) dari file .env (lokal)
    """
    # Nilai default lokal
    host = "localhost"
    port = 3306
    user = "root"
    password = ""
    database = "spk_pakan_layer"
    ssl_ca = None
    ssl_disabled = False

    # 1. Cek Streamlit Secrets jika berjalan di lingkungan Streamlit
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            # Jika user mendefinisikan grup [mysql] di secrets.toml
            if "mysql" in st.secrets:
                m = st.secrets["mysql"]
                host = str(m.get("host", m.get("DB_HOST", host)))
                port = int(m.get("port", m.get("DB_PORT", port)))
                user = str(m.get("user", m.get("DB_USER", user)))
                password = str(m.get("password", m.get("DB_PASSWORD", password)))
                database = str(m.get("database", m.get("DB_NAME", database)))
                ssl_ca = m.get("ssl_ca", m.get("DB_SSL_CA", ssl_ca))
                ssl_disabled = bool(m.get("ssl_disabled", m.get("DB_SSL_DISABLED", ssl_disabled)))
            # Jika user mendefinisikan kunci datar (flat keys) di secrets.toml
            else:
                if "DB_HOST" in st.secrets:
                    host = str(st.secrets["DB_HOST"])
                if "DB_PORT" in st.secrets:
                    port = int(st.secrets["DB_PORT"])
                if "DB_USER" in st.secrets:
                    user = str(st.secrets["DB_USER"])
                if "DB_PASSWORD" in st.secrets:
                    password = str(st.secrets["DB_PASSWORD"])
                if "DB_NAME" in st.secrets:
                    database = str(st.secrets["DB_NAME"])
                if "DB_SSL_CA" in st.secrets:
                    ssl_ca = str(st.secrets["DB_SSL_CA"])
                if "DB_SSL_DISABLED" in st.secrets:
                    ssl_disabled = bool(st.secrets["DB_SSL_DISABLED"])
    except Exception:
        pass

    # 2. Fallback / Override ke Environment Variables (Lokal .env)
    host = os.getenv("DB_HOST", host)
    port = int(os.getenv("DB_PORT", str(port)))
    user = os.getenv("DB_USER", user)
    password = os.getenv("DB_PASSWORD", password)
    database = os.getenv("DB_NAME", database)
    ssl_ca = os.getenv("DB_SSL_CA", ssl_ca)
    if os.getenv("DB_SSL_DISABLED") is not None:
        ssl_disabled = os.getenv("DB_SSL_DISABLED", "").lower() in ("true", "1")

    return {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "database": database,
        "ssl_ca": ssl_ca,
        "ssl_disabled": ssl_disabled
    }


def get_db_connection():
    """
    Membuka dan mengembalikan koneksi MySQL aktif.
    Mendukung koneksi lokal (Laragon/XAMPP) dan cloud (Aiven/PlanetScale).
    Mengembalikan None jika koneksi gagal.
    """
    cfg = get_db_config()
    try:
        conn_params = {
            "host": cfg["host"],
            "port": cfg["port"],
            "user": cfg["user"],
            "password": cfg["password"],
            "database": cfg["database"],
            "charset": "utf8mb4",
            "connection_timeout": 10
        }

        # Penanganan SSL untuk Cloud Database (Aiven MySQL)
        if cfg["ssl_ca"] and os.path.exists(cfg["ssl_ca"]):
            conn_params["ssl_ca"] = cfg["ssl_ca"]
        elif cfg["ssl_disabled"]:
            conn_params["ssl_disabled"] = True

        connection = mysql.connector.connect(**conn_params)
        if connection.is_connected():
            return connection
    except Error:
        return None
    except Exception:
        return None
    return None


def test_db_connection() -> Tuple[bool, str]:
    """
    Menguji koneksi ke database MySQL.
    Mengembalikan tuple (status_sukses, pesan).
    """
    cfg = get_db_config()
    try:
        conn = get_db_connection()
        if conn and conn.is_connected():
            db_info = conn.get_server_info()
            cursor = conn.cursor()
            cursor.execute("SELECT DATABASE();")
            current_db = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            return True, f"Terhubung ke MySQL Server v{db_info} di {cfg['host']}:{cfg['port']} (Database: {current_db})"
        else:
            return False, (
                f"Tidak dapat terhubung ke MySQL di {cfg['host']}:{cfg['port']}. "
                f"Pastikan database '{cfg['database']}' aktif dan kredensial benar."
            )
    except Error as e:
        return False, f"Gagal koneksi MySQL: {str(e)}"
    except Exception as e:
        return False, f"Galat tidak terduga saat koneksi: {str(e)}"
