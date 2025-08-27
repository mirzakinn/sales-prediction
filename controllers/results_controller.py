"""
Sonuçlar Blueprint'i - Kullanıcı Odaklı ML Pipeline
Veri yükleme → Kolon seçimi → Model eğitimi → Tahmin yapma akışı
"""
from flask import Blueprint, render_template, request
from services.results_workflow_service import ResultsWorkflowService

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
    
    # Tam sonuçlar iş akışını ResultsWorkflowService ile yürüt
    result = ResultsWorkflowService.process_results_request(
        date_filter, r2_filter, sort_by
    )
    
    return render_template('results_new.html', 
                         results=result['models'],
                         filters=result['filters'],
                         total_count=result['total_count'],
                         filtered_count=result['filtered_count'])
