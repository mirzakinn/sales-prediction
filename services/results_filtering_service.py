"""
Results Filtering Service - Model filtreleme işlemleri
"""
from datetime import datetime, timedelta


class ResultsFilteringService:
    """Model sonuçlarını filtreleme servisi"""
    
    @staticmethod
    def filter_by_date(models, date_filter):
        """
        Modelleri tarihe göre filtrele
        
        Args:
            models (list): Model listesi
            date_filter (str): Tarih filtresi (all, today, week, month)
            
        Returns:
            list: Filtrelenmiş model listesi
        """
        if date_filter == 'all':
            return models
        
        now = datetime.now()
        
        if date_filter == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif date_filter == 'week':
            start_date = now - timedelta(days=7)
        elif date_filter == 'month':
            start_date = now - timedelta(days=30)
        else:
            return models
        
        filtered_models = []
        for model in models:
            try:
                model_date = datetime.strptime(model['created_at'], '%Y-%m-%d %H:%M:%S')
                if model_date >= start_date:
                    filtered_models.append(model)
            except:
                # Tarih parse edilemezse modeli dahil et
                filtered_models.append(model)
        
        return filtered_models
    
    @staticmethod
    def filter_by_r2_score(models, r2_filter):
        """
        Modelleri R2 skoruna göre filtrele
        
        Args:
            models (list): Model listesi
            r2_filter (str): R2 filtresi (all, high, medium, low)
            
        Returns:
            list: Filtrelenmiş model listesi
        """
        if r2_filter == 'all':
            return models
        
        if r2_filter == 'high':  # R2 > 0.8
            return [m for m in models if m['r2_score'] > 0.8]
        elif r2_filter == 'medium':  # 0.5 < R2 <= 0.8
            return [m for m in models if 0.5 < m['r2_score'] <= 0.8]
        elif r2_filter == 'low':  # R2 <= 0.5
            return [m for m in models if m['r2_score'] <= 0.5]
        
        return models
    
    @staticmethod
    def apply_all_filters(models, date_filter, r2_filter):
        """
        Tüm filtreleri uygula
        
        Args:
            models (list): Model listesi
            date_filter (str): Tarih filtresi
            r2_filter (str): R2 filtresi
            
        Returns:
            list: Filtrelenmiş model listesi
        """
        # Tarihe göre filtrele
        filtered_models = ResultsFilteringService.filter_by_date(models, date_filter)
        
        # R2 skoruna göre filtrele
        filtered_models = ResultsFilteringService.filter_by_r2_score(filtered_models, r2_filter)
        
        return filtered_models
