"""
Session Management Service - Session verilerini yönetme
"""
import pandas as pd
import os


class SessionManagementService:
    """Session verilerini yönetme servisi"""
    
    @staticmethod
    def validate_training_session(session_data):
        """
        Eğitim için session verilerini doğrula
        
        Args:
            session_data (dict): Session verileri
            
        Returns:
            dict: Doğrulama sonucu
        """
        filename = session_data.get('current_file')
        target_column = session_data.get('target_column')
        feature_columns = session_data.get('feature_columns')
        
        if not filename:
            return {
                'valid': False,
                'message': 'Dosya bilgisi bulunamadı. Lütfen dosya yükleyin.'
            }
        
        if not target_column:
            return {
                'valid': False,
                'message': 'Hedef sütun seçilmemiş. Lütfen veri işleme sayfasına gidin.'
            }
        
        if not feature_columns:
            return {
                'valid': False,
                'message': 'Özellik sütunları seçilmemiş. Lütfen veri işleme sayfasına gidin.'
            }
        
        # Dosya varlığını kontrol et
        filepath = os.path.join('storage/uploads', filename)
        if not os.path.exists(filepath):
            return {
                'valid': False,
                'message': f'Dosya bulunamadı: {filename}'
            }
        
        return {
            'valid': True,
            'message': 'Session doğrulama başarılı'
        }
    
    @staticmethod
    def prepare_training_session_data(filename, target_column, feature_columns, model_type, 
                                    test_size, handle_missing, performance, model_id):
        """
        Eğitim sonrası session verilerini hazırla
        
        Args:
            filename (str): Dosya adı
            target_column (str): Hedef sütun
            feature_columns (list): Özellik sütunları
            model_type (str): Model tipi
            test_size (float): Test veri oranı
            handle_missing (str): Eksik veri işleme yöntemi
            performance (dict): Model performansı
            model_id (int): Model ID
            
        Returns:
            dict: Session verileri
        """
        return {
            'trained_model': {
                'filename': filename,
                'target_column': target_column,
                'feature_columns': feature_columns,
                'model_type': model_type,
                'test_size': test_size,
                'handle_missing': handle_missing,
                'performance': performance,
                'trained_at': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            'current_model_id': model_id,
            'current_model_ready': True
        }
    
    @staticmethod
    def extract_session_parameters(session_data):
        """
        Session'dan eğitim parametrelerini çıkar
        
        Args:
            session_data (dict): Session verileri
            
        Returns:
            dict: Eğitim parametreleri
        """
        return {
            'filename': session_data.get('current_file'),
            'target_column': session_data.get('target_column'),
            'feature_columns': session_data.get('feature_columns')
        }
    
    @staticmethod
    def update_session_with_training_results(session, session_updates):
        """
        Session'ı eğitim sonuçlarıyla güncelle
        
        Args:
            session: Flask session objesi
            session_updates (dict): Güncellenecek veriler
        """
        for key, value in session_updates.items():
            session[key] = value
