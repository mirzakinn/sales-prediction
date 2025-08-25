"""Model eğitimi ve yönetimi servisleri"""

from models.ml_models.model_selector import select_model
from utils.auto_model_selector import find_best_model
from utils.ml_utils import analyze_model
from utils.file_utils import save_model_files
from models.database.crud import save_trained_model

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
