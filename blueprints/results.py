"""
Sonuçlar Blueprint'i - Kullanıcı Odaklı ML Pipeline
Veri yükleme → Kolon seçimi → Model eğitimi → Tahmin yapma akışı
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import json
import os
import pandas as pd
from utils.data_utils import read_file_by_extension, handle_missing_data, handle_outliers
from utils.ml_utils import *

results_bp = Blueprint('results', __name__)

@results_bp.route('/results')
def results():
    """
    Sonuçlar sayfası - eğitilmiş modellerin listesi
    """
    # TODO: Burada gerçek eğitilmiş modelleri veritabanından veya dosyadan alabilirsiniz
    # Şimdilik örnek veriler gösteriyoruz
    model_results = [
        {
            'model_name': 'Linear Regression',
            'accuracy': 85.2,
            'dataset': 'sales_data.csv',
            'target_column': 'sales',
            'features': ['price', 'marketing_spend'],
            'trained_date': '2024-01-15'
        }
    ]
    
    return render_template('results.html', results=model_results)

@results_bp.route('/select-columns/<filename>')
def select_columns(filename):
    """
    Kolon seçimi sayfası - kullanıcı hangi kolonları analiz edeceğini seçer
    """
    try:
        filepath = os.path.join('uploads', filename)
        if not os.path.exists(filepath):
            flash('Dosya bulunamadı!', 'error')
            return redirect(url_for('upload.upload_file'))
        
        # CSV dosyasını oku ve kolonları al
        from utils.data_utils import read_file_by_extension
        df = read_file_by_extension(filepath, filename)
        
        # Boş DataFrame kontrolü
        if df.empty:
            flash('Dosya boş veya geçersiz!', 'error')
            return redirect(url_for('upload.upload_file'))
        
        # Kolon adlarını temizle (boşlukları kaldır, özel karakterleri düzelt)
        df.columns = df.columns.str.strip()
        columns = df.columns.tolist()
        
        # İlk 5 satırı önizleme için al - güvenli şekilde
        try:
            preview_data = df.head(5).fillna('').to_dict('records')
            # Çok uzun değerleri kısalt
            for row in preview_data:
                for key, value in row.items():
                    if isinstance(value, str) and len(str(value)) > 50:
                        row[key] = str(value)[:50] + "..."
        except Exception:
            preview_data = []
        
        # Kolon tiplerini belirle - daha güvenli
        column_types = {}
        for col in columns:
            try:
                dtype = str(df[col].dtype)
                # Numeric olmaya çalış
                if 'int' in dtype or 'float' in dtype:
                    column_types[col] = 'sayısal'
                else:
                    # String bir kolonu numeric'e çevirmeyi dene
                    try:
                        pd.to_numeric(df[col].dropna().head(10), errors='raise')
                        column_types[col] = 'sayısal'
                    except:
                        column_types[col] = 'metin'
            except Exception:
                column_types[col] = 'metin'
        
        # Dosya bilgilerini session'a kaydet
        session['current_file'] = filename
        session['file_columns'] = columns
        session['column_types'] = column_types
        
        return render_template('select_columns.html', 
                             filename=filename, 
                             columns=columns, 
                             column_types=column_types,
                             preview_data=preview_data,
                             df_shape=df.shape)
        
    except Exception as e:
        print(f"Select columns error: {str(e)}", flush=True)
        flash(f'Dosya işleme hatası: {str(e)}', 'error')
        return redirect(url_for('upload.upload_file'))

@results_bp.route('/configure-model', methods=['GET', 'POST'])
def configure_model():
    """
    Model konfigürasyonu - kullanıcının seçtiği kolonlara göre model ayarları
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
                             total_rows=len(df))
    
    # POST isteği - form gönderildiğinde
    try:
        # Form verilerini al
        target_column = request.form.get('target_column')
        feature_columns = request.form.getlist('feature_columns')
        
        if not target_column or not feature_columns:
            flash('Hedef kolon ve en az bir özellik kolonu seçmelisiniz!', 'error')
            return redirect(url_for('results.select_columns', filename=session.get('current_file')))
        
        # Seçimleri session'a kaydet
        session['target_column'] = target_column
        session['feature_columns'] = feature_columns
        
        # Veri ön işleme için gerekli bilgileri hazırla
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
                             total_rows=len(df))
        
    except Exception as e:
        flash(f'Hata oluştu: {str(e)}', 'error')
        return redirect(url_for('results.select_columns', filename=session.get('current_file')))

