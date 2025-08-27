from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from services.prediction_workflow_service import PredictionWorkflowService
from services.prediction_session_service import PredictionSessionService

prediction_bp = Blueprint('prediction', __name__)

@prediction_bp.route('/make-prediction', methods=['GET', 'POST'])
def make_prediction():
    """
    Tahmin yapma sayfası - eğitilmiş modelle yeni tahminler yapar
    """
    # Eğitilmiş model var mı kontrol et
    trained_model = session.get('trained_model')
    if not trained_model:
        flash('Önce bir model eğitmelisiniz!', 'error')
        return redirect(url_for('upload.upload_file'))
    
    if request.method == 'POST':
        # Tam tahmin sürecini PredictionWorkflowService ile yürüt
        result = PredictionWorkflowService.execute_prediction_workflow(
            session, request.form, trained_model
        )
        
        if not result['success']:
            flash(result['message'], 'error')
            return redirect(url_for('prediction.make_prediction'))
        
        # Session'ı temizle
        PredictionSessionService.clean_prediction_session(session)
        
        # Sonucu göster
        return render_template('prediction_result.html',
                             prediction=result['prediction'],
                             input_data=result['input_data'],
                             model_info=trained_model)
    
    # GET isteği - Tahmin formunu göster
    form_data_result = PredictionWorkflowService.prepare_prediction_form_data(session, trained_model)
    
    return render_template('make_prediction.html', 
                         model_info=trained_model,
                         feature_columns=trained_model['feature_columns'],
                         column_types=form_data_result['column_types'],
                         categorical_values=form_data_result['categorical_values'])

@prediction_bp.route('/make-prediction-new', methods=['GET', 'POST'])
def make_prediction_new():
    """
    Yeni tahmin sayfası - seçili modelle direkt tahmin yapar
    Veri yükleme ve kolon seçme adımlarını atlar
    """
    if request.method == 'POST':
        # Yeni tahmin sürecini PredictionWorkflowService ile yürüt
        result = PredictionWorkflowService.execute_new_prediction_workflow(request.form)
        
        if not result['success']:
            flash(result['message'], 'error')
            return redirect(url_for('management.results'))
        
        # Session'a model bilgilerini kaydet
        session['prediction_model'] = result['session_prediction_model']
        session['trained_model'] = result['model_info_for_template']
        session['prediction_mode_active'] = True
        
        # Direkt tahmin sayfasına git
        flash(result['message'], 'success')
        return render_template('make_prediction.html', 
                             model_info=result['model_info_for_template'],
                             feature_columns=result['feature_columns'],
                             column_types=result['column_types'],
                             categorical_values=result['categorical_values'])
    else:
        # GET request - model seçilmeden gelindiyse
        flash('Önce bir model seçmelisiniz!', 'error') 
        return redirect(url_for('management.results'))



