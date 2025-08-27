"""Model konfigürasyon servisleri"""

import pandas as pd
import os
from config import DevelopmentConfig
from services.data_service import DataService

class ModelConfigurationService:
    """Model konfigürasyon işlemlerini yöneten servis sınıfı"""
    
    @staticmethod
    def validate_session_data(filename, target_column, feature_columns):
        """Session verilerinin geçerliliğini kontrol eder"""
        if not all([filename, target_column, feature_columns]):
            return {
                'valid': False,
                'message': 'Session bilgileri eksik. Lütfen kolon seçimini tekrar yapın.'
            }
        return {'valid': True}
    
    @staticmethod
    def validate_column_selection(target_column, feature_columns):
        """Kolon seçiminin geçerliliğini kontrol eder"""
        if not target_column or not feature_columns:
            return {
                'valid': False,
                'message': 'Hedef kolon ve en az bir özellik kolonu seçmelisiniz!'
            }
        return {'valid': True}
    
    @staticmethod
    def analyze_missing_data_for_columns(filepath, columns):
        """Belirtilen kolonlar için eksik veri analizi yapar"""
        try:
            df = pd.read_csv(filepath)
            missing_data = {}
            
            for col in columns:
                missing_count = df[col].isnull().sum()
                missing_data[col] = {
                    'count': int(missing_count),
                    'percentage': round((missing_count / len(df)) * 100, 2)
                }
            
            return {
                'success': True,
                'missing_data': missing_data,
                'total_rows': len(df)
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Eksik veri analizi hatası: {str(e)}'
            }
    
    @staticmethod
    def prepare_configuration_data(filename, target_column, feature_columns):
        """Model konfigürasyonu için gerekli verileri hazırlar"""
        # Dosya yolu oluştur
        filepath = os.path.join(DevelopmentConfig.UPLOAD_FOLDER, filename)
        
        # Tüm seçilen kolonları birleştir
        all_columns = [target_column] + feature_columns
        
        # Eksik veri analizi yap
        analysis_result = ModelConfigurationService.analyze_missing_data_for_columns(
            filepath, all_columns
        )
        
        if not analysis_result['success']:
            return analysis_result
        
        return {
            'success': True,
            'data': {
                'filename': filename,
                'target_column': target_column,
                'feature_columns': feature_columns,
                'missing_data': analysis_result['missing_data'],
                'total_rows': analysis_result['total_rows'],
                'prediction_mode': False
            }
        }
    
    @staticmethod
    def process_column_selection(target_column, feature_columns, filename):
        """Kolon seçimini işler ve analiz yapar"""
        try:
            # Kolon seçimi doğrulama
            validation = ModelConfigurationService.validate_column_selection(
                target_column, feature_columns
            )
            if not validation['valid']:
                return {
                    'success': False,
                    'message': validation['message']
                }
            
            # Konfigürasyon verilerini hazırla
            config_result = ModelConfigurationService.prepare_configuration_data(
                filename, target_column, feature_columns
            )
            
            if not config_result['success']:
                return config_result
            
            return {
                'success': True,
                'data': {
                    'target_column': target_column,
                    'feature_columns': feature_columns,
                    'missing_data': config_result['data']['missing_data']
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Kolon seçimi işleme hatası: {str(e)}'
            }
