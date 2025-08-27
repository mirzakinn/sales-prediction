"""
Prediction Model Service - Model yükleme ve yönetimi
"""
from services.model_loading_service import ModelLoadingService
from services.prediction_session_service import PredictionSessionService


class PredictionModelService:
    """Tahmin modeli yükleme ve yönetimi servisi"""
    
    @staticmethod
    def load_model_from_database(model_id):
        """
        Database'den model bilgilerini yükle
        
        Args:
            model_id (int): Model ID
            
        Returns:
            dict: Model bilgileri veya hata
        """
        return ModelLoadingService.load_from_database(model_id)
    
    @staticmethod
    def load_model_objects(model_id):
        """
        Model dosyalarından model objelerini yükle
        
        Args:
            model_id (int): Model ID
            
        Returns:
            dict: Model objeleri veya hata
        """
        return ModelLoadingService.load_from_files(model_id)
    
    @staticmethod
    def get_current_model_objects(session_data):
        """
        Mevcut model objelerini al (session veya global'den)
        
        Args:
            session_data (dict): Session verileri
            
        Returns:
            dict: Model objeleri veya hata
        """
        session_info = PredictionSessionService.get_session_model_info(session_data)
        
        if session_info['current_model_id'] and session_info['current_model_ready']:
            # Model dosyalarından yükle
            return ModelLoadingService.load_from_files(session_info['current_model_id'])
        else:
            # Global objelerden al
            return ModelLoadingService.get_global_model_objects()
    
    @staticmethod
    def get_prediction_mode_model(session_data):
        """
        Prediction mode için model objelerini al
        
        Args:
            session_data (dict): Session verileri
            
        Returns:
            dict: Model objeleri veya hata
        """
        session_info = PredictionSessionService.get_session_model_info(session_data)
        
        if not session_info['prediction_model']:
            return {
                'success': False,
                'data': None,
                'message': 'Tahmin modeli bulunamadı!'
            }
        
        # Model dosyalarını yükle
        return ModelLoadingService.load_from_files(session_info['prediction_model']['id'])
