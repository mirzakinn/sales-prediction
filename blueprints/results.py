"""
Sonuçlar Blueprint'i - Basit Web Sayfaları Yaklaşımı
API yok, sadece normal form gönderimi ve sayfa gösterimi
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
import json
import os

results_bp = Blueprint('results', __name__)

@results_bp.route('/results')
def results():
    """
    Sonuçlar sayfası
    
    TODO: Buraya kendi model sonuçlarınızı gösterecek kodu yazın
    """
    # Örnek veri - Kendi model sonuçlarınızla değiştirin
    sample_data = {
        'predictions': [100, 150, 200, 120, 180],
        'dates': ['2024-01', '2024-02', '2024-03', '2024-04', '2024-05'],
        'accuracy': 85.5,
        'message': 'Bu veriler örnek verilerdir. Kendi model sonuçlarınızla değiştirin.'
    }
    
    # JSON formatına çevir (frontend grafikler için)
    sample_data['dates_json'] = json.dumps(sample_data['dates'])
    sample_data['predictions_json'] = json.dumps(sample_data['predictions'])
    
    return render_template('results.html', data=sample_data)

@results_bp.route('/train-model', methods=['GET', 'POST'])
def train_model():
    """
    Model eğitimi sayfası - Basit form yaklaşımı
    
    GET: Model eğitim formunu göster
    POST: Form verilerini al ve modeli eğit
    """
    if request.method == 'POST':
        # Form verilerini al
        filename = request.form.get('filename')
        model_type = request.form.get('model_type', 'linear_regression')
        
        try:
            # Dosya kontrolü
            if not filename:
                flash('Dosya adı gerekli!', 'error')
                return redirect(url_for('results.train_model'))
            
            filepath = os.path.join('uploads', filename)
            if not os.path.exists(filepath):
                flash('Dosya bulunamadı!', 'error')
                return redirect(url_for('results.train_model'))
            
            # TODO: Buraya kendi model eğitim kodunuzu yazın
            # Örnek:
            # if filename.endswith('.csv'):
            #     df = pd.read_csv(filepath)
            # else:
            #     df = pd.read_excel(filepath)
            # 
            # # Veriyi hazırla
            # X, y = prepare_data(df)
            # 
            # # Modeli eğit
            # if model_type == 'linear_regression':
            #     model = LinearRegression()
            # else:
            #     model = RandomForestRegressor()
            # 
            # model.fit(X, y)
            # 
            # # Performans hesapla
            # score = model.score(X, y)
            
            # Şimdilik başarı mesajı
            flash(f'Model eğitimi başlatıldı! Dosya: {filename}, Model: {model_type}', 'success')
            return redirect(url_for('results.results'))
            
        except Exception as e:
            flash(f'Hata oluştu: {str(e)}', 'error')
            return redirect(url_for('results.train_model'))
    
    # GET isteği - Form sayfasını göster
    # Yüklenmiş dosyaları listele
    uploaded_files = []
    uploads_dir = 'uploads'
    if os.path.exists(uploads_dir):
        for file in os.listdir(uploads_dir):
            if file.endswith(('.csv', '.xlsx', '.xls')):
                uploaded_files.append(file)
    
    return render_template('train_model.html', uploaded_files=uploaded_files)

@results_bp.route('/make-prediction', methods=['GET', 'POST'])
def make_prediction():
    """
    Tahmin yapma sayfası - Basit form yaklaşımı
    
    GET: Tahmin formunu göster
    POST: Form verilerini al ve tahmin yap
    """
    if request.method == 'POST':
        try:
            # Form verilerini al
            # TODO: Burada form verilerinizi kendi modelinize göre ayarlayın
            feature1 = request.form.get('feature1', type=float)
            feature2 = request.form.get('feature2', type=float)
            
            if feature1 is None or feature2 is None:
                flash('Tüm alanları doldurun!', 'error')
                return redirect(url_for('results.make_prediction'))
            
            # TODO: Buraya kendi tahmin kodunuzu yazın
            # Örnek:
            # model = joblib.load('uploads/trained_model.pkl')
            # prediction = model.predict([[feature1, feature2]])
            
            # Şimdilik örnek tahmin
            example_prediction = (feature1 * 1.5) + (feature2 * 0.8) + 100
            
            flash(f'Tahmin sonucu: {example_prediction:.2f}', 'success')
            return render_template('prediction_result.html', 
                                 prediction=example_prediction,
                                 feature1=feature1, 
                                 feature2=feature2)
            
        except Exception as e:
            flash(f'Hata oluştu: {str(e)}', 'error')
            return redirect(url_for('results.make_prediction'))
    
    # GET isteği - Form sayfasını göster
    return render_template('make_prediction.html')
