"""
Prediction Form Service - Form verilerini işleme ve doğrulama
"""
import json
import ast


class PredictionFormService:
    """Tahmin form verilerini işleme servisi"""
    
    @staticmethod
    def extract_prediction_data(form_data, feature_columns):
        """
        Form verilerinden tahmin verilerini çıkar
        
        Args:
            form_data (dict): Flask form verileri
            feature_columns (list): Özellik sütunları
            
        Returns:
            dict: Çıkarılan tahmin verileri veya hata
        """
        prediction_data = {}
        missing_fields = []
        
        for feature in feature_columns:
            value = form_data.get(feature)
            if value:
                # Sayısal değerleri float'a çevir
                try:
                    prediction_data[feature] = float(value)
                except ValueError:
                    prediction_data[feature] = value
            else:
                missing_fields.append(feature)
        
        if missing_fields:
            return {
                'success': False,
                'data': None,
                'message': f'Şu alanlar boş bırakılamaz: {", ".join(missing_fields)}'
            }
        
        return {
            'success': True,
            'data': prediction_data,
            'message': 'Form verileri başarıyla çıkarıldı'
        }
    
    @staticmethod
    def parse_feature_columns(feature_columns_raw):
        """
        Feature columns'ları güvenli şekilde parse et
        
        Args:
            feature_columns_raw: Ham feature columns verisi
            
        Returns:
            list: Parse edilmiş feature columns listesi
        """
        if isinstance(feature_columns_raw, list):
            return feature_columns_raw
        elif isinstance(feature_columns_raw, str):
            # Python liste string'i ise (örn: "['col1', 'col2']")
            if (feature_columns_raw.startswith('[') and feature_columns_raw.endswith(']')):
                try:
                    # Önce JSON olarak dene
                    return json.loads(feature_columns_raw)
                except json.JSONDecodeError:
                    # JSON başarısız olursa literal_eval kullan
                    return ast.literal_eval(feature_columns_raw)
            else:
                # Tek string ise listeye çevir
                return [feature_columns_raw]
        else:
            return []
    
    @staticmethod
    def prepare_model_info_for_template(model_info, feature_columns):
        """
        Template için model bilgilerini hazırla
        
        Args:
            model_info (dict): Database'den gelen model bilgileri
            feature_columns (list): Feature columns listesi
            
        Returns:
            dict: Template için hazırlanmış model bilgileri
        """
        return {
            'model_type': model_info['model_type'],
            'filename': 'Seçilen Model',
            'target_column': model_info['target_column'],
            'feature_columns': feature_columns,
            'performance': {
                'accuracy': round(model_info['r2_score'] * 100, 1) if model_info['r2_score'] else 0,
                'r2_score': model_info['r2_score']
            }
        }
    
    @staticmethod
    def prepare_session_prediction_model(model_info, feature_columns):
        """
        Session için prediction model bilgilerini hazırla
        
        Args:
            model_info (dict): Database'den gelen model bilgileri
            feature_columns (list): Feature columns listesi
            
        Returns:
            dict: Session için hazırlanmış model bilgileri
        """
        return {
            'id': model_info['id'],
            'model_type': model_info['model_type'],
            'target_column': model_info['target_column'], 
            'feature_columns': feature_columns,
            'r2_score': model_info['r2_score'],
            'mae': model_info['mae'],
            'rmse': model_info['rmse'],
            'created_at': model_info['created_at']
        }
