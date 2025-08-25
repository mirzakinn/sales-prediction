from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import pandas as pd
import os
from services.data_service import DataService
from services.model_service import ModelService
from utils.data_utils import read_file_by_extension
from models.database.crud import *

# Global değişkenleri burada tanımla
CURRENT_MODEL = None
CURRENT_ENCODERS = None
CURRENT_SCALER = None

training_bp = Blueprint('training', __name__)

@training_bp.route('/configure-model', methods=['GET', 'POST'])
def configure_model():
    """
    Model konfigürasyonu - kullanıcının seçtiği kolonlara göre model ayarları
    Prediction mode'da model eğitimi yapmaz, direkt tahmin yapar
    """
    if request.method == 'GET':
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
    
    # POST isteği - form gönderildiğinde
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
        
        return render_template('configure_model.html',
                             filename=filename,
                             target_column=target_column,
                             feature_columns=feature_columns,
                             missing_data=missing_data,
                             total_rows=len(df),
                             prediction_mode=False)
        
    except Exception as e:
        flash(f'Hata oluştu: {str(e)}', 'error')
        return redirect(url_for('processing.select_columns', filename=session.get('current_file')))

@training_bp.route('/train-model', methods=['POST'])
def train_model():
    """
    Model eğitimi - kullanıcının seçtiği parametrelerle model eğitir
    """
    try:
        global CURRENT_MODEL, CURRENT_ENCODERS, CURRENT_SCALER
        # Form verilerini al
        model_type = request.form.get('model_type')
        test_size = float(request.form.get('test_size', 0.2))
        handle_missing = request.form.get('handle_missing', 'drop')
        
        # Model parametrelerini al
        model_params = {}
        use_grid_search = 'use_grid_search' in request.form
        use_auto_model_selection = 'use_auto_model_selection' in request.form
        use_detailed_mode = 'use_detailed_mode' in request.form
        
        for key, value in request.form.items():
            if key not in ['model_type', 'test_size', 'handle_missing', 'use_grid_search', 'use_auto_model_selection', 'use_detailed_mode']:
                try:
                    # Sayısal değerleri dönüştür
                    if value.replace('.', '').replace('-', '').isdigit():
                        model_params[key] = float(value) if '.' in value else int(value)
                    elif value.lower() in ['true', 'false']:
                        model_params[key] = value.lower() == 'true'
                    else:
                        model_params[key] = value
                except:
                    model_params[key] = value
        
        filename = session.get('current_file')
        target_column = session.get('target_column')
        feature_columns = session.get('feature_columns')

        filepath = os.path.join('storage/uploads', filename)       
        df = read_file_by_extension(filepath, filename)

        # Veri işleme - DataService kullan
        processed_data = DataService.process_uploaded_file(
            filepath, filename, target_column, feature_columns,
            handle_missing=handle_missing, test_size=test_size
        )
        
        # Model eğitimi - ModelService kullan
        if use_auto_model_selection:
            result = ModelService.train_auto_model(
                processed_data['X_train'], processed_data['y_train'],
                processed_data['X_test'], processed_data['y_test'],
                detailed_mode=use_detailed_mode
            )
            model_type = result['model_type']  # Auto seçimde model tipini güncelle
        else:
            result = ModelService.train_single_model(
                processed_data['X_train'], processed_data['y_train'],
                processed_data['X_test'], processed_data['y_test'],
                model_type, model_params, use_grid_search
            )
        
        # Global değişkenlere ata
        CURRENT_MODEL = result['model']
        CURRENT_ENCODERS = processed_data['encoders']
        CURRENT_SCALER = processed_data['scaler']
        
        # Model performansı
        model_performance = result['performance']
        
        # Model kaydetme - ModelService kullan
        model_id, file_paths = ModelService.save_trained_model_complete(
            result, target_column, feature_columns, filename,
            processed_data['encoders'], processed_data['scaler']
        )
        
        # Model bilgilerini session'a kaydet
        session['trained_model'] = {
            'filename': filename,
            'target_column': target_column,
            'feature_columns': feature_columns,
            'model_type': model_type,
            'test_size': test_size,
            'handle_missing': handle_missing,
            'performance': model_performance,
            'trained_at': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Session'a model ID'sini kaydet (objeler değil)
        session['current_model_id'] = model_id
        session['current_model_ready'] = True
        return render_template('training_results.html', 
                             model_info=session['trained_model'],
                             performance=model_performance)
        
    except Exception as e:
        flash(f'Model eğitimi hatası: {str(e)}', 'error')
        return redirect(url_for('training.configure_model'))

