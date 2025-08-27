from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import os
from services.data_service import DataService
from config import DevelopmentConfig

processing_bp = Blueprint('processing', __name__)

@processing_bp.route('/select-columns/<filename>')
def select_columns(filename):
    """
    Kolon seçimi sayfası - kullanıcı hangi kolonları analiz edeceğini seçer
    """
    # Dosya yolunu oluştur
    filepath = os.path.join(DevelopmentConfig.UPLOAD_FOLDER, filename)
    
    # DataService ile dosya analizi yap
    result = DataService.analyze_file(filepath, filename)
    
    if not result['success']:
        flash(result['message'], 'error')
        return redirect(url_for('upload.upload_file'))
    
    # Başarılı analiz - session'a kaydet
    data = result['data']
    session['current_file'] = data['filename']
    session['file_columns'] = data['columns']
    session['column_types'] = data['column_types']
    
    return render_template('select_columns.html', 
                         filename=data['filename'],
                         columns=data['columns'],
                         column_types=data['column_types'],
                         preview_data=data['preview_data'],
                         df_shape=data['df_shape'])

@processing_bp.route('/clear-session')
def clear_session():
    """
    Session'ı temizler ve başa döner
    """
    session.clear()
    flash('Oturum temizlendi. Yeni bir analiz başlatabilirsiniz.', 'info')
    return redirect(url_for('main.index'))