"""
Sonuçlar Blueprint'i - Kullanıcı Odaklı ML Pipeline
Veri yükleme → Kolon seçimi → Model eğitimi → Tahmin yapma akışı
"""
from flask import Blueprint, render_template, request
from models.database.crud import get_all_models
from datetime import datetime

# Global değişkenler - eğitilen model objeleri
CURRENT_MODEL = None
CURRENT_ENCODERS = None
CURRENT_SCALER = None

results_bp = Blueprint('results', __name__)

@results_bp.route('/results')
def results():
    """
    Sonuçlar sayfası - eğitilmiş modellerin listesi (filtreleme ile)
    """
    # Filtreleme parametrelerini al
    date_filter = request.args.get('date_filter', 'all')  # all, today, week, month
    r2_filter = request.args.get('r2_filter', 'all')     # all, high, medium, low
    sort_by = request.args.get('sort_by', 'date_desc')   # date_desc, date_asc, r2_desc, r2_asc
    
    # Tüm modelleri al
    all_models = get_all_models()
    
    if not all_models:
        return render_template('results_new.html', results=[], filters={
            'date_filter': date_filter,
            'r2_filter': r2_filter,
            'sort_by': sort_by
        })
    
    # Model objelerini oluştur
    class ModelObject:
        def __init__(self, row):
            self.id = row[0]
            self.model_type = row[1]
            self.dataset_filename = row[2]
            self.target_column = row[3]
            self.feature_columns = row[4]
            self.r2_score = row[5] if row[5] else 0
            self.mae = row[6] if row[6] else 0
            self.mse = row[7] if row[7] else 0
            self.rmse = row[8] if row[8] else 0
            self.model_params = row[9]
            self.created_at = row[10]
    
    models = [ModelObject(row) for row in all_models]
    
    # Tarihe göre filtreleme
    if date_filter != 'all':
        from datetime import datetime, timedelta
        now = datetime.now()
        
        if date_filter == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif date_filter == 'week':
            start_date = now - timedelta(days=7)
        elif date_filter == 'month':
            start_date = now - timedelta(days=30)
        
        filtered_models = []
        for model in models:
            try:
                model_date = datetime.strptime(model.created_at, '%Y-%m-%d %H:%M:%S')
                if model_date >= start_date:
                    filtered_models.append(model)
            except:
                # Tarih parse edilemezse modeli dahil et
                filtered_models.append(model)
        models = filtered_models
    
    # R2 skoruna göre filtreleme
    if r2_filter != 'all':
        if r2_filter == 'high':  # R2 > 0.8
            models = [m for m in models if m.r2_score > 0.8]
        elif r2_filter == 'medium':  # 0.5 < R2 <= 0.8
            models = [m for m in models if 0.5 < m.r2_score <= 0.8]
        elif r2_filter == 'low':  # R2 <= 0.5
            models = [m for m in models if m.r2_score <= 0.5]
    
    # Sıralama
    if sort_by == 'date_desc':
        models.sort(key=lambda x: x.created_at, reverse=True)
    elif sort_by == 'date_asc':
        models.sort(key=lambda x: x.created_at)
    elif sort_by == 'r2_desc':
        models.sort(key=lambda x: x.r2_score, reverse=True)
    elif sort_by == 'r2_asc':
        models.sort(key=lambda x: x.r2_score)
    
    return render_template('results_new.html', 
                         results=models,
                         filters={
                             'date_filter': date_filter,
                             'r2_filter': r2_filter,
                             'sort_by': sort_by
                         },
                         total_count=len(all_models),
                         filtered_count=len(models))
