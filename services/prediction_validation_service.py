"""
Prediction Validation Service - Doğrulama işlemleri
"""


class PredictionValidationService:
    """Tahmin doğrulama servisi"""
    
    @staticmethod
    def validate_model_id(model_id):
        """
        Model ID'sini doğrula
        
        Args:
            model_id: Model ID
            
        Returns:
            dict: Doğrulama sonucu
        """
        if not model_id:
            return {
                'valid': False,
                'message': 'Model ID eksik!'
            }
        
        try:
            int(model_id)
            return {
                'valid': True,
                'message': 'Model ID geçerli'
            }
        except (ValueError, TypeError):
            return {
                'valid': False,
                'message': 'Model ID geçerli bir sayı olmalıdır!'
            }
    
    @staticmethod
    def validate_prediction_data(prediction_data, feature_columns):
        """
        Tahmin verilerini doğrula
        
        Args:
            prediction_data (dict): Tahmin verileri
            feature_columns (list): Gerekli özellik sütunları
            
        Returns:
            dict: Doğrulama sonucu
        """
        missing_fields = []
        
        for feature in feature_columns:
            if feature not in prediction_data or not prediction_data[feature]:
                missing_fields.append(feature)
        
        if missing_fields:
            return {
                'valid': False,
                'message': f'Şu alanlar boş bırakılamaz: {", ".join(missing_fields)}'
            }
        
        return {
            'valid': True,
            'message': 'Tahmin verileri geçerli'
        }
    
    @staticmethod
    def validate_model_objects(model_objects):
        """
        Model objelerini doğrula
        
        Args:
            model_objects (dict): Model objeleri
            
        Returns:
            dict: Doğrulama sonucu
        """
        required_keys = ['model', 'encoders', 'scaler']
        
        if not model_objects:
            return {
                'valid': False,
                'message': 'Model objeleri bulunamadı!'
            }
        
        missing_keys = [key for key in required_keys if key not in model_objects]
        
        if missing_keys:
            return {
                'valid': False,
                'message': f'Model objelerinde eksik anahtarlar: {", ".join(missing_keys)}'
            }
        
        return {
            'valid': True,
            'message': 'Model objeleri geçerli'
        }
