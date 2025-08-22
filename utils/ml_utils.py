import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# kategorik verileri sayısal hale getir
# label encoding ve one-hot encoding
def encoding_data(df):
    df_processed = df.copy()
    encoders = {}
    
    categorical_columns = df_processed.select_dtypes(include=['object']).columns
    for col in categorical_columns:
        encoder = LabelEncoder()
        df_processed[col] = encoder.fit_transform(df_processed[col])
        encoders[col] = encoder
    # label encoding ile kategorik veriler sayısal değerlere çevrildi
    return df_processed, encoders

def scaling_data(df, feature_columns, target_column):

    df_processed = df.copy()

    scaler = StandardScaler() # standardScaller ile her sütunun ortalaması 0, standart sapması 1 yapılır
    x = df_processed[feature_columns].values
    y = df_processed[target_column].values

    x = scaler.fit_transform(x) # feature kolonlarını scale ediyorum
    
    data = np.hstack((x, np.reshape(y, (-1, 1)))) # feature kolonu ile target kolonunu birleştiriyorum

    return data, x, y, scaler

def data_split(x, y, test_size):
    x_train, x_test, y_train, y_test = train_test_split(
    x, y, test_size=test_size, random_state=42)
    return x_train, x_test, y_train, y_test



def analyze_model(y_test, y_pred):
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    return {
        'mse': mse,
        'rmse': rmse,
        'mae': mae,
        'r2_score': r2,
        'accuracy': round(r2 * 100, 1)  # R² skorunu yüzdelik accuracy olarak ekle
    }
