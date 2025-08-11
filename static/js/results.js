// Results page JavaScript functions

// Initialize results page based on page type
document.addEventListener('DOMContentLoaded', function() {
    // Check if this is the new results page (models listing)
    if (document.querySelector('.card-header.bg-primary') || document.querySelector('.card.h-100.border-0.shadow-sm')) {
        initializeModelsPage();
    }
    
    // Check if this is the old results page (predictions chart)
    if (document.getElementById('predictionChart')) {
        // Old chart initialization will be handled by existing code
    }
});

// New function for models page
function initializeModelsPage() {
    // Get all model cards
    const modelCards = document.querySelectorAll('.card.h-100.border-0.shadow-sm');
    
    modelCards.forEach((card, index) => {
        const detailBtn = card.querySelector('.model-detail-btn');
        const predictBtn = card.querySelector('.model-predict-btn'); // Bu selector artık kullanılmıyor
        
        if (detailBtn) {
            detailBtn.setAttribute('data-model-index', index);
            detailBtn.addEventListener('click', function(e) {
                e.preventDefault();
                showModelDetails(this.getAttribute('data-model-index'), card);
            });
        }
        
        // Prediction butonuna müdahale etme - form kendi işini görsün
        // Form submit'i normal şekilde çalışacak
    });
}

