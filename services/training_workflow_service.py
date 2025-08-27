"""
Training Workflow Service - Eğitim sürecini orkestrasyon
"""
from services.form_processing_service import FormProcessingService
from services.session_management_service import SessionManagementService
from services.training_service import TrainingService


class TrainingWorkflowService:
    """Eğitim sürecini orkestrasyon servisi"""
    
    @staticmethod
    def execute_complete_training_workflow(session_data, form_data):
        """
        Tam eğitim sürecini yürüt
        
        Args:
            session_data (dict): Session verileri
            form_data (dict): Form verileri
            
        Returns:
            dict: Tam eğitim sonucu
        """
        # 1. Session doğrulama
        session_validation = SessionManagementService.validate_training_session(session_data)
        if not session_validation['valid']:
            return TrainingWorkflowService._create_error_response(
                session_validation['message'], 'upload.upload_file'
            )
        
        # 2. Form doğrulama
        form_validation = FormProcessingService.validate_form_data(form_data)
        if not form_validation['valid']:
            return TrainingWorkflowService._create_error_response(
                form_validation['message'], 'configure_model.configure_model'
            )
        
        # 3. Form parametrelerini ayrıştır
        training_params = FormProcessingService.parse_training_form_parameters(form_data)
        
        # 4. Session parametrelerini çıkar
        session_params = SessionManagementService.extract_session_parameters(session_data)
        
        # 5. Veriyi işle
        data_result = TrainingService.process_training_data(
            session_params['filename'], 
            session_params['target_column'], 
            session_params['feature_columns'],
            training_params['handle_missing'], 
            training_params['test_size']
        )
        
        if not data_result['success']:
            return TrainingWorkflowService._create_error_response(
                data_result['message'], 'configure_model.configure_model'
            )
        
        # 6. Model eğit
        training_result = TrainingService.train_model_with_parameters(
            data_result['data'], training_params
        )
        
        if not training_result['success']:
            return TrainingWorkflowService._create_error_response(
                training_result['message'], 'configure_model.configure_model'
            )
        
        # 7. Sonuçları kaydet
        save_result = TrainingService.save_training_results(
            training_result['result'], 
            session_params['target_column'], 
            session_params['feature_columns'],
            session_params['filename'], 
            data_result['data']
        )
        
        if not save_result['success']:
            return TrainingWorkflowService._create_error_response(
                save_result['message'], 'configure_model.configure_model'
            )
        
        # 8. Session verilerini hazırla
        session_updates = SessionManagementService.prepare_training_session_data(
            session_params['filename'], 
            session_params['target_column'], 
            session_params['feature_columns'],
            training_result['model_type'], 
            training_params['test_size'],
            training_params['handle_missing'], 
            training_result['result']['performance'],
            save_result['model_id']
        )
        
        return {
            'success': True,
            'session_updates': session_updates,
            'performance': training_result['result']['performance'],
            'message': 'Model eğitimi başarıyla tamamlandı'
        }
    
    @staticmethod
    def _create_error_response(message, redirect_route):
        """
        Hata yanıtı oluştur
        
        Args:
            message (str): Hata mesajı
            redirect_route (str): Yönlendirilecek route
            
        Returns:
            dict: Hata yanıtı
        """
        return {
            'success': False,
            'message': message,
            'redirect': redirect_route
        }
