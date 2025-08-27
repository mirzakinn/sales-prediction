"""
Results Data Service - Model verilerini işleme
"""
from models.database.crud import get_all_models


class ResultsDataService:
    """Sonuç verilerini işleme servisi"""
    
    @staticmethod
    def get_all_models_data():
        """
        Tüm modelleri veritabanından al ve dictionary formatına çevir
        
        Returns:
            list: Model dictionary'leri listesi
        """
        all_models = get_all_models()
        
        if not all_models:
            return []
        
        models = []
        for row in all_models:
            model = {
                'id': row[0],
                'model_type': row[1],
                'dataset_filename': row[2],
                'target_column': row[3],
                'feature_columns': row[4],
                'r2_score': row[5] if row[5] else 0,
                'mae': row[6] if row[6] else 0,
                'mse': row[7] if row[7] else 0,
                'rmse': row[8] if row[8] else 0,
                'model_params': row[9],
                'created_at': row[10]
            }
            models.append(model)
        
        return models
    
    @staticmethod
    def validate_filter_parameters(date_filter, r2_filter, sort_by):
        """
        Filtre parametrelerini doğrula
        
        Args:
            date_filter (str): Tarih filtresi
            r2_filter (str): R2 filtresi
            sort_by (str): Sıralama kriteri
            
        Returns:
            dict: Doğrulanmış parametreler
        """
        valid_date_filters = ['all', 'today', 'week', 'month']
        valid_r2_filters = ['all', 'high', 'medium', 'low']
        valid_sort_options = ['date_desc', 'date_asc', 'r2_desc', 'r2_asc']
        
        return {
            'date_filter': date_filter if date_filter in valid_date_filters else 'all',
            'r2_filter': r2_filter if r2_filter in valid_r2_filters else 'all',
            'sort_by': sort_by if sort_by in valid_sort_options else 'date_desc'
        }
