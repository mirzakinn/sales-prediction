from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import pandas as pd
import os
from services.data_service import DataService
from services.model_service import ModelService
from utils.data_utils import read_file_by_extension
from models.database.crud import *
from utils import globals


configure_model_bp = Blueprint('configure_model', __name__)

@configure_model_bp.route('/configure-model', methods=['GET'])
def configure_model():
    """
    Model konfigürasyonu sayfası - GET endpoint
    """
    # GET isteği - sayfa yenilendiğinde veya doğrudan erişimde
    filename = session.get('current_file')
    target_column = session.get('target_column')
    feature_columns = session.get('feature_columns')
    
    if not all([filename, target_column, feature_columns]):
        flash('Session bilgileri eksik. Lütfen kolon seçimini tekrar yapın.', 'error')
        return redirect(url_for('upload.upload_file'))
    
    # Eksik veri analizini tekrar yap
    filepath = os.path.join('storage/uploads', filename)
    df = pd.read_csv(filepath)
    
    missing_data = {}
    for col in [target_column] + feature_columns:
        missing_count = df[col].isnull().sum()
        missing_data[col] = {
            'count': int(missing_count),
            'percentage': round((missing_count / len(df)) * 100, 2)
        }
    
    return render_template('configure_model.html',
                         filename=filename,
                         target_column=target_column,
                         feature_columns=feature_columns,
                         missing_data=missing_data,
                         total_rows=len(df),
                         prediction_mode=False)

@configure_model_bp.route('/configure-model', methods=['POST'])
def configure_model_post():
    """
    Model konfigürasyonu form işleme - POST endpoint
    """
    try:
        # Form verilerini al
        target_column = request.form.get('target_column')
        feature_columns = request.form.getlist('feature_columns')
        
        if not target_column or not feature_columns:
            flash('Hedef kolon ve en az bir özellik kolonu seçmelisiniz!', 'error')
            return redirect(url_for('processing.select_columns', filename=session.get('current_file')))
        
        # Seçimleri session'a kaydet
        session['target_column'] = target_column
        session['feature_columns'] = feature_columns
        
        # NORMAL MODE: Veri ön işleme için gerekli bilgileri hazırla
        filename = session.get('current_file')
        filepath = os.path.join('storage/uploads', filename)
        df = pd.read_csv(filepath)
        
        # Seçilen kolonlardaki eksik veri sayısını hesapla
        missing_data = {}
        for col in [target_column] + feature_columns:
            missing_count = df[col].isnull().sum()
            missing_data[col] = {
                'count': int(missing_count),
                'percentage': round((missing_count / len(df)) * 100, 2)
            }
        
        return redirect(url_for('configure_model.configure_model'))

        
    except Exception as e:
        flash(f'Hata oluştu: {str(e)}', 'error')
        return redirect(url_for('processing.select_columns', filename=session.get('current_file')))
