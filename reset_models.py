import sqlite3
from pathlib import Path

def reset_all_models():
    """Tüm eğitilmiş modelleri siler ve ID'leri sıfırlar"""
    
    # Database bağlantısı
    conn = sqlite3.connect('sales_prediction.db')
    cursor = conn.cursor()
    
    try:
        # Tabloları temizle
        cursor.execute('DELETE FROM trained_models')
        cursor.execute('DELETE FROM model_files') 
        cursor.execute('DELETE FROM training_sessions')
        
        # AUTOINCREMENT sayaçlarını sıfırla
        cursor.execute('DELETE FROM sqlite_sequence WHERE name IN ("trained_models", "model_files", "training_sessions")')
        
        conn.commit()
        print("Database tabloları temizlendi ve ID sayaçları sıfırlandı")
        
    except Exception as e:
        print(f"Database temizleme hatası: {e}")
    finally:
        conn.close()
    
    # Model dosyalarını sil
    storage_path = Path('storage')
    
    # Models klasörü
    models_path = storage_path / 'models'
    if models_path.exists():
        deleted_count = 0
        for file in models_path.glob('*.pkl'):
            file.unlink()
            deleted_count += 1
        print(f"{deleted_count} model dosyası silindi")
    
    # Encoders klasörü
    encoders_path = storage_path / 'encoders'
    if encoders_path.exists():
        for file in encoders_path.glob('*.pkl'):
            file.unlink()
        print("Encoder dosyaları silindi")
    
    # Scalers klasörü  
    scalers_path = storage_path / 'scalers'
    if scalers_path.exists():
        for file in scalers_path.glob('*.pkl'):
            file.unlink()
        print("Scaler dosyaları silindi")
    
    print("\nTüm modeller başarıyla silindi! Yeni model ID'si 1'den başlayacak.")

if __name__ == "__main__":
    reset_all_models()
