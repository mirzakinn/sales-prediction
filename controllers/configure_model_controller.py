from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from services.model_configuration_service import ModelConfigurationService
from config import DevelopmentConfig


configure_model_bp = Blueprint('configure_model', __name__)

@configure_model_bp.route('/configure-model', methods=['GET'])
def configure_model():
    """
    Model konfigürasyonu sayfası - GET endpoint
    """
    # Session verilerini al
    filename = session.get('current_file')
    target_column = session.get('target_column')
    feature_columns = session.get('feature_columns')
    
    # Session doğrulama
    validation = ModelConfigurationService.validate_session_data(
        filename, target_column, feature_columns
    )
    if not validation['valid']:
        flash(validation['message'], 'error')
        return redirect(url_for('upload.upload_file'))
    
    # Konfigürasyon verilerini hazırla
    result = ModelConfigurationService.prepare_configuration_data(
        filename, target_column, feature_columns
    )
    
    if not result['success']:
        flash(result['message'], 'error')
        return redirect(url_for('upload.upload_file'))
    
    return render_template('configure_model.html', **result['data'])

@configure_model_bp.route('/configure-model', methods=['POST'])
def configure_model_post():
    """
    Model konfigürasyonu form işleme - POST endpoint
    """
    # Form verilerini al
    target_column = request.form.get('target_column')
    feature_columns = request.form.getlist('feature_columns')
    filename = session.get('current_file')
    
    # Kolon seçimini işle
    result = ModelConfigurationService.process_column_selection(
        target_column, feature_columns, filename
    )
    
    if not result['success']:
        flash(result['message'], 'error')
        return redirect(url_for('processing.select_columns', filename=filename))
    
    # Seçimleri session'a kaydet
    session['target_column'] = result['data']['target_column']
    session['feature_columns'] = result['data']['feature_columns']
    
    return redirect(url_for('configure_model.configure_model'))
