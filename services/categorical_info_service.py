"""
Categorical Info Service - Kategorik bilgi işlemleri
"""


class CategoricalInfoService:
    """Kategorik bilgi işleme servisi"""
    
    @staticmethod
    def extract_from_model_objects(model_objects):
        """
        Model objelerinden kategorik bilgileri çıkar
        
        Args:
            model_objects (dict): Model objeleri
            
        Returns:
            tuple: (column_types, categorical_values)
        """
        column_types = {}
        categorical_values = {}
        
        try:
            if model_objects and 'encoders' in model_objects:
                encoders = model_objects['encoders']
                for col_name, encoder in encoders.items():
                    if hasattr(encoder, 'classes_'):
                        categorical_values[col_name] = encoder.classes_.tolist()
                        column_types[col_name] = 'categorical'
            
            return column_types, categorical_values
            
        except Exception as e:
            return {}, {}
    
    @staticmethod
    def set_default_column_types(feature_columns, column_types):
        """
        Eksik kolonlar için varsayılan tipleri ayarla
        
        Args:
            feature_columns (list): Özellik sütunları
            column_types (dict): Mevcut kolon tipleri
            
        Returns:
            dict: Güncellenmiş kolon tipleri
        """
        updated_types = column_types.copy()
        
        for feature in feature_columns:
            if feature not in updated_types:
                updated_types[feature] = 'numeric'
        
        return updated_types
    
    @staticmethod
    def prepare_form_column_info(session_data, model_id, feature_columns):
        """
        Form için kolon bilgilerini hazırla
        
        Args:
            session_data (dict): Session verileri
            model_id (int): Model ID
            feature_columns (list): Özellik sütunları
            
        Returns:
            dict: Kolon bilgileri
        """
        from services.model_loading_service import ModelLoadingService
        
        column_types = {}
        categorical_values = {}
        
        try:
            # Session'dan column types'ı al (eğer varsa)
            if 'column_types' in session_data:
                column_types = session_data['column_types']
            
            # Model objelerini yükle ve categorical values'ları çıkar
            if model_id:
                model_result = ModelLoadingService.load_from_files(model_id)
                if model_result['success']:
                    col_types, cat_values = CategoricalInfoService.extract_from_model_objects(
                        model_result['data']
                    )
                    column_types.update(col_types)
                    categorical_values.update(cat_values)
            
            # Eksik kolonlar için varsayılan tipleri ayarla
            column_types = CategoricalInfoService.set_default_column_types(
                feature_columns, column_types
            )
                
        except Exception as e:
            # Hata durumunda tüm kolonları numeric olarak varsay
            column_types = CategoricalInfoService.set_default_column_types(
                feature_columns, {}
            )
        
        return {
            'column_types': column_types,
            'categorical_values': categorical_values
        }
