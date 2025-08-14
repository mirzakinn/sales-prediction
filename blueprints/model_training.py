from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import pandas as pd
import os
from utils.data_utils import read_file_by_extension, handle_missing_data, handle_outliers
from utils.ml_utils import *
from database.crud import *
from utils.file_utils import save_model_files

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
        filepath = os.path.join('uploads', filename)
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
        filepath = os.path.join('uploads', filename)
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
        if model_type in ['ridge', 'lasso']:
            alpha = request.form.get('alpha', '1.0')
            try:
                model_params['alpha'] = float(alpha)
            except ValueError:
                model_params['alpha'] = 1.0  # Default değer
        elif model_type == 'elasticnet':
            alpha = request.form.get('alpha', '1.0')
            l1_ratio = request.form.get('l1_ratio', '0.5')
            try:
                model_params['alpha'] = float(alpha)
                model_params['l1_ratio'] = float(l1_ratio)
            except ValueError:
                model_params['alpha'] = 1.0
                model_params['l1_ratio'] = 0.5
        
        filename = session.get('current_file')
        target_column = session.get('target_column')
        feature_columns = session.get('feature_columns')

        filepath = os.path.join('uploads', filename)       
        df = read_file_by_extension(filepath, filename)

        # Seçilen kolonları filtrele
        selected_columns = [target_column] + feature_columns
        df_filtered = df[selected_columns].copy()
        
        # Eksik verileri işle
        df_processed = handle_missing_data(
        df_filtered, 
        method=handle_missing,
        target_column=target_column
        )
        
        df_processed = handle_outliers(
        df_processed,
        columns=selected_columns
        )

        if not all([filename, target_column, feature_columns, model_type]):
            flash('Eksik bilgiler var! Lütfen baştan başlayın.', 'error')
            return redirect(url_for('upload.upload_file'))


        df_processed, encoders = encoding_data(df_processed)
        _, x, y, scaler = scaling_data(df_processed,feature_columns, target_column)
        x_train, x_test, y_train, y_test = data_split(x, y, test_size)
        reg, y_pred, score = select_model(x_train, y_train, x_test, y_test, model_type, model_params)
        # Model objelerini global değişkenlere at
        CURRENT_MODEL = reg
        CURRENT_ENCODERS = encoders
        CURRENT_SCALER = scaler
        
        # Şimdilik örnek sonuçlar (siz gerçek ML kodunu yazacaksınız)
        model_performance = analyze_model(y_test, y_pred)
        
        # Model bilgilerini session'a kaydet
        session['trained_model'] = {
            'filename': filename,
            'target_column': target_column,
            'feature_columns': feature_columns,
            'model_type': model_type,
            'test_size': test_size,
            'handle_missing': handle_missing,
            'performance': model_performance,
            'trained_at': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')  # String'e çevir
        }

        model_id = save_trained_model(
            model_name="Model",
            algorithm=model_type,
            r2_score=model_performance["r2_score"],
            mae=model_performance["mae"],
            mse=model_performance["mse"],
            rmse=model_performance["rmse"],
            target_column=target_column,
            feature_columns=feature_columns,
            filename=filename,
            model_params=model_params
        )

        # Model dosyalarını kaydet
        file_paths = save_model_files(
            model_id=model_id,
            model_obj=CURRENT_MODEL,
            encoders_obj=CURRENT_ENCODERS,
            scaler_obj=CURRENT_SCALER
        )
        
        # Session'a model ID'sini kaydet (objeler değil)
        session['current_model_id'] = model_id
        session['current_model_ready'] = True
        
        flash(f'Model eğitildi! R² Score: {model_performance["r2_score"]:.3f}', 'success')
        
        flash(f'{model_type} modeli başarıyla eğitildi!', 'success')
        return render_template('training_results.html', 
                             model_info=session['trained_model'],
                             performance=model_performance)
        
    except Exception as e:
        flash(f'Model eğitimi hatası: {str(e)}', 'error')
        return redirect(url_for('training.configure_model'))

