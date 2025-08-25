"""
Development server entry point
Flask uygulamasını geliştirme modunda başlatır
"""
import os
from app import create_app

if __name__ == '__main__':
    # Yapılandırma adını al
    config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Uygulamayı oluştur
    app = create_app(config_name)
    
    # Geliştirme modunda çalıştır
    app.run(debug=True, host='127.0.0.1', port=5000)
