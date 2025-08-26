"""
Dosya yükleme Blueprint'i - Refactored
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.file_service import FileService

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """Dosya yükleme endpoint'i"""
    if request.method == 'GET':
        return render_template('upload.html')

    result = FileService.handle_file_upload(request.files.get('file'))
    
    if result['success']:
        flash(result['message'], 'success')
        return redirect(url_for('processing.select_columns', filename=result['data']['filename'], filepath=result['data']['filepath']))
    else:
        flash(result['message'], 'error')
        return redirect(url_for('main.index'))
