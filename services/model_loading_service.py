"""
Model Loading Service - Model dosyalarını yükleme işlemleri
"""
from models.database.crud import get_model_by_id
from utils.file_utils import load_model_files
from utils import globals


class ModelLoadingService:
    """Model dosyalarını yükleme servisi"""
    
    @staticmethod
    def load_from_database(model_id):
        """
        Database'den model bilgilerini yükle
        
        Args:
            model_id (int): Model ID
            
        Returns:
            dict: Model bilgileri veya hata
        """
        try:
            model_info = get_model_by_id(model_id)
            
            if not model_info:
                return {
                    'success': False,
                    'data': None,
                    'message': 'Model veritabanında bulunamadı!'
                }
            
            return {
                'success': True,
                'data': model_info,
                'message': 'Model bilgileri başarıyla yüklendi'
            }
            
        except Exception as e:
            return {
                'success': False,
                'data': None,
                'message': f'Model yükleme hatası: {str(e)}'
            }
    
    @staticmethod
    def load_from_files(model_id):
        """
        Model dosyalarından model objelerini yükle
        
        Args:
            model_id (int): Model ID
            
        Returns:
            dict: Model objeleri veya hata
        """
        try:
            model_objects = load_model_files(model_id)
            
            if not model_objects:
                return {
                    'success': False,
                    'data': None,
                    'message': 'Model dosyaları yüklenemedi!'
                }
            
            return {
                'success': True,
                'data': model_objects,
                'message': 'Model objeleri başarıyla yüklendi'
            }
            
        except Exception as e:
            return {
                'success': False,
                'data': None,
                'message': f'Model dosyaları yükleme hatası: {str(e)}'
            }
    
    @staticmethod
    def get_global_model_objects():
        """
        Global model objelerini al
        
        Returns:
            dict: Model objeleri veya hata
        """
        if globals.CURRENT_MODEL is not None:
            return {
                'success': True,
                'data': {
                    'model': globals.CURRENT_MODEL,
                    'encoders': globals.CURRENT_ENCODERS,
                    'scaler': globals.CURRENT_SCALER
                },
                'message': 'Global model objeleri kullanıldı'
            }
        else:
            return {
                'success': False,
                'data': None,
                'message': 'Global model objeleri bulunamadı'
            }
