# Satış Tahmin Sistemi

Bu proje, Excel dosyalarından satış verilerini okuyarak makine öğrenmesi ile gelecek satış tahminleri yapan bir web uygulamasıdır.

## Kurulum

1. Python virtual environment oluşturun:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

2. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

3. Uygulamayı çalıştırın:
```bash
python app.py
```

## Özellikler

- ✅ **HTML/CSS Hazır** - Responsive web arayüzü
- ✅ **Flask Temel Yapı** - Web framework kurulumu
- ✅ **JavaScript Fonksiyonları** - Tüm UI interaktivitesi hazır
- ✅ **AJAX File Upload** - Asenkron dosya yükleme
- ✅ **Chart.js Entegrasyonu** - Grafik görselleştirme
- ✅ **CSV/Excel Export** - Veri indirme özellikleri
- ✅ **PDF Rapor** - Otomatik rapor oluşturma
- ⏳ **Excel Dosya Okuma** - Sen implement edeceksin
- ⏳ **Veri İşleme** - Sen implement edeceksin  
- ⏳ **Makine Öğrenmesi** - Sen implement edeceksin
- ⏳ **Tahmin Modeli** - Sen implement edeceksin

## Sen Yapacağın Kısımlar

### 1. Excel Dosya Okuma (`app.py` - upload_file route)
```python
# Dosya yükleme ve okuma
file = request.files['file']
if file and allowed_file(file.filename):
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # Excel/CSV okuma
    if filename.endswith('.csv'):
        df = pd.read_csv(filepath)
    else:
        df = pd.read_excel(filepath)
```

### 2. Veri İşleme
```python
# Veri temizleme ve preprocessing
# - Eksik değerleri temizle
# - Tarih sütununu datetime'a çevir
# - Numerik olmayan değerleri temizle
# - Feature engineering
```

### 3. Makine Öğrenmesi Modeli
```python
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

# Model eğitimi
# - Veriyi train/test olarak böl
# - Model seç (Linear Regression, Random Forest, vs.)
# - Modeli eğit
# - Performans değerlendir
```

### 4. Tahmin Endpoint'i (`app.py` - predict route)
```python
# Yeni tahminler yapma
# - Eğitilmiş modeli yükle
# - Yeni veri al
# - Tahmin yap
# - Sonucu JSON olarak döndür
```

## Klasör Yapısı

```
task/
├── app.py                 # Ana Flask uygulaması
├── templates/             # HTML şablonları (HAZIR)
│   ├── base.html
│   ├── index.html
│   ├── upload.html
│   └── results.html
├── static/               # CSS ve JS dosyaları (HAZIR)
│   ├── css/style.css
│   └── js/main.js
├── uploads/              # Yüklenen dosyalar
├── models/               # Eğitilmiş modeller (sen oluşturacaksın)
└── requirements.txt      # Python paketleri
```

## Örnek Veri Formatı

Excel dosyanız şu formatta olmalı:

| Tarih      | Satış  | Ürün     | Kategori |
|-----------|--------|----------|----------|
| 2023-01   | 15000  | Ürün A   | Kategori1|
| 2023-02   | 18000  | Ürün B   | Kategori2|
| 2023-03   | 12000  | Ürün A   | Kategori1|

## Geliştirme Sırası

1. **Excel okuma**: Önce basit Excel dosyası okumayı çalıştır
2. **Veri görselleştirme**: Matplotlib ile grafikler oluştur
3. **Basit model**: Linear Regression ile başla
4. **Model iyileştirme**: Random Forest, XGBoost dene
5. **Web entegrasyonu**: Modeli Flask'e entegre et

## Yardımcı Kaynaklar

- Pandas: https://pandas.pydata.org/docs/
- Scikit-learn: https://scikit-learn.org/stable/
- Flask: https://flask.palletsprojects.com/
- Matplotlib: https://matplotlib.org/

## İletişim

Takıldığın yerler olursa sorabilirsin!
