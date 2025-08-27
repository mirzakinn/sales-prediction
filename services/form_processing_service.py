"""
Form Processing Service - Form verilerini işleme ve doğrulama
"""


class FormProcessingService:
    """Form verilerini işleme ve doğrulama servisi"""
    
    @staticmethod
    def parse_training_form_parameters(form_data):
        """
        Form verilerinden model parametrelerini çıkar
        
        Args:
            form_data (dict): Flask form verileri
            
        Returns:
            dict: Ayrıştırılmış parametreler
        """
        model_type = form_data.get('model_type')
        test_size = float(form_data.get('test_size', 0.2))
        handle_missing = form_data.get('handle_missing', 'drop')
        
        # Checkbox'ları kontrol et
        use_grid_search = 'use_grid_search' in form_data
        use_auto_model_selection = 'use_auto_model_selection' in form_data
        use_detailed_mode = 'use_detailed_mode' in form_data
        
        # Model parametrelerini ayıkla
        model_params = FormProcessingService._extract_model_parameters(form_data)
        
        return {
            'model_type': model_type,
            'test_size': test_size,
            'handle_missing': handle_missing,
            'use_grid_search': use_grid_search,
            'use_auto_model_selection': use_auto_model_selection,
            'use_detailed_mode': use_detailed_mode,
            'model_params': model_params
        }
    
    @staticmethod
    def _extract_model_parameters(form_data):
        """
        Form verilerinden model parametrelerini ayıkla
        
        Args:
            form_data (dict): Flask form verileri
            
        Returns:
            dict: Model parametreleri
        """
        model_params = {}
        excluded_keys = [
            'model_type', 'test_size', 'handle_missing', 
            'use_grid_search', 'use_auto_model_selection', 'use_detailed_mode'
        ]
        
        for key, value in form_data.items():
            if key not in excluded_keys:
                model_params[key] = FormProcessingService._convert_parameter_value(value)
        
        return model_params
    
    @staticmethod
    def _convert_parameter_value(value):
        """
        Parametre değerini uygun tipe dönüştür
        
        Args:
            value (str): Form değeri
            
        Returns:
            Dönüştürülmüş değer
        """
        try:
            # Sayısal değerleri dönüştür
            if value.replace('.', '').replace('-', '').isdigit():
                return float(value) if '.' in value else int(value)
            elif value.lower() in ['true', 'false']:
                return value.lower() == 'true'
            else:
                return value
        except:
            return value
    
    @staticmethod
    def validate_form_data(form_data):
        """
        Form verilerini doğrula
        
        Args:
            form_data (dict): Flask form verileri
            
        Returns:
            dict: Doğrulama sonucu
        """
        model_type = form_data.get('model_type')
        test_size = form_data.get('test_size', '0.2')
        
        if not model_type and 'use_auto_model_selection' not in form_data:
            return {
                'valid': False,
                'message': 'Model tipi seçilmemiş veya otomatik seçim aktif değil.'
            }
        
        try:
            test_size_float = float(test_size)
            if not (0.1 <= test_size_float <= 0.5):
                return {
                    'valid': False,
                    'message': 'Test veri oranı 0.1 ile 0.5 arasında olmalıdır.'
                }
        except ValueError:
            return {
                'valid': False,
                'message': 'Test veri oranı geçerli bir sayı olmalıdır.'
            }
        
        return {
            'valid': True,
            'message': 'Form doğrulama başarılı'
        }
