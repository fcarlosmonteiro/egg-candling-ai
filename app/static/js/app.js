// Egg Candling AI - Main Application JavaScript

class EggCandlingApp {
    constructor() {
        this.isAnalyzing = false;
        this.showCamera = false;
        this.currentImage = null;
        this.results = null;
        this.stream = null;

        this.init();
    }

    init() {
        // Initialize event listeners
        this.setupEventListeners();
    }

    setupEventListeners() {
        // File input change
        document.addEventListener('change', (e) => {
            if (e.target.id === 'fileInput') {
                this.handleFileUpload(e);
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.showCamera) {
                this.stopCamera();
            }
        });
    }

    enterApp() {
        this.showNotification('Acessando sistema...', 'info');
        setTimeout(() => {
            window.location.href = '/app';
        }, 500);
    }

    goHome() {
        this.results = null;
        this.currentImage = null;
        this.stopCamera();
        this.showNotification('Voltando ao início...', 'info');
        setTimeout(() => {
            window.location.href = '/';
        }, 500);
    }

    handleFileUpload(event) {
        const file = event.target.files[0];
        if (file) {
            // Validate file type
            if (!file.type.startsWith('image/')) {
                this.showNotification('Por favor, selecione apenas arquivos de imagem', 'error');
                return;
            }

            // Validate file size (max 10MB)
            if (file.size > 10 * 1024 * 1024) {
                this.showNotification('Arquivo muito grande. Máximo 10MB', 'error');
                return;
            }

            const reader = new FileReader();
            reader.onload = (e) => {
                this.currentImage = e.target.result;
                this.render();
            };
            reader.readAsDataURL(file);
        }
    }

    async startCamera() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({ 
                video: { 
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                    facingMode: 'environment' // Use back camera if available
                } 
            });
            
            const video = document.getElementById('cameraVideo');
            if (video) {
                video.srcObject = this.stream;
                this.showCamera = true;
                this.render();
            }
        } catch (error) {
            console.error('Camera error:', error);
            this.showNotification('Erro ao acessar a câmera: ' + error.message, 'error');
        }
    }

    capturePhoto() {
        const video = document.getElementById('cameraVideo');
        if (video) {
            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            canvas.getContext('2d').drawImage(video, 0, 0);
            this.currentImage = canvas.toDataURL('image/jpeg', 0.9);
            this.stopCamera();
            this.showNotification('Foto capturada com sucesso!', 'success');
        }
    }

    stopCamera() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
        this.showCamera = false;
        this.render();
    }

    async analyzeImage() {
        if (!this.currentImage) {
            this.showNotification('Nenhuma imagem selecionada', 'error');
            return;
        }
        
        this.isAnalyzing = true;
        this.render();
        
        try {
            // Converter data URL para blob
            const response = await fetch(this.currentImage);
            const blob = await response.blob();
            
            // Criar FormData
            const formData = new FormData();
            formData.append('image', blob, 'image.jpg');
            
            // Enviar para API
            const apiResponse = await fetch('/infer', {
                method: 'POST',
                body: formData
            });
            
            if (apiResponse.ok) {
                this.results = await apiResponse.json();
                this.showNotification('Análise concluída com sucesso!', 'success');
            } else {
                const error = await apiResponse.json();
                this.showNotification('Erro na análise: ' + error.error, 'error');
            }
        } catch (error) {
            console.error('Analysis error:', error);
            this.showNotification('Erro ao analisar imagem: ' + error.message, 'error');
        }
        
        this.isAnalyzing = false;
        this.render();
    }

    getFertileCount() {
        if (!this.results) return 0;
        return this.results.detections.filter(d => d.class === 'fertile').length;
    }

    getInfertileCount() {
        if (!this.results) return 0;
        return this.results.detections.filter(d => d.class === 'infertile').length;
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg transition-all duration-300 transform translate-x-full`;
        
        // Set colors based on type
        const colors = {
            success: 'bg-green-500 text-white',
            error: 'bg-red-500 text-white',
            warning: 'bg-yellow-500 text-black',
            info: 'bg-blue-500 text-white'
        };
        
        notification.className += ` ${colors[type] || colors.info}`;
        notification.innerHTML = `
            <div class="flex items-center">
                <i class="fas fa-${this.getNotificationIcon(type)} mr-2"></i>
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-white hover:text-gray-200">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.classList.remove('translate-x-full');
        }, 100);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            notification.classList.add('translate-x-full');
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, 300);
        }, 5000);
    }

    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-triangle',
            warning: 'exclamation-circle',
            info: 'info-circle'
        };
        return icons[type] || icons.info;
    }

}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.eggApp = new EggCandlingApp();
});

// Export for use in Alpine.js
window.EggCandlingApp = EggCandlingApp;
