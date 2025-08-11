"""
Dosya işlemleri için yardımcı fonksiyonlar
"""
import os
import joblib
from pathlib import Path

ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}

def allowed_file(filename):
    """Dosya uzantısının izin verilen türde olup olmadığını kontrol eder"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_folder(upload_folder):
    """Upload klasörünün var olduğundan emin olur"""
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

def save_model_files(model_id, model_obj, encoders_obj, scaler_obj):
    """
    Model objelerini dosyaya kaydet
    
    Args:
        model_id (int): Database'deki model ID'si
        model_obj: Eğitilmiş model objesi
        encoders_obj: Encoder objeleri
        scaler_obj: Scaler objesi
    
    Returns:
        dict: Kaydedilen dosya yolları
    """
    # Storage klasörleri oluştur (yoksa)
    base_path = Path(__file__).parent.parent / 'storage'
    models_path = base_path / 'models'
    encoders_path = base_path / 'encoders'
    scalers_path = base_path / 'scalers'
    
    # Klasörleri oluştur
    models_path.mkdir(parents=True, exist_ok=True)
    encoders_path.mkdir(parents=True, exist_ok=True)  
    scalers_path.mkdir(parents=True, exist_ok=True)
    
    # Dosya yolları
    model_file = models_path / f'model_{model_id}.pkl'
    encoder_file = encoders_path / f'encoder_{model_id}.pkl'
    scaler_file = scalers_path / f'scaler_{model_id}.pkl'
    
    # Dosyaları kaydet
    joblib.dump(model_obj, model_file)
    joblib.dump(encoders_obj, encoder_file)  
    joblib.dump(scaler_obj, scaler_file)
    
    print(f"✅ Model dosyaları kaydedildi:")
    print(f"   Model: {model_file}")
    print(f"   Encoder: {encoder_file}")
    print(f"   Scaler: {scaler_file}")
    
    return {
        'model_path': str(model_file),
        'encoder_path': str(encoder_file),
        'scaler_path': str(scaler_file)
    }

def load_model_files(model_id):
    """
    Kaydedilmiş model dosyalarını yükler
    
    Args:
        model_id (int): Database'deki model ID'si
    
    Returns:
        dict: Yüklenmiş model objeleri veya None
    """
    try:
        base_path = Path(__file__).parent.parent / 'storage'
        
        # Dosya yolları
        model_file = base_path / 'models' / f'model_{model_id}.pkl'
        encoder_file = base_path / 'encoders' / f'encoder_{model_id}.pkl'  
        scaler_file = base_path / 'scalers' / f'scaler_{model_id}.pkl'
        
        # Dosyaların varlığını kontrol et
        if not all([model_file.exists(), encoder_file.exists(), scaler_file.exists()]):
            print(f"❌ Model dosyaları bulunamadı (ID: {model_id})")
            return None
        
        # Dosyaları yükle
        model_obj = joblib.load(model_file)
        encoders_obj = joblib.load(encoder_file)
        scaler_obj = joblib.load(scaler_file)
        
        print(f"✅ Model dosyaları yüklendi (ID: {model_id})")
        print(f"   Model: {type(model_obj).__name__}")
        print(f"   Encoders: {len(encoders_obj)} adet") 
        print(f"   Scaler: {type(scaler_obj).__name__}")
        
        return {
            'model': model_obj,
            'encoders': encoders_obj,
            'scaler': scaler_obj
        }
        
    except Exception as e:
        print(f"❌ Model yükleme hatası (ID: {model_id}): {e}")
        return None