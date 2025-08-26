"""
Flask uygulama yapılandırması
"""
import os
from pathlib import Path

# Base directory path
BASE_DIR = Path(__file__).parent.parent

class Config:
    """Uygulama yapılandırma sınıfı"""
    SECRET_KEY = 'your-secret-key-here'  # Güvenlik için değiştir
    
    # File upload settings
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 256 * 1024 * 1024  # 256MB max file size
    
    # Storage paths for ML models (otomatik klasör oluşturma)
    STORAGE_BASE_PATH = BASE_DIR / 'storage'
    MODEL_STORAGE_PATH = STORAGE_BASE_PATH / 'trained_models'
    ENCODER_STORAGE_PATH = STORAGE_BASE_PATH / 'encoders'
    SCALER_STORAGE_PATH = STORAGE_BASE_PATH / 'scalers'
    
    # Database configuration
    DATABASE_URL = 'sqlite:///sales_prediction.db'
    
    @staticmethod
    def create_storage_directories():
        """Storage klasörlerini otomatik oluştur"""
        directories = [
            Config.STORAGE_BASE_PATH,
            Config.MODEL_STORAGE_PATH,
            Config.ENCODER_STORAGE_PATH,
            Config.SCALER_STORAGE_PATH
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

class DevelopmentConfig(Config):
    """Geliştirme ortamı yapılandırması"""
    DEBUG = True
    HOST = '127.0.0.1'
    PORT = 5000

class ProductionConfig(Config):
    """Prodüksiyon ortamı Ayapılandırması"""
    DEBUG = False
    HOST = '0.0.0.0'
    PORT = int(os.environ.get('PORT', 5000))

    DATABASE_URL = 'sqlite:///sales_prediction_prod.db'

# Yapılandırma seçeneği
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
