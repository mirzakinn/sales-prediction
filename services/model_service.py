"""Model eğitimi ve yönetimi servisleri"""

import sqlite3
from pathlib import Path
from models.ml_models.model_selector import select_model
from utils.auto_model_selector import find_best_model
from utils.ml_utils import analyze_model
from utils.file_utils import save_model_files
from models.database.crud import save_trained_model
from utils import globals

class ModelService:
    """Model eğitimi ve yönetimi işlemlerini yöneten servis sınıfı"""
    
    @staticmethod
    def train_single_model(x_train, y_train, x_test, y_test, model_type, 
                          model_params, use_grid_search=False):
        """
        Tek model eğitimi yapar
        """
        model, y_pred, score = select_model(
            x_train, y_train, x_test, y_test, 
            model_type, model_params, use_grid_search
        )
        
        performance = analyze_model(y_test, y_pred)
        
        return {
            'model': model,
            'predictions': y_pred,
            'score': score,
            'performance': performance,
            'model_type': model_type,
            'model_params': model_params
        }
    
    @staticmethod
    def train_auto_model(x_train, y_train, x_test, y_test, detailed_mode=False):
        """
        Otomatik model seçimi yapar
        """
        best_result = find_best_model(
            x_train, y_train, x_test, y_test, 
            detailed_mode=detailed_mode
        )
        
        # Performance hesaplama - y_test'i parametre olarak kullan
        performance = analyze_model(y_test, best_result['predictions'])
        
        return {
            'model': best_result['model'],
            'predictions': best_result['predictions'],
            'score': best_result['r2_score'],
            'performance': performance,
            'model_type': best_result['model_name'],
            'model_params': best_result.get('best_params', {})
        }
    
    @staticmethod
    def save_trained_model_complete(model_result, target_column, feature_columns, 
                                   filename, encoders, scaler):
        """
        Eğitilmiş modeli veritabanına ve dosya sistemine kaydeder
        """
        # Veritabanına kaydet
        model_id = save_trained_model(
            model_name="Model",
            algorithm=model_result['model_type'],
            r2_score=model_result['performance']['r2_score'],
            mae=model_result['performance']['mae'],
            mse=model_result['performance']['mse'],
            rmse=model_result['performance']['rmse'],
            target_column=target_column,
            feature_columns=feature_columns,
            filename=filename,
            model_params=model_result.get('model_params', {})
        )
        
        # Dosya sistemine kaydet
        file_paths = save_model_files(
            model_id=model_id,
            model_obj=model_result['model'],
            encoders_obj=encoders,
            scaler_obj=scaler
        )
        
        return model_id, file_paths
    
    @staticmethod
    def reset_all_models():
        """Tüm eğitilmiş modelleri siler ve ID'leri sıfırlar"""
        
        # Global değişkenleri temizle
        globals.CURRENT_MODEL = None
        globals.CURRENT_ENCODERS = None
        globals.CURRENT_SCALER = None
        
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
            
        except Exception as e:
            raise Exception(f"Database temizleme hatası: {e}")
        finally:
            conn.close()
        
        # Model dosyalarını sil
        storage_path = Path('storage')
        deleted_count = 0
        
        # Models klasörü
        models_path = storage_path / 'models'
        if models_path.exists():
            for file in models_path.glob('*.pkl'):
                file.unlink()
                deleted_count += 1
        
        # Encoders klasörü
        encoders_path = storage_path / 'encoders'
        if encoders_path.exists():
            for file in encoders_path.glob('*.pkl'):
                file.unlink()
        
        # Scalers klasörü  
        scalers_path = storage_path / 'scalers'
        if scalers_path.exists():
            for file in scalers_path.glob('*.pkl'):
                file.unlink()
        
        return deleted_count
