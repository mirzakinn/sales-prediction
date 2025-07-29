"""
Dosya işlemleri için yardımcı fonksiyonlar
"""
import os

ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}

def allowed_file(filename):
    """Dosya uzantısının izin verilen türde olup olmadığını kontrol eder"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_folder(upload_folder):
    """Upload klasörünün var olduğundan emin olur"""
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
