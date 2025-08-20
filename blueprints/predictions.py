from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import json
import pandas as pd
from database.crud import get_model_by_id

CURRENT_MODEL = None
CURRENT_ENCODERS = None
CURRENT_SCALER = None

prediction_bp = Blueprint('prediction', __name__)

@prediction_bp.route('/make-prediction', methods=['GET', 'POST'])
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
                    return redirect(url_for('prediction.make_prediction'))
            
            # Tahmin modunu kontrol et
            prediction_model = None
            model_objects = None
            
            if session.get('prediction_mode_active'):
                # PREDICTION MODE: Seçilen modeli kullan
                prediction_model = session.get('prediction_model')
                
                
                if not prediction_model:
                    flash('Tahmin modeli bulunamadı!', 'error')
                    return redirect(url_for('management.results'))
                
                # Model dosyalarını yükle
                from utils.file_utils import load_model_files
                model_objects = load_model_files(prediction_model['id'])
                
                
                if not model_objects:
                    flash('Model dosyaları yüklenemedi!', 'error')
                    return redirect(url_for('management.results'))
                
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
                # Normal eğitimden sonra tahmin yapma - Model ID'sinden dosya yükle
                
                # Önce session'dan model ID'sini almaya çalış
                current_model_id = session.get('current_model_id')
                current_model_ready = session.get('current_model_ready', False)
                
                if current_model_id and current_model_ready:
                    
                    # Model dosyalarından yükle
                    from utils.file_utils import load_model_files
                    model_objects = load_model_files(current_model_id)
                    
                    if model_objects:
                        # Dosyadan yüklenen model objelerini kullan
                        session_model = model_objects['model']
                        session_encoders = model_objects['encoders']
                        session_scaler = model_objects['scaler']
                        
                        # Kullanıcı verisini DataFrame'e çevir ve işle
                        input_df = pd.DataFrame([prediction_data])
                        
                        # Kategorik kolonları encode et
                        for col in input_df.columns:
                            if col in session_encoders:
                                try:
                                    input_df[col] = session_encoders[col].transform([str(prediction_data[col])])[0]
                                except:
                                    # Bilinmeyen kategori varsa, en sık kullanılan kategoriyi kullan
                                    most_common = session_encoders[col].classes_[0]
                                    input_df[col] = session_encoders[col].transform([most_common])[0]
                        
                        # Feature'ları doğru sırayla al ve scale et
                        feature_values = input_df[trained_model['feature_columns']].values
                        input_scaled = session_scaler.transform(feature_values)
                        
                        # Tahmin yap
                        prediction = session_model.predict(input_scaled)[0]
                    else:
                        flash('Model dosyaları yüklenemedi!', 'error')
                        return redirect(url_for('upload.upload_file'))
                    
                elif CURRENT_MODEL is not None and CURRENT_ENCODERS is not None and CURRENT_SCALER is not None:
                    
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
                else:
                    flash('Model objeleri bulunamadı. Lütfen önce bir model eğitin.', 'error')
                    return redirect(url_for('upload.upload_file'))
            
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
            return redirect(url_for('prediction.make_prediction'))
    
    # GET isteği - Tahmin formunu göster
    return render_template('make_prediction.html', 
                         model_info=trained_model,
                         feature_columns=trained_model['feature_columns'])

@prediction_bp.route('/make-prediction-new', methods=['GET', 'POST'])
def make_prediction_new():
    """
    Yeni tahmin sayfası - seçili modelle direkt tahmin yapar
    Veri yükleme ve kolon seçme adımlarını atlar
    """
    
    if request.method == 'POST':
        
        try:
            # Form'dan model ID'sini al
            model_id = request.form.get('model_id')
            
            if not model_id:
                flash('Model ID eksik!', 'error')
                return redirect(url_for('management.results'))
            
            # Database'den model bilgilerini al
            model_info = get_model_by_id(int(model_id))
            
            if not model_info:
                flash('Model veritabanında bulunamadı!', 'error')
                return redirect(url_for('management.results'))
            
            # Debug: feature_columns'u kontrol et
            
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
            pass
            flash(f'Model yükleme hatası: {str(e)}', 'error')
            return redirect(url_for('management.results'))
    
    else:
        # GET request - model seçilmeden gelindiyse
        flash('Önce bir model seçmelisiniz!', 'error') 
        return redirect(url_for('management.results'))