@results_bp.route('/train-model', methods=['POST'])
def train_model():
    """
    Model eğitimi - kullanıcının seçtiği parametrelerle model eğitir
    """
    try:
        # Form verilerini al
        model_type = request.form.get('model_type')
        test_size = float(request.form.get('test_size', 0.2))
        handle_missing = request.form.get('handle_missing', 'drop')
        
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
        reg, y_pred, score = select_model(x_train, y_train, x_test, y_test, model_type)
        # 4. Train/test split yap
        # 5. Modeli eğit
        # 6. Performans metriklerini hesapla
        # 7. Modeli kaydet
        
        # Şimdilik örnek sonuçlar (siz gerçek ML kodunu yazacaksınız)
        model_performance = analyze_model(y_test, y_pred)
        
        # Global değişkenlere model objelerini kaydet
        global CURRENT_MODEL, CURRENT_ENCODERS, CURRENT_SCALER
        CURRENT_MODEL = reg
        CURRENT_ENCODERS = encoders
        CURRENT_SCALER = scaler
        
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

        #
        print(f"Model Performance: {model_performance}")  # Debug için
        flash(f'Model eğitildi! R² Score: {model_performance["r2_score"]:.3f}', 'success')
        
        flash(f'{model_type} modeli başarıyla eğitildi!', 'success')
        return render_template('training_results.html', 
                             model_info=session['trained_model'],
                             performance=model_performance)
        
    except Exception as e:
        flash(f'Model eğitimi hatası: {str(e)}', 'error')
        return redirect(url_for('results.configure_model'))
    
    return render_template('train_model.html', uploaded_files=uploaded_files)

@results_bp.route('/make-prediction', methods=['GET', 'POST'])
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
        try:
            # Form verilerinden tahmin değerlerini al
            prediction_data = {}
            for feature in trained_model['feature_columns']:
                value = request.form.get(feature)
                if value:
                    # Sayısal değerleri float'a çevir
                    try:
                        prediction_data[feature] = float(value)
                    except ValueError:
                        prediction_data[feature] = value
                else:
                    flash(f'{feature} alanı boş bırakılamaz!', 'error')
                    return redirect(url_for('results.make_prediction'))
            
            # TODO: Buraya gerçek tahmin kodunu yazabilirsiniz
            # model = joblib.load(f"models/{trained_model['filename']}_{trained_model['model_type']}.pkl")
            # prediction = model.predict([list(prediction_data.values())])[0]
            
            # Global değişkenlerden model objelerini al
            global CURRENT_MODEL, CURRENT_ENCODERS, CURRENT_SCALER
            
            if CURRENT_MODEL is None:
                flash('Model bulunamadı! Lütfen modeli yeniden eğitin.', 'error')
                return redirect(url_for('upload.upload_file'))
            
            # Kullanıcı verisini DataFrame'e çevir
            input_df = pd.DataFrame([prediction_data])
            
            # Kategorik kolonları encode et (eğitimde olduğu gibi)
            for col in input_df.columns:
                if col in CURRENT_ENCODERS:
                    # String'e çevir ve encode et
                    input_df[col] = CURRENT_ENCODERS[col].transform([str(prediction_data[col])])[0]
            
            # Feature'ları doğru sırayla al ve scale et
            feature_values = input_df[trained_model['feature_columns']].values
            input_scaled = CURRENT_SCALER.transform(feature_values)
            
            # Gerçek tahmin yap
            prediction = CURRENT_MODEL.predict(input_scaled)[0]
            
            # Şimdilik örnek tahmin (siz gerçek kodu yazacaksınız)
            example_prediction = prediction  # Artık gerçek tahmin!
            
            return render_template('prediction_result.html',
                                 prediction=round(example_prediction, 2),
                                 input_data=prediction_data,
                                 model_info=trained_model)
            
        except Exception as e:
            flash(f'Tahmin yapma hatası: {str(e)}', 'error')
            return redirect(url_for('results.make_prediction'))
    
    # GET isteği - Tahmin formunu göster
    return render_template('make_prediction.html', 
                         model_info=trained_model,
                         feature_columns=trained_model['feature_columns'])

@results_bp.route('/clear-session')
def clear_session():
    """
    Session'ı temizler ve başa döner
    """
    session.clear()
    flash('Oturum temizlendi. Yeni bir analiz başlatabilirsiniz.', 'info')
    return redirect(url_for('main.index'))
