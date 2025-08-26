"""
Sales Prediction Flask Uygulaması
Blueprint mimarisi kullanılarak modüler hale getirildi.
Basit web sayfaları yaklaşımı - API yok.
"""
from flask import Flask
import os
from config import config
from services.file_service import FileService
from controllers.main_controller import main_bp
from controllers.upload_controller import upload_bp
from controllers.data_controller import processing_bp
from controllers.configure_model_controller import configure_model_bp
from controllers.training_model_controller import training_model_bp
from controllers.prediction_controller import prediction_bp
from controllers.management_controller import management_bp
from controllers.results_controller import results_bp


def create_app(config_name='default'):
    """Flask uygulaması factory fonksiyonu"""
    app = Flask(__name__)
    
    # Yapılandırmayı yükle
    app.config.from_object(config[config_name])
    
    # Upload klasörünü oluştur
    FileService.ensure_directory('storage/uploads')
    
    # Template ve static klasörlerini güncelle
    app.template_folder = '../views/templates'
    app.static_folder = '../views/static'
    
    # Blueprint'leri kaydet
    app.register_blueprint(main_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(processing_bp)
    app.register_blueprint(configure_model_bp)
    app.register_blueprint(training_model_bp)
    app.register_blueprint(prediction_bp)
    app.register_blueprint(results_bp)
    app.register_blueprint(management_bp)

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
