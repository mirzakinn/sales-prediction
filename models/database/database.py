import sqlite3
import os
from pathlib import Path
from contextlib import contextmanager

"""
SQLite database connection and operations for the application.

Responsibilities:
- Initialize SQLite database and create tables
- Provide safe database connections with context managers
- Basic CRUD operations for trained models
"""

# Database dosya yolu
from config import Config
DB_PATH = Config.DATABASE_PATH

def init_database():
    """
    Veritabanını başlatır ve tabloları oluşturur
    
    Returns:
        bool: Başarılı ise True, aksi halde False
    """
    try:
        # schema.sql dosyasını oku
        sql_file_path = Path(__file__).parent / 'schema.sql'
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            schema_sql = file.read()

        # SQLite bağlantısını aç ve tabloları oluştur
        conn = sqlite3.connect(DB_PATH)
        conn.executescript(schema_sql)
        conn.close()
        
        return True
    except Exception as e:
        return False


@contextmanager
def get_db_connection():
    """
    Güvenli SQLite database bağlantısı sağlar (Context Manager)
    
    Kullanım:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM trained_models")
            # Otomatik commit ve close yapılır
    
    Returns:
        sqlite3.Connection: Database connection objesi
    """
    conn = None
    try:
        # SQLite bağlantısını aç
        conn = sqlite3.connect(
            DB_PATH, 
            check_same_thread=False,  # Flask multi-threading için gerekli
            timeout=20.0              # 20 saniye timeout
        )
        
        # SQLite ayarları
        conn.execute('PRAGMA foreign_keys = ON')      # Foreign key kontrolünü aç
        conn.execute('PRAGMA journal_mode = WAL')     # Performans için WAL mode
        
        # Row factory - dict gibi erişim için
        conn.row_factory = sqlite3.Row
        
        # Connection'ı yield et (fonksiyon burada durur)
        yield conn
        
        # with bloğu başarılı biterse commit yap
        conn.commit()
        
    except sqlite3.Error as e:
        # Database hatası varsa rollback yap
        if conn:
            conn.rollback()
        raise
        
    except Exception as e:
        if conn:
            conn.rollback()
        raise
        
    finally:
        # Her durumda connection'ı kapat
        if conn:
            conn.close()


def test_connection():
    """
    Database bağlantısını test eder
    
    Returns:
        bool: Bağlantı başarılı ise True, aksi halde False
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 as test_value")
            result = cursor.fetchone()
            return True
    except Exception as e:
        return False


def get_database_info():
    """
    Database hakkında bilgi verir (tablo sayısı, kayıt sayıları vb.)
    
    Returns:
        dict: Database bilgileri
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Tablo listesini al
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row['name'] for row in cursor.fetchall()]
            
            info = {
                'database_path': DB_PATH,
                'database_exists': os.path.exists(DB_PATH),
                'tables': tables,
                'table_counts': {}
            }
            
            # Her tablodaki kayıt sayısını al
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                count = cursor.fetchone()['count']
                info['table_counts'][table] = count
            
            return info
    except Exception as e:
        return {
            'database_path': DB_PATH,
            'database_exists': False,
            'error': str(e)
        }


# Test fonksiyonu - dosya direkt çalıştırıldığında test yapar
if __name__ == "__main__":
    init_database()
    test_connection()
    get_database_info()