// Show detailed model information
function showModelDetails(modelIndex, cardElement) {
    try {
        // Extract model data from button's data attributes (database'den gelen gerçek veriler)
        const button = cardElement.querySelector('.model-detail-btn');
        
        const modelId = button.getAttribute('data-model-id');
        const modelType = button.getAttribute('data-model-type');
        const targetColumn = button.getAttribute('data-target-column');
        const r2Score = parseFloat(button.getAttribute('data-r2-score'));
        const mae = parseFloat(button.getAttribute('data-mae'));
        const mse = parseFloat(button.getAttribute('data-mse'));
        const rmse = parseFloat(button.getAttribute('data-rmse'));
        const createdAt = button.getAttribute('data-created-at');
        const featuresJson = button.getAttribute('data-features');
        
        // JSON string'i parse et
        let features = [];
        try {
            features = JSON.parse(featuresJson.replace(/'/g, '"'));
        } catch {
            features = featuresJson ? featuresJson.split(',') : [];
        }

        // Calculate additional display values
        const r2Percentage = (r2Score * 100).toFixed(1);
        const modelTypeDisplay = modelType.replace('_', ' ').split(' ').map(word => 
            word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ');

        // Create modal content
        const modalHTML = `
            <div class="modal fade" id="modelDetailsModal" tabindex="-1" aria-hidden="true">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header" style="background-color: #ff0000; color: white;">
                            <h5 class="modal-title">
                                <i class="fas fa-robot me-2"></i>Model Detayları: ${modelTypeDisplay}
                            </h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <!-- Sol Kolon: Temel Bilgiler -->
                                <div class="col-md-6">
                                    <h6 style="color: #ff0000;"><i class="fas fa-database me-2"></i>Temel Model Bilgileri</h6>
                                    <table class="table table-sm">
                                        <tr><td><strong>Model ID:</strong></td><td><span class="badge" style="background-color: #ff0000;">#${modelId}</span></td></tr>
                                        <tr><td><strong>Model Türü:</strong></td><td><span class="badge" style="background-color: #ff0000;">${modelTypeDisplay}</span></td></tr>
                                        <tr><td><strong>Veri Dosyası:</strong></td><td>data.csv</td></tr>
                                        <tr><td><strong>Hedef Değişken:</strong></td><td><span class="badge" style="background-color: #ff0000;">${targetColumn}</span></td></tr>
                                        <tr><td><strong>Özellik Değişkenleri:</strong></td><td>
                                            ${features.map(feature => `<span class="badge" style="background-color: #ff0000; margin-right: 5px;">${feature}</span>`).join('')}
                                        </td></tr>
                                        <tr><td><strong>Eğitim Tarihi:</strong></td><td>${createdAt}</td></tr>
                                        <tr><td><strong>Model Durumu:</strong></td><td><span class="badge bg-success">Aktif</span></td></tr>
                                    </table>
                                </div>
                                
                                <!-- Sağ Kolon: Performans Metrikleri -->
                                <div class="col-md-6">
                                    <h6 class="text-success"><i class="fas fa-chart-line me-2"></i>Performans Metrikleri</h6>
                                    <div class="text-center mb-3">
                                        <div class="h3 text-success mb-0">${r2Percentage}%</div>
                                        <small class="text-muted">R² Score (Açıklama Gücü)</small>
                                    </div>
                                    <div class="row text-center mb-3">
                                        <div class="col-4">
                                            <div class="h5 text-info mb-0">${mae.toFixed(2)}</div>
                                            <small class="text-muted">MAE</small>
                                        </div>
                                        <div class="col-4">
                                            <div class="h5 text-warning mb-0">${mse.toFixed(2)}</div>
                                            <small class="text-muted">MSE</small>
                                        </div>
                                        <div class="col-4">
                                            <div class="h5" style="color: #ff0000;">${rmse.toFixed(2)}</div>
                                            <small class="text-muted">RMSE</small>
                                        </div>
                                    </div>
                                    <div class="alert alert-light">
                                        <small>
                                            <strong>MAE:</strong> Ortalama Mutlak Hata - Gerçek ve tahmin değerleri arasındaki mutlak farkların ortalaması<br>
                                            <strong>MSE:</strong> Ortalama Kare Hata - Hataların karelerinin ortalaması<br>
                                            <strong>RMSE:</strong> Kök Ortalama Kare Hata - MSE'nin karekökü, orijinal birimde hata
                                        </small>
                                    </div>
                                </div>
                            </div>
                            
                            <hr>
                            
                            <!-- Performans Analizi -->
                            <div class="row">
                                <div class="col-12">
                                    <h6 style="color: #ff0000;"><i class="fas fa-analytics me-2"></i>Performans Analizi</h6>
                                    <div class="alert" style="background-color: #ffe6e6; border-color: #ff9999;">
                                        <div class="row">
                                            <div class="col-md-3 text-center">
                                                <div class="h5 text-success">${r2Percentage}%</div>
                                                <small class="text-muted">Açıklama Gücü</small>
                                            </div>
                                            <div class="col-md-3 text-center">
                                                <div class="h5 ${mae < 100 ? 'text-success' : mae < 500 ? 'text-warning' : 'text-danger'}">${mae < 100 ? 'İyi' : mae < 500 ? 'Orta' : 'Zayıf'}</div>
                                                <small class="text-muted">Hata Seviyesi</small>
                                            </div>
                                            <div class="col-md-3 text-center">
                                                <div class="h5 ${features.length >= 5 ? 'text-success' : features.length >= 3 ? 'text-warning' : 'text-danger'}">${features.length >= 5 ? 'Zengin' : features.length >= 3 ? 'Yeterli' : 'Az'}</div>
                                                <small class="text-muted">Özellik Zenginliği</small>
                                            </div>
                                            <div class="col-md-3 text-center">
                                                <div class="h5 text-primary">${r2Score > 0.8 ? 'A' : r2Score > 0.6 ? 'B' : 'C'}</div>
                                                <small class="text-muted">Genel Not</small>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                <i class="fas fa-times me-2"></i>Kapat
                            </button>
                            <button type="button" class="btn btn-danger me-2" onclick="deleteModel('${modelId}')">
                                <i class="fas fa-trash me-2"></i>Modeli Sil
                            </button>
                            <form method="POST" action="/make-prediction-new" style="display: inline;">
                                <input type="hidden" name="model_id" value="${modelId}">
                                <button type="submit" class="btn btn-success">
                                    <i class="fas fa-magic me-2"></i>Bu Modelle Tahmin Yap
                                </button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Remove existing modal if any
        const existingModal = document.getElementById('modelDetailsModal');
        if (existingModal) {
            existingModal.remove();
        }

        // Add modal to page
        document.body.insertAdjacentHTML('beforeend', modalHTML);

        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('modelDetailsModal'));
        modal.show();

    } catch (error) {
        console.error('Model details error:', error);
        alert('Model detayları gösterilirken hata oluştu: ' + error.message);
    }
}

// Initialize accordion functionality for expandable model details
function initializeAccordion() {
    const accordionButtons = document.querySelectorAll('[data-bs-toggle="collapse"]');
    
    accordionButtons.forEach(button => {
        button.addEventListener('click', function() {
            const target = document.querySelector(this.getAttribute('data-bs-target'));
            if (target) {
                target.addEventListener('shown.bs.collapse', function() {
                    this.querySelector('.card-body').style.maxHeight = 'none';
                });
            }
        });
    });
}

function initializeCharts(chartData) {
    // Prediction Line Chart
    const ctx1 = document.getElementById('predictionChart').getContext('2d');
    new Chart(ctx1, {
        type: 'line',
        data: {
            labels: chartData.dates,
            datasets: [{
                label: 'Tahmin Edilen Değer',
                data: chartData.predictions,
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                tension: 0.1,
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Aylık Tahminler'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString() + ' TL';
                        }
                    }
                }
            }
        }
    });

    // Trend Pie Chart
    const ctx2 = document.getElementById('trendChart').getContext('2d');
    new Chart(ctx2, {
        type: 'doughnut',
        data: {
            labels: ['Artış', 'Azalış', 'Stabil'],
            datasets: [{
                data: [60, 25, 15],
                backgroundColor: [
                    'rgb(40, 167, 69)',
                    'rgb(220, 53, 69)',
                    'rgb(255, 193, 7)'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Trend Dağılımı'
                }
            }
        }
    });
    
    // Initialize all event listeners after charts are created
    initializeEventListeners();
}

function initializeEventListeners() {
    // CSV Export Button
    const csvBtn = document.getElementById('csvExportBtn');
    if (csvBtn) {
        csvBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            exportToCSV();
        });
    }

    // Excel Export Button
    const excelBtn = document.getElementById('excelExportBtn');
    if (excelBtn) {
        excelBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            exportToExcel();
        });
    }

    // Generate Report Button
    const reportBtn = document.getElementById('generateReportBtn');
    if (reportBtn) {
        reportBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            generateReport();
        });
    }

    // Refresh Predictions Button
    const refreshBtn = document.getElementById('refreshPredictionsBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            refreshPredictions();
        });
    }

    // Detail buttons
    document.querySelectorAll('.detail-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const date = this.getAttribute('data-date');
            const prediction = parseFloat(this.getAttribute('data-prediction'));
            showDetails(date, prediction);
        });
    });
}

function showDetails(date, prediction) {
    const modalContent = document.getElementById('modalContent');
    modalContent.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <h6>Dönem Bilgileri</h6>
                <p><strong>Tarih:</strong> ${date}</p>
                <p><strong>Tahmin:</strong> ${prediction.toLocaleString()} TL</p>
                <p><strong>Güven Aralığı:</strong> %85</p>
            </div>
            <div class="col-md-6">
                <h6>Algoritma Detayları</h6>
                <p><strong>Model:</strong> Random Forest</p>
                <p><strong>R² Score:</strong> 0.92</p>
                <p><strong>RMSE:</strong> 15.3</p>
            </div>
        </div>
    `;
    new bootstrap.Modal(document.getElementById('detailModal')).show();
}

function exportToCSV() {
    try {
        const table = document.getElementById('predictionsTable');
        if (!table) {
            console.error('Tablo bulunamadı');
            return;
        }
        
        let csv = [];
        
        // Header
        const headers = [];
        table.querySelectorAll('thead th').forEach((th, index) => {
            if (index < 4) { // Skip last action column
                headers.push(th.textContent.trim().replace(/\s+/g, ' '));
            }
        });
        csv.push(headers.join(','));
        
        // Data rows
        table.querySelectorAll('tbody tr').forEach(tr => {
            const row = [];
            tr.querySelectorAll('td').forEach((td, index) => {
                if (index < 4) { // Skip last action column
                    let text = td.textContent.trim().replace(/\s+/g, ' ');
                    if (index === 1) text = text.replace(' TL', ''); // Remove TL from amount
                    if (index === 2) text = text.replace('%', ''); // Remove % from confidence
                    row.push('"' + text + '"');
                }
            });
            if (row.length > 0) {
                csv.push(row.join(','));
            }
        });
        
        // Download
        const csvContent = csv.join('\n');
        const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = `satis_tahminleri_${new Date().toISOString().slice(0,10)}.csv`;
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        if (typeof Utils !== 'undefined') {
            Utils.showToast('CSV dosyası başarıyla indirildi!', 'success');
        } else {
            alert('CSV dosyası başarıyla indirildi!');
        }
    } catch (error) {
        console.error('CSV export error:', error);
        if (typeof Utils !== 'undefined') {
            Utils.showToast('CSV export hatası: ' + error.message, 'danger');
        } else {
            alert('CSV export hatası: ' + error.message);
        }
    }
}

function exportToExcel() {
    try {
        if (typeof XLSX === 'undefined') {
            alert('Excel export kütüphanesi yüklenmedi!');
            return;
        }
        
        // Create workbook and worksheet
        const wb = XLSX.utils.book_new();
        
        // Get table data
        const table = document.getElementById('predictionsTable');
        if (!table) {
            console.error('Tablo bulunamadı');
            return;
        }
        
        const ws_data = [];
        
        // Add headers
        const headers = [];
        table.querySelectorAll('thead th').forEach((th, index) => {
            if (index < 4) { // Skip last action column
                headers.push(th.textContent.trim().replace(/\s+/g, ' '));
            }
        });
        ws_data.push(headers);
        
        // Add data rows
        table.querySelectorAll('tbody tr').forEach(tr => {
            const row = [];
            tr.querySelectorAll('td').forEach((td, index) => {
                if (index < 4) { // Skip last action column
                    let text = td.textContent.trim().replace(/\s+/g, ' ');
                    if (index === 1) {
                        // Convert sales amount to number
                        text = parseFloat(text.replace(/[^\d]/g, ''));
                    } else if (index === 2) {
                        // Convert percentage to number
                        text = parseFloat(text.replace('%', ''));
                    }
                    row.push(text);
                }
            });
            if (row.length > 0) {
                ws_data.push(row);
            }
        });
        
        const ws = XLSX.utils.aoa_to_sheet(ws_data);
        
        // Set column widths
        ws['!cols'] = [
            {wch: 15}, // Date
            {wch: 20}, // Sales
            {wch: 15}, // Confidence
            {wch: 10}  // Trend
        ];
        
        XLSX.utils.book_append_sheet(wb, ws, "Tahminler");
        
        // Save file
        XLSX.writeFile(wb, `satis_tahminleri_${new Date().toISOString().slice(0,10)}.xlsx`);
        
        if (typeof Utils !== 'undefined') {
            Utils.showToast('Excel dosyası başarıyla indirildi!', 'success');
        } else {
            alert('Excel dosyası başarıyla indirildi!');
        }
    } catch (error) {
        console.error('Excel export error:', error);
        if (typeof Utils !== 'undefined') {
            Utils.showToast('Excel export hatası: ' + error.message, 'danger');
        } else {
            alert('Excel export hatası: ' + error.message);
        }
    }
}

function generateReport() {
    if (typeof Utils !== 'undefined') {
        Utils.showLoading('PDF raporu oluşturuluyor...');
    }
    
    // Create PDF using jsPDF
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    
    // Set font to support Turkish characters
    doc.setFont("helvetica");
    
    // Title
    doc.setFontSize(20);
    doc.text('Tahmin Raporu', 20, 30);
    
    // Date
    doc.setFontSize(12);
    doc.text(`Rapor Tarihi: ${new Date().toLocaleDateString('tr-TR')}`, 20, 45);
    
    // Model Performance
    doc.setFontSize(16);
    doc.text('Model Performansı', 20, 65);
    doc.setFontSize(12);
    
    const accuracy = document.querySelector('.text-success h4').textContent;
    const predictionCount = document.querySelector('.text-info h4').textContent;
    
    doc.text(`• Model Doğruluğu: ${accuracy}`, 25, 80);
    doc.text(`• Tahmin Sayısı: ${predictionCount}`, 25, 95);
    doc.text('• Güncelleme: Real-time', 25, 110);
    
    // Insights
    doc.setFontSize(16);
    doc.text('Önemli İçgörüler', 20, 135);
    doc.setFontSize(12);
    
    const insights = [
        'En yüksek değer: Mart 2024\'te bekleniyor',
        'Düşük performans: Yaz aylarında değerlerde azalma',
        'Genel trend: %12 yıllık büyüme beklentisi',
        'Önerilen aksiyon: Q2\'de promosyon kampanyaları'
    ];
    
    insights.forEach((insight, index) => {
        doc.text(`• ${insight}`, 25, 150 + (index * 15));
    });
    
    // Table
    doc.setFontSize(16);
    doc.text('Tahmin Tablosu', 20, 220);
    
    const table = document.getElementById('predictionsTable');
    const tableData = [];
    
    // Get table data for PDF
    table.querySelectorAll('tbody tr').forEach(tr => {
        const row = [];
        tr.querySelectorAll('td').forEach((td, index) => {
            if (index < 4) { // Skip action column
                let text = td.textContent.trim().replace(/\s+/g, ' ');
                row.push(text);
            }
        });
        tableData.push(row);
    });
    
    // Add table to PDF
    doc.autoTable({
        startY: 235,
        head: [['Dönem', 'Tahmin', 'Güven', 'Trend']],
        body: tableData,
        styles: { fontSize: 10 },
        headStyles: { fillColor: [13, 110, 253] }
    });
    
    // Save PDF
    doc.save(`satis_tahmin_raporu_${new Date().toISOString().slice(0,10)}.pdf`);
    
    if (typeof Utils !== 'undefined') {
        Utils.hideLoading();
        Utils.showToast('PDF raporu başarıyla oluşturuldu!', 'success');
    } else {
        alert('PDF raporu başarıyla oluşturuldu!');
    }
}

function refreshPredictions() {
    if (typeof Utils !== 'undefined') {
        Utils.showLoading('Tahminler yenileniyor...');
    }
    
    // AJAX call to refresh predictions
    fetch('/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            action: 'refresh',
            timestamp: new Date().getTime()
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Reload the page to show new predictions
            window.location.reload();
        } else {
            if (typeof Utils !== 'undefined') {
                Utils.showToast('Tahminler yenilenirken hata oluştu', 'danger');
            } else {
                alert('Tahminler yenilenirken hata oluştu');
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        if (typeof Utils !== 'undefined') {
            Utils.showToast('Tahminler yenilenirken hata oluştu: ' + error.message, 'danger');
        } else {
            alert('Tahminler yenilenirken hata oluştu: ' + error.message);
        }
    })
    .finally(() => {
        if (typeof Utils !== 'undefined') {
            Utils.hideLoading();
        }
    });
}

// Model silme fonksiyonu
function deleteModel(modelId) {
    // Onay dialog'u göster
    if (!confirm('Bu modeli silmek istediğinizden emin misiniz?\n\nBu işlem geri alınamaz. Model veritabanından ve dosya sisteminden tamamen kaldırılacaktır.')) {
        return;
    }
    
    try {
        // Loading göster (eğer Utils varsa)
        if (typeof Utils !== 'undefined') {
            Utils.showLoading('Model siliniyor...');
        }
        
        // Form oluştur ve submit et
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/delete-model/${modelId}`;
        form.style.display = 'none';
        
        // CSRF token varsa ekle (Flask-WTF için)
        const csrfToken = document.querySelector('meta[name=csrf-token]');
        if (csrfToken) {
            const tokenInput = document.createElement('input');
            tokenInput.type = 'hidden';
            tokenInput.name = 'csrf_token';
            tokenInput.value = csrfToken.getAttribute('content');
            form.appendChild(tokenInput);
        }
        
        document.body.appendChild(form);
        form.submit();
        
        // Modal'ı kapat
        const modal = document.getElementById('modelDetailsModal');
        if (modal) {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
                bsModal.hide();
            }
        }
        
    } catch (error) {
        console.error('Model silme hatası:', error);
        alert('Model silinirken hata oluştu: ' + error.message);
        
        // Loading'i gizle
        if (typeof Utils !== 'undefined') {
            Utils.hideLoading();
        }
    }
}
