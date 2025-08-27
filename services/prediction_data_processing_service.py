"""
Prediction Data Processing Service - Tahmin verilerini işleme
"""
import pandas as pd


class PredictionDataProcessingService:
    """Tahmin verilerini işleme servisi"""
    
    @staticmethod
    def process_prediction_input(prediction_data, feature_columns, model_objects):
        """
        Tahmin girdi verilerini işle
        
        Args:
            prediction_data (dict): Ham tahmin verileri
            feature_columns (list): Özellik sütunları
            model_objects (dict): Model objeleri (model, encoders, scaler)
            
        Returns:
            dict: İşlenmiş veri veya hata
        """
        try:
            # DataFrame oluştur
            input_df = pd.DataFrame([prediction_data])
            
            # Kategorik kolonları encode et
            encoded_df = PredictionDataProcessingService._encode_categorical_columns(
                input_df, model_objects['encoders']
            )
            
            # Feature'ları doğru sırayla al
            feature_df = encoded_df[feature_columns]
            
            # Scaling uygula
            scaled_data = model_objects['scaler'].transform(feature_df.values)
            
            # DataFrame ile tahmin için hazırla
            input_scaled_df = pd.DataFrame(scaled_data, columns=feature_columns)
            
            return {
                'success': True,
                'data': input_scaled_df,
                'message': 'Veri işleme başarılı'
            }
            
        except Exception as e:
            return {
                'success': False,
                'data': None,
                'message': f'Veri işleme hatası: {str(e)}'
            }
    
    @staticmethod
    def _encode_categorical_columns(input_df, encoders):
        """
        Kategorik kolonları encode et
        
        Args:
            input_df (DataFrame): Girdi DataFrame
            encoders (dict): Encoder objeleri
            
        Returns:
            DataFrame: Encode edilmiş DataFrame
        """
        encoded_df = input_df.copy()
        
        for col in encoded_df.columns:
            if col in encoders:
                try:
                    # Normal encoding
                    encoded_df[col] = encoders[col].transform([str(encoded_df[col].iloc[0])])[0]
                except:
                    # Bilinmeyen kategori varsa, en sık kullanılan kategoriyi kullan
                    most_common = encoders[col].classes_[0]
                    encoded_df[col] = encoders[col].transform([most_common])[0]
        
        return encoded_df
    
    @staticmethod
    def make_prediction(processed_data, model):
        """
        İşlenmiş veri ile tahmin yap
        
        Args:
            processed_data (DataFrame): İşlenmiş veri
            model: Eğitilmiş model
            
        Returns:
            dict: Tahmin sonucu veya hata
        """
        try:
            prediction = model.predict(processed_data)[0]
            
            return {
                'success': True,
                'prediction': round(prediction, 2),
                'message': 'Tahmin başarılı'
            }
            
        except Exception as e:
            return {
                'success': False,
                'prediction': None,
                'message': f'Tahmin hatası: {str(e)}'
            }
