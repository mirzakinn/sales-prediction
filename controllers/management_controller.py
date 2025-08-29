from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import os
from pathlib import Path
from models.database.crud import get_all_models, get_model_by_id, delete_model
from services.model_service import ModelService
from config import Config

management_bp = Blueprint('management', __name__)

@management_bp.route('/results')
def results():
    """
    Sonuçlar sayfası - eğitilmiş modellerin listesi
    """

    model_results = get_all_models()
    
    return render_template('results.html', models=model_results)

@management_bp.route('/reset-all-models', methods=['POST'])
def reset_all_models():
    """Tüm eğitilmiş modelleri siler"""
    try:
        deleted_count = ModelService.reset_all_models()
        flash(f'Tüm modeller başarıyla silindi! {deleted_count} model dosyası temizlendi.', 'success')
    except Exception as e:
        flash(f'Model silme işlemi sırasında hata oluştu: {str(e)}', 'error')
    
    return redirect(url_for('management.results'))

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
        base_path = Config.STORAGE_BASE_PATH
        
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
        
        flash(f'Model başarıyla silindi! (ID: {model_id})', 'success')
        return redirect(url_for('management.results'))
        
    except Exception as e:
        flash(f'Model silinirken hata oluştu: {str(e)}', 'error')
        return redirect(url_for('management.results'))
    