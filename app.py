from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import pandas as pd
import os
from werkzeug.utils import secure_filename
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Güvenlik için değiştir
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Upload klasörünü oluştur
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        try:
            # Dosya kontrolü
            if 'file' not in request.files:
                return jsonify({
                    'success': False,
                    'message': 'Dosya seçilmedi'
                }), 400
                
            file = request.files['file']
            
            # Dosya boş mu kontrolü
            if file.filename == '':
                return jsonify({
                    'success': False,
                    'message': 'Dosya seçilmedi'
                }), 400
            
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # Dosya türüne göre okuma
                try:
                    if filename.endswith('.csv'):
                        df = pd.read_csv(filepath)
                    else:
                        df = pd.read_excel(filepath)
                    
                    # Veri analizi ve model eğitimi burada
                    print("=" * 50, flush=True)
                    print("📊 VERİ ANALİZİ BAŞLADI", flush=True)
                    print("=" * 50, flush=True)
                    print(f"📁 Dosya başarıyla okundu: {filename}", flush=True)
                    print(f"📏 Veri boyutu: {df.shape[0]} satır, {df.shape[1]} sütun", flush=True)
                    print(f"📋 Sütunlar: {list(df.columns)}", flush=True)
                    print("📖 İlk 5 satır:", flush=True)
                    print(df.head().to_string(), flush=True)
                    
                    # Veri tipi bilgileri
                    print("🔍 Veri tipleri:", flush=True)
                    for col, dtype in df.dtypes.items():
                        print(f"  {col}: {dtype}", flush=True)
                    
                    # Eksik veri kontrolü
                    missing_data = df.isnull().sum()
                    if missing_data.sum() > 0:
                        print("⚠️  Eksik veriler:", flush=True)
                        for col, count in missing_data[missing_data > 0].items():
                            print(f"  {col}: {count} eksik değer", flush=True)
                    else:
                        print("✅ Eksik veri bulunamadı", flush=True)
                    
                    print("=" * 50, flush=True)
                    


                    # Şimdilik başarılı response döndür
                    return jsonify({
                        'success': True,
                        'message': 'Dosya başarıyla yüklendi ve işlendi',
                        'filename': filename,
                        'rows': df.shape[0],
                        'columns': df.shape[1]
                    })
                    
                except Exception as read_error:
                    return jsonify({
                        'success': False,
                        'message': f'Dosya okuma hatası: {str(read_error)}'
                    }), 500
            else:
                return jsonify({
                    'success': False,
                    'message': 'Geçersiz dosya türü. Sadece XLSX, XLS, CSV dosyaları desteklenir.'
                }), 400
                
        except Exception as e:
            print(f"Upload hatası: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Dosya yükleme hatası: {str(e)}'
            }), 500
    
    return render_template('upload.html')

@app.route('/results')
def results():
    # BURASI SENİN YAPACAĞIN KISIM
    # Model sonuçlarını ve tahminleri burada göster
    # Örnek veri (gerçek verilerle değiştireceksin)
    sample_data = {
        'predictions': [100, 150, 200, 120, 180],
        'dates': ['2024-01', '2024-02', '2024-03', '2024-04', '2024-05'],
        'accuracy': 85.5
    }
    
    # JSON formatına çevir
    import json
    sample_data['dates_json'] = json.dumps(sample_data['dates'])
    sample_data['predictions_json'] = json.dumps(sample_data['predictions'])
    
    return render_template('results.html', data=sample_data)

@app.route('/predict', methods=['POST'])
def predict():
    # BURASI SENİN YAPACAĞIN KISIM
    # AJAX ile tahmin yapma endpoint'i
    # Örnek:
    # data = request.get_json()
    # prediction = your_model.predict(data)
    # return jsonify({'prediction': prediction})
    
    return jsonify({'prediction': 'Bu kısım henüz implement edilmedi'})

if __name__ == '__main__':
    print("Flask uygulaması başlatılıyor...")
    print(f"Upload klasörü: {app.config['UPLOAD_FOLDER']}")
    print(f"Desteklenen dosya türleri: {ALLOWED_EXTENSIONS}")
    app.run(debug=True, host='127.0.0.1', port=5000)