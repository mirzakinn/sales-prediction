"""
Training Service - Core model eğitimi işlemleri
"""
import os
from services.data_service import DataService
from services.model_service import ModelService
from utils.data_utils import read_file_by_extension
from utils import globals


class TrainingService:
    """Core model eğitimi işlemleri servisi"""
    
    @staticmethod
    def process_training_data(filename, target_column, feature_columns, handle_missing, test_size):
        """
        Eğitim için veriyi işle
        
        Args:
            filename (str): Dosya adı
            target_column (str): Hedef sütun
            feature_columns (list): Özellik sütunları
            handle_missing (str): Eksik veri işleme yöntemi
            test_size (float): Test veri oranı
            
        Returns:
            dict: İşlenmiş veri
        """
        try:
            filepath = os.path.join('storage/uploads', filename)
            df = read_file_by_extension(filepath, filename)
            
            # Veri işleme - DataService kullan
            processed_data = DataService.process_uploaded_file(
                filepath, filename, target_column, feature_columns,
                handle_missing=handle_missing, test_size=test_size
            )
            
            return {
                'success': True,
                'data': processed_data,
                'message': 'Veri işleme başarılı'
            }
            
        except Exception as e:
            return {
                'success': False,
                'data': None,
                'message': f'Veri işleme hatası: {str(e)}'
            }
    
    @staticmethod
    def train_model_with_parameters(processed_data, training_params):
        """
        Parametrelerle model eğit
        
        Args:
            processed_data (dict): İşlenmiş veri
            training_params (dict): Eğitim parametreleri
            
        Returns:
            dict: Eğitim sonucu
        """
        try:
            # Model eğitimi - ModelService kullan
            if training_params['use_auto_model_selection']:
                result = ModelService.train_auto_model(
                    processed_data['X_train'], processed_data['y_train'],
                    processed_data['X_test'], processed_data['y_test'],
                    detailed_mode=training_params['use_detailed_mode']
                )
                # Auto seçimde model tipini güncelle
                training_params['model_type'] = result['model_type']
            else:
                result = ModelService.train_single_model(
                    processed_data['X_train'], processed_data['y_train'],
                    processed_data['X_test'], processed_data['y_test'],
                    training_params['model_type'], 
                    training_params['model_params'], 
                    training_params['use_grid_search']
                )
            
            return {
                'success': True,
                'result': result,
                'model_type': training_params['model_type'],
                'message': 'Model eğitimi başarılı'
            }
            
        except Exception as e:
            return {
                'success': False,
                'result': None,
                'model_type': None,
                'message': f'Model eğitimi hatası: {str(e)}'
            }
    
    @staticmethod
    def save_training_results(result, target_column, feature_columns, filename, processed_data):
        """
        Eğitim sonuçlarını kaydet
        
        Args:
            result (dict): Eğitim sonucu
            target_column (str): Hedef sütun
            feature_columns (list): Özellik sütunları
            filename (str): Dosya adı
            processed_data (dict): İşlenmiş veri
            
        Returns:
            dict: Kaydetme sonucu
        """
        try:
            # Global değişkenleri ayarla
            globals.CURRENT_MODEL = result['model']
            globals.CURRENT_ENCODERS = processed_data['encoders']
            globals.CURRENT_SCALER = processed_data['scaler']
            
            # Model kaydetme - ModelService kullan
            model_id, file_paths = ModelService.save_trained_model_complete(
                result, target_column, feature_columns, filename,
                processed_data['encoders'], processed_data['scaler']
            )
            
            return {
                'success': True,
                'model_id': model_id,
                'file_paths': file_paths,
                'message': 'Model kaydetme başarılı'
            }
            
        except Exception as e:
            return {
                'success': False,
                'model_id': None,
                'file_paths': None,
                'message': f'Model kaydetme hatası: {str(e)}'
            }
