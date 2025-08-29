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
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
    MAX_CONTENT_LENGTH = 256 * 1024 * 1024  # 256MB max file size
    
    # Storage paths for ML models (otomatik klasör oluşturma)
    STORAGE_BASE_PATH = BASE_DIR / 'storage'
    
    # Folder names - centralized configuration
    MODEL_FOLDER_NAME = 'models'
    ENCODER_FOLDER_NAME = 'encoders'
    SCALER_FOLDER_NAME = 'scalers'
    
    # Full paths
    MODEL_STORAGE_PATH = STORAGE_BASE_PATH / MODEL_FOLDER_NAME
    ENCODER_STORAGE_PATH = STORAGE_BASE_PATH / ENCODER_FOLDER_NAME
    SCALER_STORAGE_PATH = STORAGE_BASE_PATH / SCALER_FOLDER_NAME
    
    # Database configuration
    DATABASE_URL = 'sqlite:///sales_prediction.db'
    DATABASE_PATH = 'sales_prediction.db'
    
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
    """Prodüksiyon ortamı yapılandırması"""
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
