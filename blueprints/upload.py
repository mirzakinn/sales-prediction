"""
Dosya yükleme Blueprint'i - Yeni Workflow
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
import pandas as pd
import os
from werkzeug.utils import secure_filename
from utils.file_utils import allowed_file
from utils.data_utils import analyze_dataframe, read_file_by_extension

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """Dosya yükleme endpoint'i - yeni workflow için güncellenmiş"""
    if request.method == 'POST':
        try:
            # Dosya kontrolü
            if 'file' not in request.files:
                flash('Dosya seçilmedi!', 'error')
                return redirect(url_for('upload.upload_file'))
                
            file = request.files['file']
            
            # Dosya boş mu kontrolü
            if file.filename == '':
                flash('Dosya seçilmedi!', 'error')
                return redirect(url_for('upload.upload_file'))
            
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_folder = 'uploads'
                
                # Upload klasörü yoksa oluştur
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                
                filepath = os.path.join(upload_folder, filename)
                file.save(filepath)
                
                # Dosya türüne göre okuma
                try:
                    df = read_file_by_extension(filepath, filename)
                    
                    # Veri analizi
                    analyze_dataframe(df, filename)
                    
                    # Başarılı yükleme sonrası kolon seçimine yönlendir
                    flash(f'Dosya başarıyla yüklendi! ({df.shape[0]} satır, {df.shape[1]} kolon)', 'success')
                    return redirect(url_for('processing.select_columns', filename=filename))
                    
                except Exception as read_error:
                    flash(f'Dosya okuma hatası: {str(read_error)}', 'error')
                    return redirect(url_for('upload.upload_file'))
            else:
                flash('Geçersiz dosya türü. Sadece XLSX, XLS, CSV dosyaları desteklenir.', 'error')
                return redirect(url_for('upload.upload_file'))
                
        except Exception as e:
            pass
            flash(f'Dosya yükleme hatası: {str(e)}', 'error')
            return redirect(url_for('upload.upload_file'))
    
    return render_template('upload.html')
