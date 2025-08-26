"""
Veri analizi ve işleme fonksiyonları
Bu dosya sizin veri analizi kodlarınız için hazırlanmıştır.
"""
import pandas as pd

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
        raise e

def handle_missing_data(df, method='drop'):
    """
    Eksik verileri belirtilen yönteme göre işler

    Args:
        df: DataFrame
        method: 'drop', 'mean', 'median'
    
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
    else:
        numeric_columns = df_processed.select_dtypes(include=['number']).columns
        columns = [col for col in columns if col in numeric_columns]

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
