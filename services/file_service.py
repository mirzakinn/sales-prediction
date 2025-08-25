"""Dosya işlemleri servisleri"""

import os
import pandas as pd
from werkzeug.utils import secure_filename

class FileService:
    """Dosya işlemlerini yöneten servis sınıfı"""
    
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
    UPLOAD_FOLDER = 'storage/uploads'
    
    @staticmethod
    def allowed_file(filename):
        """Dosya uzantısının izin verilen türde olup olmadığını kontrol eder"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in FileService.ALLOWED_EXTENSIONS
    
    @staticmethod
    def save_uploaded_file(file):
        """Yüklenen dosyayı kaydeder"""
        if file and FileService.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(FileService.UPLOAD_FOLDER, filename)
            file.save(filepath)
            return filename, filepath
        return None, None
    
    @staticmethod
    def get_file_info(filepath):
        """Dosya hakkında bilgi döner"""
        if not os.path.exists(filepath):
            return None
        
        # Dosya boyutu
        file_size = os.path.getsize(filepath)
        
        # Dosya türüne göre satır sayısı
        try:
            if filepath.endswith('.csv'):
                df = pd.read_csv(filepath)
            else:
                df = pd.read_excel(filepath)
            
            return {
                'size': file_size,
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': df.columns.tolist()
            }
        except Exception as e:
            return {
                'size': file_size,
                'error': str(e)
            }
    
    @staticmethod
    def analyze_columns(filepath):
        """Kolonları analiz eder ve türlerini belirler"""
        try:
            if filepath.endswith('.csv'):
                df = pd.read_csv(filepath)
            else:
                df = pd.read_excel(filepath)
            
            column_info = {}
            for col in df.columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    column_info[col] = 'sayısal'
                else:
                    column_info[col] = 'kategorik'
            
            return df.columns.tolist(), column_info
        except Exception as e:
            return [], {}
    
    @staticmethod
    def export_predictions(predictions_df, filename):
        """Tahmin sonuçlarını dışa aktarır"""
        export_path = os.path.join('storage/exports', filename)
        predictions_df.to_csv(export_path, index=False)
        return export_path
