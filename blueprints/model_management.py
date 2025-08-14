from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import json
import os
import pandas as pd
from utils.data_utils import read_file_by_extension, handle_missing_data, handle_outliers
from utils.ml_utils import *
from database.crud import *
from utils.file_utils import save_model_files, allowed_file

CURRENT_MODEL = None
CURRENT_ENCODERS = None
CURRENT_SCALER = None

management_bp = Blueprint('management', __name__)

@management_bp.route('/results')
def results():
    """
    Sonuçlar sayfası - eğitilmiş modellerin listesi
    """

    model_results = get_all_models()
    
    return render_template('results_new.html', results=model_results)

@management_bp.route('/delete-model/<int:model_id>', methods=['POST'])
def delete_model_route(model_id):
    """
    Model silme işlemi - Database'den ve dosya sisteminden siler
    """
    try:
        # Database'den model bilgilerini al (silmeden önce kontrol için)
        model = get_model_by_id(model_id)
        
        if not model:
            flash('Model bulunamadı!', 'error')
            return redirect(url_for('management.results'))
        
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
        return redirect(url_for('management.results'))
        
    except Exception as e:
        print(f"Model silme hatası: {e}")
        flash(f'Model silinirken hata oluştu: {str(e)}', 'error')
        return redirect(url_for('management.results'))
    