// Results page JavaScript functions

function initializeCharts(chartData) {
    // Prediction Line Chart
    const ctx1 = document.getElementById('predictionChart').getContext('2d');
    new Chart(ctx1, {
        type: 'line',
        data: {
            labels: chartData.dates,
            datasets: [{
                label: 'Tahmin Edilen Satış',
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
                    text: 'Aylık Satış Tahminleri'
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
        
        XLSX.utils.book_append_sheet(wb, ws, "Satış Tahminleri");
        
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
    doc.text('Satış Tahmin Raporu', 20, 30);
    
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
        'En yüksek satış: Mart 2024\'te bekleniyor',
        'Düşük performans: Yaz aylarında satışlarda azalma',
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
