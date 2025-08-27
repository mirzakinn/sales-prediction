"""Dosya analizi servisleri"""

import pandas as pd
import os
from utils.data_utils import read_file_by_extension

class AnalysisService:
    """Dosya analizi işlemlerini yöneten servis sınıfı"""
    
    @staticmethod
    def get_preview_data(df, rows=5):
        """Preview data hazırlama"""
        try:
            preview_data = df.head(rows).fillna('').to_dict('records')
            # Çok uzun değerleri kısalt
            for row in preview_data:
                for key, value in row.items():
                    if isinstance(value, str) and len(str(value)) > 50:
                        row[key] = str(value)[:50] + "..."
            return preview_data
        except Exception:
            return []
    
    @staticmethod
    def determine_column_types(df):
        """Kolon tiplerini otomatik belirle"""
        column_types = {}
        columns = df.columns.tolist()
        
        for col in columns:
            try:
                dtype = str(df[col].dtype)
                # Numeric olmaya çalış
                if 'int' in dtype or 'float' in dtype:
                    column_types[col] = 'sayısal'
                else:
                    # String bir kolonu numeric'e çevirmeyi dene
                    try:
                        pd.to_numeric(df[col].dropna().head(10), errors='raise')
                        column_types[col] = 'sayısal'
                    except:
                        # Kategorik veri olarak kabul et
                        unique_values = df[col].nunique()
                        total_values = len(df[col].dropna())
                        
                        # Eğer unique değer sayısı toplam değerlerin %50'sinden azsa kategorik
                        if unique_values < total_values * 0.5:
                            column_types[col] = 'kategorik'
                        else:
                            column_types[col] = 'metin'  # Çok fazla unique değer varsa metin
            except Exception:
                column_types[col] = 'kategorik'  # Hata durumunda kategorik kabul et
        
        return column_types
    
    @staticmethod
    def clean_dataframe(df):
        """DataFrame temizleme"""
        # Kolon adlarını temizle (boşlukları kaldır, özel karakterleri düzelt)
        df.columns = df.columns.str.strip()
        return df
    
    @staticmethod
    def load_dataframe(filepath, filename):
        """Dosyayı yükle ve temel DataFrame kontrolleri yap"""
        try:
            # Dosyayı oku
            df = read_file_by_extension(filepath, filename)
            
            # Boş DataFrame kontrolü
            if df.empty:
                return {
                    'valid': False,
                    'message': 'Dosya boş veya geçersiz!'
                }
            
            return {
                'valid': True,
                'dataframe': df
            }
            
        except Exception as e:
            return {
                'valid': False,
                'message': f'Dosya okuma hatası: {str(e)}'
            }
    
    @staticmethod
    def analyze_dataframe_structure(df):
        """DataFrame yapısını analiz et"""
        return {
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'dtypes': df.dtypes.to_dict(),
            'null_counts': df.isnull().sum().to_dict(),
            'memory_usage': df.memory_usage(deep=True).sum()
        }
