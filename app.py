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
from blueprints.data_processing import processing_bp
from blueprints.model_training import training_bp
from blueprints.predictions import prediction_bp
from blueprints.results import results_bp
from blueprints.model_management import management_bp


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
    app.register_blueprint(processing_bp)
    app.register_blueprint(training_bp)
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


if __name__ == '__main__':
    # Yapılandırma adını al
    config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Uygulamayı oluştur
    app = create_app(config_name)
    
    # Yapılandırma bilgilerini al
    current_config = config[config_name]
    
    
    # Uygulamayı çalıştır
    app.run(
        debug=current_config.DEBUG,
        host=current_config.HOST,
        port=current_config.PORT
    )