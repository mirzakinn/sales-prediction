from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from services.training_workflow_service import TrainingWorkflowService
from services.session_management_service import SessionManagementService


training_model_bp = Blueprint('training_model', __name__)

@training_model_bp.route('/train-model', methods=['POST'])
def train_model():
    """
    Model eğitimi - kullanıcının seçtiği parametrelerle model eğitir
    """
    # Tam eğitim sürecini TrainingWorkflowService ile yürüt
    result = TrainingWorkflowService.execute_complete_training_workflow(session, request.form)
    
    if not result['success']:
        flash(result['message'], 'error')
        return redirect(url_for(result['redirect']))
    
    # Session güncellemelerini uygula
    SessionManagementService.update_session_with_training_results(session, result['session_updates'])
    
    # Başarılı sonucu göster
    return render_template('training_results.html', 
                         model_info=session['trained_model'],
                         performance=result['performance'])
