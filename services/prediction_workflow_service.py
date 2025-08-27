"""
Prediction Workflow Service - Tahmin sürecini orkestrasyon
"""
from services.prediction_form_service import PredictionFormService
from services.prediction_model_service import PredictionModelService
from services.prediction_data_processing_service import PredictionDataProcessingService
from services.prediction_session_service import PredictionSessionService
from services.prediction_validation_service import PredictionValidationService
from services.categorical_info_service import CategoricalInfoService


class PredictionWorkflowService:
    """Tahmin sürecini orkestrasyon servisi"""
    
    @staticmethod
    def execute_prediction_workflow(session_data, form_data, trained_model):
        """
        Tam tahmin sürecini yürüt
        
        Args:
            session_data (dict): Session verileri
            form_data (dict): Form verileri
            trained_model (dict): Eğitilmiş model bilgileri
            
        Returns:
            dict: Tahmin sonucu
        """
        # 1. Form verilerini çıkar ve doğrula
        form_result = PredictionFormService.extract_prediction_data(
            form_data, trained_model['feature_columns']
        )
        
        if not form_result['success']:
            return PredictionWorkflowService._create_error_response(form_result['message'])
        
        prediction_data = form_result['data']
        
        # 2. Session doğrulama
        session_validation = PredictionSessionService.validate_session_for_prediction(session_data)
        if not session_validation['valid']:
            return PredictionWorkflowService._create_error_response(session_validation['message'])
        
        # 3. Model objelerini yükle
        session_info = PredictionSessionService.get_session_model_info(session_data)
        if session_info['prediction_mode_active']:
            model_result = PredictionModelService.get_prediction_mode_model(session_data)
        else:
            model_result = PredictionModelService.get_current_model_objects(session_data)
        
        if not model_result['success']:
            return PredictionWorkflowService._create_error_response(model_result['message'])
        
        model_objects = model_result['data']
        
        # 4. Model objelerini doğrula
        validation_result = PredictionValidationService.validate_model_objects(model_objects)
        if not validation_result['valid']:
            return PredictionWorkflowService._create_error_response(validation_result['message'])
        
        # 5. Veriyi işle
        processing_result = PredictionDataProcessingService.process_prediction_input(
            prediction_data, trained_model['feature_columns'], model_objects
        )
        
        if not processing_result['success']:
            return PredictionWorkflowService._create_error_response(processing_result['message'])
        
        # 6. Tahmin yap
        prediction_result = PredictionDataProcessingService.make_prediction(
            processing_result['data'], model_objects['model']
        )
        
        if not prediction_result['success']:
            return PredictionWorkflowService._create_error_response(prediction_result['message'])
        
        return {
            'success': True,
            'prediction': prediction_result['prediction'],
            'input_data': prediction_data,
            'message': 'Tahmin başarıyla tamamlandı'
        }
    
    @staticmethod
    def prepare_prediction_form_data(session_data, trained_model):
        """
        Tahmin formu için veriyi hazırla
        
        Args:
            session_data (dict): Session verileri
            trained_model (dict): Eğitilmiş model bilgileri
            
        Returns:
            dict: Form için hazırlanmış veri
        """
        current_model_id = session_data.get('current_model_id')
        column_info = CategoricalInfoService.prepare_form_column_info(
            session_data, current_model_id, trained_model['feature_columns']
        )
        
        return {
            'success': True,
            'column_types': column_info['column_types'],
            'categorical_values': column_info['categorical_values'],
            'message': 'Form verileri hazırlandı'
        }
    
    @staticmethod
    def execute_new_prediction_workflow(form_data):
        """
        Yeni tahmin sürecini yürüt (model seçimi ile)
        
        Args:
            form_data (dict): Form verileri
            
        Returns:
            dict: İşlem sonucu
        """
        # 1. Model ID'sini doğrula
        model_id = form_data.get('model_id')
        id_validation = PredictionValidationService.validate_model_id(model_id)
        if not id_validation['valid']:
            return PredictionWorkflowService._create_error_response(id_validation['message'])
        
        # 2. Database'den model bilgilerini al
        model_result = PredictionModelService.load_model_from_database(int(model_id))
        if not model_result['success']:
            return PredictionWorkflowService._create_error_response(model_result['message'])
        
        model_info = model_result['data']
        
        # 3. Feature columns'ları parse et
        feature_columns = PredictionFormService.parse_feature_columns(
            model_info['feature_columns']
        )
        
        # 4. Template için model bilgilerini hazırla
        model_info_for_template = PredictionFormService.prepare_model_info_for_template(
            model_info, feature_columns
        )
        
        # 5. Session için prediction model bilgilerini hazırla
        session_prediction_model = PredictionFormService.prepare_session_prediction_model(
            model_info, feature_columns
        )
        
        # 6. Column types ve categorical values'ları hazırla
        column_info = CategoricalInfoService.prepare_form_column_info(
            {}, model_info['id'], feature_columns
        )
        
        return {
            'success': True,
            'model_info_for_template': model_info_for_template,
            'session_prediction_model': session_prediction_model,
            'feature_columns': feature_columns,
            'column_types': column_info['column_types'],
            'categorical_values': column_info['categorical_values'],
            'message': f'{model_info["model_type"].title()} modeli ile tahmin yapabilirsiniz.'
        }
    
    @staticmethod
    def _create_error_response(message):
        """
        Hata yanıtı oluştur
        
        Args:
            message (str): Hata mesajı
            
        Returns:
            dict: Hata yanıtı
        """
        return {
            'success': False,
            'message': message
        }
