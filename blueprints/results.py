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
from database.crud import *
from utils.file_utils import save_model_files, allowed_file

# Global değişkenler - eğitilen model objeleri
CURRENT_MODEL = None
CURRENT_ENCODERS = None
CURRENT_SCALER = None

results_bp = Blueprint('results', __name__)

@results_bp.route('/results')
def results():
    """
    Sonuçlar sayfası - eğitilmiş modellerin listesi
    """

    model_results = get_all_models()
    
    return render_template('results_new.html', results=model_results)

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
        global CURRENT_MODEL, CURRENT_ENCODERS, CURRENT_SCALER
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
        # Model objelerini global değişkenlere ata
        CURRENT_MODEL = reg
        CURRENT_ENCODERS = encoders
        CURRENT_SCALER = scaler
        # 4. Train/test split yap
        # 5. Modeli eğit
        # 6. Performans metriklerini hesapla
        # 7. Modeli kaydet
        
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
            feature_columns=feature_columns
        )

        print(f"Model database'e kaydedildi. ID: {model_id}")

        
        # Model dosyalarını kaydet
        file_paths = save_model_files(
            model_id=model_id,
            model_obj=CURRENT_MODEL,
            encoders_obj=CURRENT_ENCODERS,
            scaler_obj=CURRENT_SCALER
        )
        print(f"Model dosyaları kaydedildi: {file_paths}")
        
        print(f"Model Performance: {model_performance}")  # Debug için
        flash(f'Model eğitildi! R² Score: {model_performance["r2_score"]:.3f}', 'success')
        
        flash(f'{model_type} modeli başarıyla eğitildi!', 'success')
        return render_template('training_results.html', 
                             model_info=session['trained_model'],
                             performance=model_performance)
        
    except Exception as e:
        flash(f'Model eğitimi hatası: {str(e)}', 'error')
        return redirect(url_for('results.configure_model'))

@results_bp.route('/make-prediction', methods=['GET', 'POST'])
def make_prediction():
    """
    Tahmin yapma sayfası - eğitilmiş modelle yeni tahminler yapar
    """
    global CURRENT_MODEL, CURRENT_ENCODERS, CURRENT_SCALER
    
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
            
            # Normal model eğitiminden sonra tahmin yapma durumu
            if session.get('prediction_mode_active'):
                # PREDICTION MODE: Seçilen modeli kullan
                prediction_model = session.get('prediction_model')
                
                print(f"🔍 Prediction model from session: {prediction_model}")
                
                if not prediction_model:
                    flash('Tahmin modeli bulunamadı!', 'error')
                    return redirect(url_for('results.results'))
                
                # Model dosyalarını yükle
                from utils.file_utils import load_model_files
                model_objects = load_model_files(prediction_model['id'])
                
                print(f"🔍 Model objects loaded: {model_objects is not None}")
                
                if not model_objects:
                    flash('Model dosyaları yüklenemedi!', 'error')
                    return redirect(url_for('results.results'))
                    
                # Kategorik kolonları encode et
                encoders = model_objects['encoders']
                # Feature'ları doğru sırayla al ve scale et
                feature_values = pd.DataFrame([prediction_data])[trained_model['feature_columns']].values
                scaler = model_objects['scaler']
                input_scaled = scaler.transform(feature_values)
                # Tahmin yap
                model = model_objects['model']
                prediction = model.predict(input_scaled)[0]
            else:
                # Normal eğitimden sonra tahmin yapma - Global değişkenleri kullan
                print("🔍 Using current session trained model with global variables")
                
                # Global değişkenlerin tanımlı olup olmadığını kontrol et
                try:
                    print(f"CURRENT_MODEL exists: {CURRENT_MODEL is not None}")
                    print(f"CURRENT_ENCODERS exists: {CURRENT_ENCODERS is not None}")
                    print(f"CURRENT_SCALER exists: {CURRENT_SCALER is not None}")
                except NameError as e:
                    flash('Model objeleri bulunamadı. Lütfen önce bir model eğitin.', 'error')
                    return redirect(url_for('upload.upload_file'))
                
                # Kullanıcı verisini DataFrame'e çevir ve işle
                input_df = pd.DataFrame([prediction_data])
                
                # Kategorik kolonları encode et
                for col in input_df.columns:
                    if col in CURRENT_ENCODERS:
                        try:
                            input_df[col] = CURRENT_ENCODERS[col].transform([str(prediction_data[col])])[0]
                        except:
                            # Bilinmeyen kategori varsa, en sık kullanılan kategoriyi kullan
                            most_common = CURRENT_ENCODERS[col].classes_[0]
                            input_df[col] = CURRENT_ENCODERS[col].transform([most_common])[0]
                
                # Feature'ları doğru sırayla al ve scale et
                feature_values = input_df[trained_model['feature_columns']].values
                input_scaled = CURRENT_SCALER.transform(feature_values)
                
                # Tahmin yap
                prediction = CURRENT_MODEL.predict(input_scaled)[0]
            
            # Session'ı temizle
            session.pop('prediction_mode_active', None)
            session.pop('prediction_mode', None)
            
            # Sonucu göster
            return render_template('prediction_result.html',
                                 prediction=round(prediction, 2),
                                 input_data=prediction_data,
                                 model_info=trained_model)
            
        except Exception as e:
            flash(f'Tahmin yapma hatası: {str(e)}', 'error')
            return redirect(url_for('results.make_prediction'))
    
    # GET isteği - Tahmin formunu göster
    return render_template('make_prediction.html', 
                         model_info=trained_model,
                         feature_columns=trained_model['feature_columns'])

