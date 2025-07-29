"""
Veri analizi ve işleme fonksiyonları
Bu dosya sizin veri analizi kodlarınız için hazırlanmıştır.
"""
import pandas as pd

def analyze_dataframe(df, filename):
    """
    DataFrame'i analiz eder ve detayları yazdırır
    
    TODO: Buraya kendi veri analizi kodunuzu yazabilirsiniz
    Örneğin:
    - Eksik veri kontrolü
    - Veri tipleri analizi
    - İstatistiksel özetler
    - Korelasyon analizi
    - Outlier tespiti
    """

    print("=" * 50, flush=True)
    print("📊 VERİ ANALİZİ BAŞLADI", flush=True)
    print("=" * 50, flush=True)
    print(f"📁 Dosya başarıyla okundu: {filename}", flush=True)
    print(f"📏 Veri boyutu: {df.shape[0]} satır, {df.shape[1]} sütun", flush=True)
    print(f"📋 Sütunlar: {list(df.columns)}", flush=True)
    
    # TODO: Buraya kendi analiz kodlarınızı ekleyin
    print("💡 Kendi veri analizi kodlarınızı buraya ekleyebilirsiniz", flush=True)
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
