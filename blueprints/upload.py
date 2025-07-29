"""
Dosya yükleme Blueprint'i
"""
from flask import Blueprint, render_template, request, jsonify
import pandas as pd
import os
from werkzeug.utils import secure_filename
from utils.file_utils import allowed_file
from utils.data_utils import analyze_dataframe, read_file_by_extension

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """Dosya yükleme endpoint'i"""
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
                upload_folder = 'uploads'
                filepath = os.path.join(upload_folder, filename)
                file.save(filepath)
                
                # Dosya türüne göre okuma
                try:
                    df = read_file_by_extension(filepath, filename)
                    
                    # Veri analizi
                    analyze_dataframe(df, filename)
                    
                    # Başarılı response döndür
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
