"""
Prediction Session Service - Session yönetimi işlemleri
"""


class PredictionSessionService:
    """Tahmin session yönetimi servisi"""
    
    @staticmethod
    def get_session_model_info(session_data):
        """
        Session'dan model bilgilerini al
        
        Args:
            session_data (dict): Session verileri
            
        Returns:
            dict: Model bilgileri
        """
        return {
            'current_model_id': session_data.get('current_model_id'),
            'current_model_ready': session_data.get('current_model_ready', False),
            'prediction_model': session_data.get('prediction_model'),
            'prediction_mode_active': session_data.get('prediction_mode_active', False),
            'column_types': session_data.get('column_types', {})
        }
    
    @staticmethod
    def validate_session_for_prediction(session_data):
        """
        Tahmin için session verilerini doğrula
        
        Args:
            session_data (dict): Session verileri
            
        Returns:
            dict: Doğrulama sonucu
        """
        session_info = PredictionSessionService.get_session_model_info(session_data)
        
        # Prediction mode kontrolü
        if session_info['prediction_mode_active']:
            if not session_info['prediction_model']:
                return {
                    'valid': False,
                    'message': 'Tahmin modeli bulunamadı!'
                }
        else:
            # Normal mode kontrolü
            if not (session_info['current_model_id'] and session_info['current_model_ready']):
                return {
                    'valid': False,
                    'message': 'Model objeleri bulunamadı. Lütfen önce bir model eğitin.'
                }
        
        return {
            'valid': True,
            'message': 'Session doğrulama başarılı'
        }
    
    @staticmethod
    def clean_prediction_session(session):
        """
        Tahmin sonrası session'ı temizle
        
        Args:
            session: Flask session objesi
        """
        session.pop('prediction_mode_active', None)
        session.pop('prediction_mode', None)
