"""Dosya işlemleri servisleri"""
import os
from werkzeug.utils import secure_filename
from config import DevelopmentConfig

class FileService:
    """Dosya işlemlerini yöneten servis sınıfı"""
    
    @staticmethod
    def allowed_file(filename):
        """Dosya uzantısının izin verilen türde olup olmadığını kontrol eder"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in DevelopmentConfig.ALLOWED_EXTENSIONS
    
    @staticmethod
    def ensure_directory(directory_path):
        """Klasörün var olduğundan emin olur"""
        os.makedirs(directory_path, exist_ok=True)
    
    @staticmethod
    def get_upload_path(filename):
        """Upload dosyası için tam path döner"""
        return os.path.join(DevelopmentConfig.UPLOAD_FOLDER, filename)
    
    @staticmethod
    def handle_file_upload(file):
        """
        Dosya upload işlemini tamamen handle eder
        
        Args:
            file: Flask request.files['file'] objesi
            
        Returns:
            dict: {
                'success': bool,
                'message': str,
                'data': dict or None
            }
        """
        try:
            # Dosya kontrolü
            if not file or file.filename == '':
                return {
                    'success': False,
                    'message': 'Dosya seçilmedi!'
                }
            
            # Dosya türü kontrolü
            if not FileService.allowed_file(file.filename):
                return {
                    'success': False,
                    'message': 'Geçersiz dosya türü. Sadece XLSX, XLS, CSV dosyaları desteklenir.'
                }
            
            # Upload klasörü oluştur
            FileService.ensure_directory(DevelopmentConfig.UPLOAD_FOLDER)
            
            # Dosyayı kaydet
            filename = secure_filename(file.filename)
            filepath = FileService.get_upload_path(filename)
            file.save(filepath)

            return {
                'success': True,
                'message': 'Dosya başarıyla yüklendi!',
                'data': {
                    'filename': filename,
                    'filepath': filepath
                }
            } 
        except Exception as e:
            return {
                'success': False,
                'message': f'Dosya yükleme hatası: {str(e)}'
            }
