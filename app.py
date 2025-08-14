"""
Sales Prediction Flask Uygulaması
Blueprint mimarisi kullanılarak modüler hale getirildi.
Basit web sayfaları yaklaşımı - API yok.
"""
from flask import Flask
import os
from config import config
from utils.file_utils import ensure_upload_folder
from blueprints.main import main_bp
from blueprints.upload import upload_bp
from blueprints.model_management import management_bp
from blueprints.predictions import prediction_bp
from blueprints.model_training import training_bp  
from blueprints.data_processing import processing_bp


def create_app(config_name='default'):
    """Flask uygulaması factory fonksiyonu"""
    app = Flask(__name__)
    
    # Yapılandırmayı yükle
    app.config.from_object(config[config_name])
    
    # Upload klasörünü oluştur
    ensure_upload_folder(app.config['UPLOAD_FOLDER'])
    
    # Blueprint'leri kaydet
    app.register_blueprint(main_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(management_bp)
    app.register_blueprint(prediction_bp)
    app.register_blueprint(training_bp)
    app.register_blueprint(processing_bp)

    # Template context processor - session'ı template'lerde kullanılabilir yap
    @app.context_processor
    def inject_session():
        from flask import session
        return dict(session=session)
    
    # JSON filter ekleme
    @app.template_filter('from_json')
    def from_json_filter(value):
        """JSON string'i Python objesine çevirir"""
        import json
        try:
            if isinstance(value, str):
                return json.loads(value)
            return value
        except:
            return []
    
    return app

def get_config_name():
    """Ortam değişkeninden veya varsayılan değerden config adını al"""
    return os.environ.get('FLASK_ENV', 'development')

if __name__ == '__main__':
    # Yapılandırma adını al
    config_name = get_config_name()
    
    # Uygulamayı oluştur
    app = create_app(config_name)
    
    # Yapılandırma bilgilerini al
    current_config = config[config_name]
    
    print("=" * 60)
    print("🚀 SALES PREDICTION FLASK UYGULAMASI")
    print("=" * 60)
    print(f"📂 Upload klasörü: {app.config['UPLOAD_FOLDER']}")
    print(f"📄 Desteklenen dosya türleri: XLSX, XLS, CSV")
    print(f"🔧 Yapılandırma: {config_name}")
    print(f"🌐 Host: {current_config.HOST}")
    print(f"🚪 Port: {current_config.PORT}")
    print(f"🐛 Debug modu: {current_config.DEBUG}")
    print("=" * 60)
    print("💡 Blueprint yapısı:")
    print("   • Main Blueprint: Ana sayfa")
    print("   • Upload Blueprint: Dosya yükleme") 
    print("   • Management Blueprint: Model yönetimi")
    print("   • Prediction Blueprint: Tahmin işlemleri")
    print("   • Training Blueprint: Model eğitimi")
    print("   • Processing Blueprint: Veri işleme")
    print("=" * 60)
    
    # Uygulamayı çalıştır
    app.run(
        debug=current_config.DEBUG,
        host=current_config.HOST,
        port=current_config.PORT
    )