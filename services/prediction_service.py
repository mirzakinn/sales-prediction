"""Tahmin servisleri"""

import pandas as pd
import numpy as np
from utils.file_utils import load_model_files

class PredictionService:
    """Tahmin işlemlerini yöneten servis sınıfı"""
    
    @staticmethod
    def make_prediction(model_id, input_data):
        """
        Eğitilmiş model ile tahmin yapar
        """
        # Model dosyalarını yükle
        model_files = load_model_files(model_id)
        model = model_files['model']
        encoders = model_files['encoders']
        scaler = model_files['scaler']
        
        # Veriyi işle
        processed_data = PredictionService._preprocess_input(
            input_data, encoders, scaler
        )
        
        # Tahmin yap
        prediction = model.predict(processed_data)
        
        return prediction
    
    @staticmethod
    def _preprocess_input(input_data, encoders, scaler):
        """
        Girdi verisini model için hazırlar
        """
        df = pd.DataFrame([input_data])
        
        # Kategorik verileri encode et
        for col, encoder in encoders.items():
            if col in df.columns:
                df[col] = encoder.transform(df[col])
        
        # Scaling uygula
        scaled_data = scaler.transform(df.values)
        
        return scaled_data
    
    @staticmethod
    def batch_prediction(model_id, input_file_path):
        """
        Toplu tahmin yapar
        """
        # Dosyayı oku
        df = pd.read_csv(input_file_path)
        
        # Model dosyalarını yükle
        model_files = load_model_files(model_id)
        model = model_files['model']
        encoders = model_files['encoders']
        scaler = model_files['scaler']
        
        # Veriyi işle
        processed_df = df.copy()
        
        # Kategorik verileri encode et
        for col, encoder in encoders.items():
            if col in processed_df.columns:
                processed_df[col] = encoder.transform(processed_df[col])
        
        # Scaling uygula
        scaled_data = scaler.transform(processed_df.values)
        
        # Tahmin yap
        predictions = model.predict(scaled_data)
        
        # Sonuçları DataFrame'e ekle
        df['prediction'] = predictions
        
        return df
