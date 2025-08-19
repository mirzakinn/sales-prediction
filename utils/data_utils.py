"""
Veri analizi ve işleme fonksiyonları
Bu dosya sizin veri analizi kodlarınız için hazırlanmıştır.
"""
import pandas as pd
import numpy as np

def analyze_dataframe(df, filename):
    """
    DataFrame'i analiz eder ve detayları yazdırır
    """
    print("=" * 50, flush=True)
    print("VERI ANALIZI BASLADI", flush=True)
    print("=" * 50, flush=True)
    print(f"Dosya basariyla okundu: {filename}", flush=True)
    print(f"Veri boyutu: {df.shape[0]} satir, {df.shape[1]} sutun", flush=True)
    print(f"Sutunlar: {list(df.columns)}", flush=True)
    
    # Sayısal kolonlar için temel istatistikler
    numeric_columns = df.select_dtypes(include=['number']).columns
    if len(numeric_columns) > 0:
        print(f"Sayisal kolonlar: {list(numeric_columns)}", flush=True)
    
    # Eksik veri kontrolü
    missing_data = df.isnull().sum()
    if missing_data.any():
        print("UYARI - Eksik veriler:", flush=True)
        for col, count in missing_data.items():
            if count > 0:
                print(f"   {col}: {count} eksik", flush=True)
    
    print("=" * 50, flush=True)

def read_file_by_extension(filepath, filename):
    """Dosya uzantısına göre dosyayı okur ve hata yönetimi yapar"""
    try:
        if filename.lower().endswith('.csv'):
            # CSV için farklı encoding ve separator denemeleriyapalım
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            separators = [',', ';', '\t']
            
            for encoding in encodings:
                for sep in separators:
                    try:
                        df = pd.read_csv(filepath, encoding=encoding, sep=sep)
                        # Eğer tek kolon geliyorsa ve virgül varsa, virgül ayıracı dene
                        if len(df.columns) == 1 and ',' in str(df.iloc[0, 0]):
                            df = pd.read_csv(filepath, encoding=encoding, sep=',')
                        
                        # Eğer veri başarıyla okunduysa
                        if len(df.columns) > 1 and len(df) > 0:
                            print(f"✅ CSV başarıyla okundu: encoding={encoding}, separator='{sep}'", flush=True)
                            return df
                    except Exception as e:
                        continue
            
            # Hiçbiri çalışmazsa varsayılan
            return pd.read_csv(filepath)
            
        elif filename.lower().endswith(('.xlsx', '.xls')):
            return pd.read_excel(filepath)
        else:
            raise ValueError(f"Desteklenmeyen dosya formatı: {filename}")
            
    except Exception as e:
        print(f"❌ Dosya okuma hatası: {str(e)}", flush=True)
        raise e

# TODO: Buraya kendi veri işleme fonksiyonlarınızı ekleyebilirsiniz
# Örnek fonksiyonlar:
# def clean_data(df): ...
# def handle_missing_values(df): ...
# def feature_engineering(df): ...
# def normalize_data(df): ...

# Dosyanın sonuna ekle:

def handle_missing_data(df, method='drop', target_column=None):
    """
    Eksik verileri belirtilen yönteme göre işler
    
    Args:
        df: DataFrame
        method: 'drop', 'mean', 'median'
        target_column: Hedef kolon (özel işlem için)
    
    Returns:
        İşlenmiş DataFrame
    """
    df_processed = df.copy()
    
    if method == 'drop': # eksik satırları sil
        df_processed = df_processed.dropna()
        
    elif method == 'mean': 
        # sayısal kolonlar için ortalama ile doldurma
        numeric_columns = df_processed.select_dtypes(include=['number']).columns
        
        for col in numeric_columns:
            if df_processed[col].isnull().any():
                mean_value = df_processed[col].mean()
                df_processed[col].fillna(mean_value, inplace=True)
        
        # kategorik kolonlar için mod ile doldurma
        categorical_columns = df_processed.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            if df_processed[col].isnull().any():
                mode_values = df_processed[col].mode()
                if len(mode_values) > 0:
                    mode_value = mode_values.iloc[0]
                else:
                    mode_value = 'Unknown'
                df_processed[col].fillna(mode_value, inplace=True)
                
    elif method == 'median':
        # sayısal kolonlar için medyan ile doldurma
        numeric_columns = df_processed.select_dtypes(include=['number']).columns
        
        for col in numeric_columns:
            if df_processed[col].isnull().any():
                median_value = df_processed[col].median()
                df_processed[col].fillna(median_value, inplace=True)
        
        # kategorik kolonlar için mod ile doldurma
        categorical_columns = df_processed.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            if df_processed[col].isnull().any():
                mode_values = df_processed[col].mode()
                if len(mode_values) > 0:
                    mode_value = mode_values.iloc[0]
                else:
                    mode_value = 'Unknown'
                df_processed[col].fillna(mode_value, inplace=True)
    
    return df_processed

def handle_outliers(df, columns=None): #Inter Quantile Range (IQR)
    df_processed = df.copy()

    if columns is None:
        columns = df_processed.select_dtypes(include=['number']).columns
    
    for col in columns:
        q1 = df_processed[col].quantile(0.25)
        q3 = df_processed[col].quantile(0.75)
        IQR = q3 - q1

        lower_limit = q1 - (1.5 * IQR)
        upper_limit = q3 + (1.5 * IQR)

        outlier_count = len(df_processed[(df_processed[col] < lower_limit) | (df_processed[col] > upper_limit)])

        if outlier_count > 0:
            df_processed[col] = df_processed[col].clip(lower_limit, upper_limit)

    return df_processed
