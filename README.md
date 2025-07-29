# Satış Tahmin Sistemi

Bu proje, kullanıcıların CSV/Excel dosyalarını yükleyerek makine öğrenmesi modelleri ile satış tahminleri yapabilecekleri web tabanlı bir uygulamadır. Flask framework'ü kullanılarak geliştirilmiş, Blueprint mimarisi ile modüler yapıda tasarlanmıştır.

## ✨ Özellikler

- **Dosya Yükleme**: CSV, XLS, XLSX formatlarını destekler
- **Kolon Seçimi**: Kullanıcı hedef ve özellik kolonlarını seçebilir
- **Model Yapılandırması**: Farklı ML algoritmaları arasından seçim
- **Model Eğitimi**: Otomatik model eğitimi ve performans değerlendirmesi
- **Tahmin Yapma**: Eğitilen model ile yeni veriler için tahmin
- **Responsive UI**: Modern ve kullanıcı dostu arayüz
- **Session Yönetimi**: Kullanıcı işlemlerini takip eden workflow

## 🏗️ Teknik Mimari

```
sales-prediction/
│
├── app.py                 # Ana Flask uygulaması
├── config.py             # Uygulama konfigürasyonu
├── requirements.txt      # Python bağımlılıkları
│
├── blueprints/          # Modüler Blueprint yapısı
│   ├── main.py         # Ana sayfa routes
│   ├── upload.py       # Dosya yükleme işlemleri
│   └── results.py      # ML workflow ve sonuçlar
│
├── utils/               # Yardımcı fonksiyonlar
│   ├── file_utils.py   # Dosya işlemleri
│   └── data_utils.py   # Veri analizi fonksiyonları
│
├── static/              # CSS, JavaScript, images
│   ├── css/style.css
│   ├── js/main.js
│   └── images/
│
├── templates/           # HTML şablonları
│   ├── base.html               # Ana layout
│   ├── index.html              # Ana sayfa
│   ├── upload.html             # Dosya yükleme
│   ├── select_columns.html     # Kolon seçimi
│   ├── configure_model.html    # Model konfigürasyonu
│   ├── train_model.html        # Model eğitimi
│   ├── make_prediction.html    # Tahmin yapma
│   └── prediction_result.html  # Sonuçlar
│
└── uploads/             # Yüklenen dosyalar
```

## 🚀 Kurulum ve Çalıştırma

### Gereksinimler
- Python 3.8+
- Flask
- Pandas
- Scikit-learn
- Bootstrap 5

### Kurulum
1. Projeyi klonlayın:
```bash
git clone https://github.com/mirzakinn/sales-prediction.git
cd sales-prediction
```

2. Virtual environment oluşturun:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS
```

3. Bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

4. Uygulamayı çalıştırın:
```bash
python app.py
```

5. Tarayıcıda açın: `http://127.0.0.1:5000`

## � Kullanım Workflow'u

1. **Ana Sayfa**: Proje tanıtımı ve mevcut workflow durumu
2. **Dosya Yükleme**: CSV/Excel dosyasını sisteme yükleyin
3. **Kolon Seçimi**: Hedef kolon ve özellik kolonlarını seçin
4. **Model Konfigürasyonu**: ML algoritmasını ve parametreleri seçin
5. **Model Eğitimi**: Sistem modeli otomatik olarak eğitir
6. **Tahmin Yapma**: Yeni verilerle tahmin yapın
7. **Sonuçlar**: Tahmin sonuçlarını ve model performansını görüntüleyin

## 🛠️ Teknik Detaylar

### Backend (Flask)
- **Blueprint Architecture**: Modüler route yönetimi
- **Session Management**: Kullanıcı workflow'u takibi
- **File Upload**: Çoklu format desteği (CSV, XLS, XLSX)
- **Error Handling**: Kapsamlı hata yönetimi ve kullanıcı bildirimleri

### Frontend (Bootstrap 5)
- **Responsive Design**: Tüm cihazlarda uyumlu
- **Interactive Forms**: Dinamik form validasyonu
- **Progress Tracking**: Workflow durumu görselleştirmesi
- **Modern UI**: Soft red color scheme ile modern tasarım

### Data Processing
- **Multi-encoding Support**: UTF-8, Latin-1, CP1252 desteği
- **Automatic Separator Detection**: Farklı CSV formatları
- **Data Validation**: Dosya formatı ve içerik kontrolü
- **Session Persistence**: Kullanıcı seçimlerini saklama

## 📊 Desteklenen Dosya Formatları

- **CSV**: Virgül, noktalı virgül, tab ayırıcılı
- **Excel**: .xlsx, .xls formatları
- **Encoding**: UTF-8, Latin-1, CP1252, ISO-8859-1

## 🔧 Konfigürasyon

`config.py` dosyasında aşağıdaki ayarları değiştirebilirsiniz:
- Upload klasörü yolu
- Maksimum dosya boyutu
- Desteklenen dosya türleri
- Debug modu

## 📱 API Endpoints

| Route | Method | Açıklama |
|-------|--------|----------|
| `/` | GET | Ana sayfa |
| `/upload` | GET/POST | Dosya yükleme |
| `/select-columns/<filename>` | GET | Kolon seçimi |
| `/configure-model` | POST | Model konfigürasyonu |
| `/train-model` | POST | Model eğitimi |
| `/make-prediction` | GET/POST | Tahmin yapma |
| `/results` | GET | Sonuçlar |
| `/clear-session` | GET | Session temizleme |

## 🎨 UI Bileşenleri

- **Navigation**: Dropdown menü ile sayfa geçişleri
- **File Upload**: Drag&drop destekli dosya yükleme
- **Progress Tracker**: Workflow durumu göstergesi
- **Flash Messages**: Kullanıcı geri bildirimleri
- **Responsive Tables**: Veri önizleme tabloları
- **Loading Modals**: İşlem durumu göstergeleri


