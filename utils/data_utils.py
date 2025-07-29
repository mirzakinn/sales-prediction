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
    """Dosya uzantısına göre dosyayı okur"""
    if filename.endswith('.csv'):
        return pd.read_csv(filepath)
    else:
        return pd.read_excel(filepath)

# TODO: Buraya kendi veri işleme fonksiyonlarınızı ekleyebilirsiniz
# Örnek fonksiyonlar:
# def clean_data(df): ...
# def handle_missing_values(df): ...
# def feature_engineering(df): ...
# def normalize_data(df): ...
