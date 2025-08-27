"""
Results Sorting Service - Model sıralama işlemleri
"""


class ResultsSortingService:
    """Model sonuçlarını sıralama servisi"""
    
    @staticmethod
    def sort_models(models, sort_by):
        """
        Modelleri belirtilen kritere göre sırala
        
        Args:
            models (list): Model listesi
            sort_by (str): Sıralama kriteri (date_desc, date_asc, r2_desc, r2_asc)
            
        Returns:
            list: Sıralanmış model listesi
        """
        if not models:
            return models
        
        if sort_by == 'date_desc':
            return sorted(models, key=lambda x: x['created_at'], reverse=True)
        elif sort_by == 'date_asc':
            return sorted(models, key=lambda x: x['created_at'])
        elif sort_by == 'r2_desc':
            return sorted(models, key=lambda x: x['r2_score'], reverse=True)
        elif sort_by == 'r2_asc':
            return sorted(models, key=lambda x: x['r2_score'])
        else:
            # Varsayılan: tarihe göre azalan
            return sorted(models, key=lambda x: x['created_at'], reverse=True)
    
    @staticmethod
    def get_available_sort_options():
        """
        Mevcut sıralama seçeneklerini döndür
        
        Returns:
            dict: Sıralama seçenekleri ve açıklamaları
        """
        return {
            'date_desc': 'En Yeni Önce',
            'date_asc': 'En Eski Önce',
            'r2_desc': 'En İyi R² Skoru Önce',
            'r2_asc': 'En Düşük R² Skoru Önce'
        }
