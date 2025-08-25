"""Veri işleme servisleri"""

import pandas as pd
import os
from utils.data_utils import read_file_by_extension, handle_missing_data, handle_outliers
from utils.ml_utils import encoding_data, scaling_data, data_split

class DataService:
    """Veri işleme işlemlerini yöneten servis sınıfı"""
    
    @staticmethod
    def process_uploaded_file(filepath, filename, target_column, feature_columns, 
                            handle_missing='drop', test_size=0.2):
        """
        Yüklenen dosyayı işler ve ML için hazırlar
        """
        # Dosyayı oku
        df = read_file_by_extension(filepath, filename)
        
        # Seçilen kolonları filtrele
        selected_columns = [target_column] + feature_columns
        df_filtered = df[selected_columns].copy()
        
        # Eksik verileri işle
        df_processed = handle_missing_data(
            df_filtered, 
            method=handle_missing,
            target_column=target_column
        )
        
        # Outlier'ları işle
        df_processed = handle_outliers(
            df_processed,
            columns=selected_columns
        )
        
        # Encoding ve scaling
        df_processed, encoders = encoding_data(df_processed)
        _, x, y, scaler = scaling_data(df_processed, feature_columns, target_column)
        
        # Train-test split
        x_train, x_test, y_train, y_test = data_split(x, y, test_size)
        
        return {
            'X_train': x_train,
            'X_test': x_test,
            'y_train': y_train,
            'y_test': y_test,
            'encoders': encoders,
            'scaler': scaler,
            'processed_df': df_processed
        }
    
    @staticmethod
    def analyze_missing_data(df, columns):
        """Eksik veri analizini yapar"""
        missing_data = {}
        for col in columns:
            missing_count = df[col].isnull().sum()
            missing_data[col] = {
                'count': int(missing_count),
                'percentage': round((missing_count / len(df)) * 100, 2)
            }
        return missing_data