@results_bp.route('/make-prediction-new', methods=['GET', 'POST'])
def make_prediction_new():
    """
    Yeni tahmin sayfası - seçili modelle direkt tahmin yapar
    Veri yükleme ve kolon seçme adımlarını atlar
    """
    print("🔥 make_prediction_new route called!")
    print(f"Request method: {request.method}")
    
    if request.method == 'POST':
        print("🔥 POST request received!")
        print(f"Form data: {request.form.to_dict()}")
        
        try:
            # Form'dan model ID'sini al
            model_id = request.form.get('model_id')
            
            if not model_id:
                flash('Model ID eksik!', 'error')
                return redirect(url_for('results.results'))
            
            # Database'den model bilgilerini al
            model_info = get_model_by_id(int(model_id))
            
            if not model_info:
                flash('Model veritabanında bulunamadı!', 'error')
                return redirect(url_for('results.results'))
            
            # Debug: feature_columns'u kontrol et
            print(f"Raw feature_columns: {model_info['feature_columns']}")
            print(f"Type: {type(model_info['feature_columns'])}")
            
            # Feature kolonlarını güvenli şekilde parse et
            feature_columns_raw = model_info['feature_columns']
            
            # Farklı formatları handle et
            if isinstance(feature_columns_raw, list):
                feature_columns = feature_columns_raw
            elif isinstance(feature_columns_raw, str):
                # Python liste string'i ise (örn: "['col1', 'col2']")
                if (feature_columns_raw.startswith('[') and feature_columns_raw.endswith(']')):
                    try:
                        # Önce JSON olarak dene
                        feature_columns = json.loads(feature_columns_raw)
                    except json.JSONDecodeError:
                        # JSON başarısız olursa literal_eval kullan
                        import ast
                        feature_columns = ast.literal_eval(feature_columns_raw)
                else:
                    # Tek string ise listeye çevir
                    feature_columns = [feature_columns_raw]
            else:
                feature_columns = []
            
            print(f"Parsed feature_columns: {feature_columns}")
            
            # Model bilgilerini hazırla (make_prediction template'i için)
            model_info_for_template = {
                'model_type': model_info['model_type'],
                'filename': 'Seçilen Model',
                'target_column': model_info['target_column'],
                'feature_columns': feature_columns,
                'performance': {
                    'accuracy': round(model_info['r2_score'] * 100, 1) if model_info['r2_score'] else 0,
                    'r2_score': model_info['r2_score']
                }
            }
            
            # Model bilgilerini session'a kaydet (tahmin için)
            session['prediction_model'] = {
                'id': model_info['id'],
                'model_type': model_info['model_type'],
                'target_column': model_info['target_column'], 
                'feature_columns': feature_columns,
                'r2_score': model_info['r2_score'],
                'mae': model_info['mae'],
                'rmse': model_info['rmse'],
                'created_at': model_info['created_at']
            }
            
            # Session'a trained_model bilgilerini kaydet ve prediction mode'u aktif et
            session['trained_model'] = model_info_for_template
            session['prediction_mode_active'] = True
            
            # Direkt tahmin sayfasına git
            flash(f'{model_info["model_type"].title()} modeli ile tahmin yapabilirsiniz.', 'success')
            return render_template('make_prediction.html', 
                                 model_info=model_info_for_template,
                                 feature_columns=feature_columns)
                                 
        except Exception as e:
            print(f"Make prediction new hatası: {e}")
            import traceback
            traceback.print_exc()
            flash(f'Model yükleme hatası: {str(e)}', 'error')
            return redirect(url_for('results.results'))
    
    else:
        # GET request - model seçilmeden gelindiyse
        flash('Önce bir model seçmelisiniz!', 'error') 
        return redirect(url_for('results.results'))

@results_bp.route('/clear-session')
def clear_session():
    """
    Session'ı temizler ve başa döner
    """
    session.clear()
    flash('Oturum temizlendi. Yeni bir analiz başlatabilirsiniz.', 'info')
    return redirect(url_for('main.index'))

@results_bp.route('/delete-model/<int:model_id>', methods=['POST'])
def delete_model_route(model_id):
    """
    Model silme işlemi - Database'den ve dosya sisteminden siler
    """
    try:
        # Database'den model bilgilerini al (silmeden önce kontrol için)
        model = get_model_by_id(model_id)
        
        if not model:
            flash('Model bulunamadı!', 'error')
            return redirect(url_for('results.results'))
        
        # Database'den modeli sil
        delete_model(model_id)
        
        # Model dosyalarını da sil
        import os
        from pathlib import Path
        
        base_path = Path(__file__).parent.parent / 'storage'
        
        files_to_delete = [
            base_path / 'models' / f'model_{model_id}.pkl',
            base_path / 'encoders' / f'encoder_{model_id}.pkl',
            base_path / 'scalers' / f'scaler_{model_id}.pkl'
        ]
        
        # Dosyaları sil (varsa)
        deleted_files = []
        for file_path in files_to_delete:
            if file_path.exists():
                os.remove(file_path)
                deleted_files.append(file_path.name)
        
        print(f"Model silindi - ID: {model_id}")
        print(f"Silinen dosyalar: {deleted_files}")
        
        flash(f'Model başarıyla silindi! (ID: {model_id})', 'success')
        return redirect(url_for('results.results'))
        
    except Exception as e:
        print(f"Model silme hatası: {e}")
        flash(f'Model silinirken hata oluştu: {str(e)}', 'error')
        return redirect(url_for('results.results'))
