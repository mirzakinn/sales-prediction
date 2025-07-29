"""
Flask uygulama yapılandırması
"""
import os

class Config:
    """Uygulama yapılandırma sınıfı"""
    SECRET_KEY = 'your-secret-key-here'  # Güvenlik için değiştir
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

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

# Yapılandırma seçeneği
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
