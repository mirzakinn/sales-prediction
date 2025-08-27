"""
Results Workflow Service - Sonuçlar sayfası iş akışı
"""
from services.results_data_service import ResultsDataService
from services.results_filtering_service import ResultsFilteringService
from services.results_sorting_service import ResultsSortingService


class ResultsWorkflowService:
    """Sonuçlar sayfası iş akışını yöneten servis"""
    
    @staticmethod
    def process_results_request(date_filter, r2_filter, sort_by):
        """
        Sonuçlar sayfası için tam iş akışını işle
        
        Args:
            date_filter (str): Tarih filtresi
            r2_filter (str): R2 filtresi  
            sort_by (str): Sıralama kriteri
            
        Returns:
            dict: İşlenmiş sonuç verisi
        """
        # 1. Parametreleri doğrula
        validated_params = ResultsDataService.validate_filter_parameters(
            date_filter, r2_filter, sort_by
        )
        
        # 2. Tüm model verilerini al
        all_models = ResultsDataService.get_all_models_data()
        
        # 3. Eğer model yoksa boş sonuç döndür
        if not all_models:
            return {
                'success': True,
                'models': [],
                'filters': validated_params,
                'total_count': 0,
                'filtered_count': 0
            }
        
        # 4. Filtreleri uygula
        filtered_models = ResultsFilteringService.apply_all_filters(
            all_models, 
            validated_params['date_filter'], 
            validated_params['r2_filter']
        )
        
        # 5. Sırala
        sorted_models = ResultsSortingService.sort_models(
            filtered_models, 
            validated_params['sort_by']
        )
        
        # 6. Sonuçları döndür
        return {
            'success': True,
            'models': sorted_models,
            'filters': validated_params,
            'total_count': len(all_models),
            'filtered_count': len(sorted_models)
        }
    
    @staticmethod
    def get_empty_result_data(date_filter, r2_filter, sort_by):
        """
        Boş sonuç verisi döndür
        
        Args:
            date_filter (str): Tarih filtresi
            r2_filter (str): R2 filtresi
            sort_by (str): Sıralama kriteri
            
        Returns:
            dict: Boş sonuç verisi
        """
        validated_params = ResultsDataService.validate_filter_parameters(
            date_filter, r2_filter, sort_by
        )
        
        return {
            'success': True,
            'models': [],
            'filters': validated_params,
            'total_count': 0,
            'filtered_count': 0
        }
