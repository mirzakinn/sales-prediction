# Satış Tahmin Sistemi - Basit Web Uygulaması

Bu proje, Excel dosyalarından satış verilerini okuyarak makine öğrenmesi ile gelecek satış tahminleri yapacak bir web uygulamasının **Flask web framework** kısmıdır. **API kullanılmaz**, sadece geleneksel web sayfaları ve formlar kullanılır. ML kısımları sizin öğrenmeniz ve uygulamanız için boş bırakılmıştır.

## 🎯 Proje Amacı

- **Flask Blueprint mimarisi** öğrenme
- **Basit web uygulaması** geliştirme  
- **Form işlemleri** ve sayfa geçişleri
- **Dosya yükleme** işlemleri
- **HTML template'leri** kullanımı

## 🏗️ Proje Yapısı

```
sales-prediction/
│
├── app.py                 # Ana uygulama dosyası (Factory Pattern)
├── config.py             # Uygulama yapılandırmaları
├── requirements.txt      # Temel Python bağımlılıkları
├── README.md            # Proje dokümantasyonu
│
├── blueprints/          # Flask Blueprint'leri
│   ├── __init__.py
│   ├── main.py         # Ana sayfa rotaları
│   ├── upload.py       # Dosya yükleme rotaları
│   └── results.py      # ML işlemleri (TODO: ML kodları)
│
├── utils/               # Yardımcı fonksiyonlar
│   ├── __init__.py
│   ├── file_utils.py   # Dosya işlemleri
│   └── data_utils.py   # Veri analizi (TODO: ML kodları)
│
├── static/              # Statik dosyalar (CSS, JS)
│   ├── css/
│   └── js/
│
├── templates/           # HTML şablonları
│   ├── base.html               # Ana template
│   ├── index.html              # Ana sayfa
│   ├── upload.html             # Dosya yükleme
│   ├── train_model.html        # Model eğitimi formu
│   ├── make_prediction.html    # Tahmin formu
│   ├── prediction_result.html  # Tahmin sonucu
│   └── results.html            # Genel sonuçlar
│
└── uploads/             # Yüklenen dosyalar
```

## 🚀 Kurulum ve Çalıştırma

1. Python virtual environment oluşturun:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS
```

2. Temel paketleri yükleyin:
```bash
pip install -r requirements.txt
```

3. ML kütüphanelerinizi ekleyin:
```bash
# Örnek: Kendi kullanacağınız kütüphaneleri yükleyin
pip install numpy scikit-learn matplotlib seaborn
```

## 📋 Tamamlanmış Kısımlar (Web Framework)

✅ **Ana Sayfa**: Güzel giriş sayfası  
✅ **Dosya Yükleme**: CSV, XLS, XLSX dosya desteği  
✅ **Model Eğitimi Formu**: Dosya seçimi ve model türü seçimi  
✅ **Tahmin Formu**: Özellik değerleri girme  
✅ **Sonuç Sayfaları**: Tahmin sonuçlarını gösterme  
✅ **Navigation**: Dropdown menü ile sayfa geçişleri  
✅ **Flash Messages**: Kullanıcı geri bildirimi  
✅ **Blueprint Mimarisi**: Modüler yapı  

## 🔨 Sizin Yapacağınız Kısımlar (ML/AI)

### 1. Veri Analizi (`utils/data_utils.py`)
- [ ] `analyze_dataframe()` fonksiyonunu geliştirin
- [ ] Eksik veri analizi ekleyin
- [ ] Veri tipi kontrolü yapın  
- [ ] İstatistiksel özetler çıkarın
- [ ] Korelasyon analizi yapın
- [ ] Outlier tespiti ekleyin

### 2. Model Eğitimi (`blueprints/results.py` - `train_model()` fonksiyonu)
- [ ] Pandas ile veri okumayı implement edin
- [ ] Veri hazırlama kodları yazın
- [ ] Sklearn modellerini entegre edin:
  - [ ] Linear Regression
  - [ ] Decision Tree  
  - [ ] Random Forest
- [ ] Model performans metriklerini hesaplayın
- [ ] Eğitilen modeli kaydedin (pickle/joblib ile)

### 3. Tahmin Yapma (`blueprints/results.py` - `make_prediction()` fonksiyonu)  
- [ ] Kaydedilmiş modeli yükleyin
- [ ] Form verilerini model formatına çevirin
- [ ] Tahmin yapın ve sonucu döndürün
- [ ] Hata durumlarını ele alın

### 4. Form Alanlarını Özelleştirin
- [ ] `templates/make_prediction.html` - gerçek özellik alanları
- [ ] `templates/train_model.html` - model seçenekleri
- [ ] Veri setinize uygun input alanları

### 5. Sonuç Görselleştirme  
- [ ] `templates/results.html` - grafik ve chartlar
- [ ] Model performans göstergeleri
- [ ] Tahmin doğruluğu metrikleri

## 🌐 Sayfa Yapısı (API YOK!)

### Ana Akış
1. **Ana Sayfa** (`/`) → Genel tanıtım
2. **Veri Yükleme** (`/upload`) → CSV/Excel dosyası yükle
3. **Model Eğitimi** (`/train-model`) → Form ile model eğit
4. **Tahmin Yapma** (`/make-prediction`) → Form ile tahmin
5. **Sonuçlar** (`/results`) → Genel sonuçlar

### Form İşlemleri
- **POST** `/train-model` → Model eğitimi başlat
- **POST** `/make-prediction` → Tahmin yap
- **POST** `/upload` → Dosya yükle

**Tüm işlemler normal HTML formları ile yapılır, JSON API yok!**

## 🎓 Öğrenme Adımları

### 1. Temel Seviye (Hafta 1-2)
1. Pandas ile CSV okuma: `pd.read_csv()`
2. Temel veri analizi: `.head()`, `.info()`, `.describe()`  
3. Linear Regression: `from sklearn.linear_model import LinearRegression`

### 2. Orta Seviye (Hafta 3-4)
1. Veri temizleme: eksik değerler, outlier'lar
2. Feature engineering: yeni özellik oluşturma
3. Model comparison: Linear vs Decision Tree vs Random Forest

### 3. İleri Seviye (Hafta 5+)
1. Cross-validation ile model değerlendirme
2. Hyperparameter tuning
3. Model persistence: pickle/joblib ile kaydetme

## 💡 İpuçları

1. **Küçük adımlarla başlayın**: Önce sadece CSV okumayı çalıştırın
2. **Print ile debug edin**: `print(df.head())` ile veriyi kontrol edin  
3. **Form verilerini kontrol edin**: `print(request.form)` ile ne geldiğini görün
4. **Hata mesajlarını okuyun**: Flask debug modu size yardımcı olur
5. **Dokümante edin**: Kodlarınıza yorum ekleyin

## 📚 Faydalı Kaynaklar

- **Pandas**: https://pandas.pydata.org/docs/
- **Scikit-learn**: https://scikit-learn.org/stable/
- **Flask Forms**: https://flask.palletsprojects.com/en/2.3.x/patterns/wtforms/
- **Bootstrap**: https://getbootstrap.com/docs/

**İyi öğrenmeler! 🚀📊**


