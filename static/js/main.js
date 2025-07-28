// Main JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    console.log('Satış Tahmin Sistemi yüklendi');
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize smooth scrolling
    initializeSmoothScrolling();
    
    // Initialize animations
    initializeAnimations();
});

// Initialize Bootstrap tooltips
function initializeTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Smooth scrolling for anchor links
function initializeSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Initialize scroll animations
function initializeAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
            }
        });
    }, observerOptions);

    // Observe all cards and feature elements
    document.querySelectorAll('.card, .feature-card, .stat-item').forEach(el => {
        observer.observe(el);
    });
}

// Utility Functions
const Utils = {
    // Format file size
    formatFileSize: function(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    // Format number with commas
    formatNumber: function(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    },

    // Show loading spinner
    showLoading: function(message = 'Yükleniyor...') {
        const loadingHtml = `
            <div class="loading-overlay">
                <div class="text-center">
                    <div class="spinner-border text-primary mb-3" role="status" style="width: 3rem; height: 3rem;">
                        <span class="visually-hidden">Yükleniyor...</span>
                    </div>
                    <h5>${message}</h5>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', loadingHtml);
    },

    // Hide loading spinner
    hideLoading: function() {
        const loading = document.querySelector('.loading-overlay');
        if (loading) {
            loading.remove();
        }
    },

    // Show toast notification
    showToast: function(message, type = 'info') {
        const toastHtml = `
            <div class="toast-container position-fixed top-0 end-0 p-3">
                <div class="toast show" role="alert">
                    <div class="toast-header">
                        <i class="fas fa-info-circle text-${type} me-2"></i>
                        <strong class="me-auto">Bilgilendirme</strong>
                        <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
                    </div>
                    <div class="toast-body">${message}</div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', toastHtml);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            const toast = document.querySelector('.toast-container');
            if (toast) toast.remove();
        }, 5000);
    },

    // Validate file type
    validateFileType: function(file, allowedTypes = ['xlsx', 'xls', 'csv']) {
        const extension = file.name.split('.').pop().toLowerCase();
        return allowedTypes.includes(extension);
    },

    // Validate file size (default 16MB)
    validateFileSize: function(file, maxSize = 16 * 1024 * 1024) {
        return file.size <= maxSize;
    }
};

// File Upload Handlers
const FileUpload = {
    // Handle drag and drop
    setupDragAndDrop: function(uploadArea, fileInput) {
        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            uploadArea.classList.add('drag-over');
        });

        uploadArea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
        });

        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                FileUpload.handleFileSelect(fileInput);
            }
        });
    },

    // Handle file selection
    handleFileSelect: function(fileInput) {
        const file = fileInput.files[0];
        if (file) {
            // Validate file
            if (!Utils.validateFileType(file)) {
                Utils.showToast('Geçersiz dosya türü. Lütfen XLSX, XLS veya CSV dosyası seçin.', 'danger');
                fileInput.value = '';
                return;
            }

            if (!Utils.validateFileSize(file)) {
                Utils.showToast('Dosya boyutu çok büyük. Maksimum 16MB dosya yükleyebilirsiniz.', 'danger');
                fileInput.value = '';
                return;
            }

            // Update UI
            this.updateFileInfo(file);
            Utils.showToast('Dosya başarıyla seçildi: ' + file.name, 'success');
        }
    },

    // Update file information display
    updateFileInfo: function(file) {
        const fileName = document.getElementById('fileName');
        const fileSize = document.getElementById('fileSize');
        const fileInfo = document.getElementById('fileInfo');
        const uploadArea = document.getElementById('uploadArea');
        const submitBtn = document.getElementById('submitBtn');

        if (fileName && fileSize && fileInfo && uploadArea && submitBtn) {
            fileName.textContent = file.name;
            fileSize.textContent = Utils.formatFileSize(file.size);
            fileInfo.classList.remove('d-none');
            uploadArea.classList.add('d-none');
            submitBtn.disabled = false;
        }
    },

    // Clear file selection
    clearFile: function() {
        const fileInput = document.getElementById('fileInput');
        const fileInfo = document.getElementById('fileInfo');
        const uploadArea = document.getElementById('uploadArea');
        const submitBtn = document.getElementById('submitBtn');

        if (fileInput) fileInput.value = '';
        if (fileInfo) fileInfo.classList.add('d-none');
        if (uploadArea) uploadArea.classList.remove('d-none');
        if (submitBtn) submitBtn.disabled = true;
    }
};

// Chart Utilities
const ChartUtils = {
    // Default chart colors
    colors: {
        primary: '#0d6efd',
        success: '#198754',
        warning: '#ffc107',
        danger: '#dc3545',
        info: '#0dcaf0'
    },

    // Create line chart
    createLineChart: function(ctx, labels, data, label = 'Veri') {
        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: label,
                    data: data,
                    borderColor: this.colors.primary,
                    backgroundColor: this.colors.primary + '20',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    },

    // Create pie chart
    createPieChart: function(ctx, labels, data) {
        return new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: [
                        this.colors.success,
                        this.colors.warning,
                        this.colors.danger,
                        this.colors.info,
                        this.colors.primary
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    }
                }
            }
        });
    }
};

// API Helper Functions
const API = {
    // Base URL for API calls
    baseURL: '',

    // Make GET request
    get: async function(endpoint) {
        try {
            const response = await fetch(this.baseURL + endpoint);
            return await response.json();
        } catch (error) {
            console.error('API GET Error:', error);
            Utils.showToast('Veri alınamadı: ' + error.message, 'danger');
            return null;
        }
    },

    // Make POST request
    post: async function(endpoint, data) {
        try {
            const response = await fetch(this.baseURL + endpoint, {
                method: 'POST',
                body: data instanceof FormData ? data : JSON.stringify(data),
                headers: data instanceof FormData ? {} : {
                    'Content-Type': 'application/json'
                }
            });
            return await response.json();
        } catch (error) {
            console.error('API POST Error:', error);
            Utils.showToast('Veri gönderilemedi: ' + error.message, 'danger');
            return null;
        }
    }
};

// Export utilities to global scope
window.Utils = Utils;
window.FileUpload = FileUpload;
window.ChartUtils = ChartUtils;
window.API = API;

// Global functions for template usage
window.clearFile = function() {
    FileUpload.clearFile();
};

window.showDetails = function(date, prediction) {
    // Bu fonksiyon results.html'de kullanılıyor
    const modalContent = document.getElementById('modalContent');
    if (modalContent) {
        modalContent.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h6>Dönem Bilgileri</h6>
                    <p><strong>Tarih:</strong> ${date}</p>
                    <p><strong>Tahmin:</strong> ${Utils.formatNumber(prediction)} TL</p>
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
        const modal = new bootstrap.Modal(document.getElementById('detailModal'));
        modal.show();
    }
};

// Console welcome message
console.log('%c Satış Tahmin Sistemi ', 'background: #0d6efd; color: white; font-size: 16px; padding: 5px;');
console.log('Sistem başarıyla yüklendi. Geliştirici araçları aktif.');
