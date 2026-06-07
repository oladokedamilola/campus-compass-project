// ============================================
// IMAGE MODAL COMPONENT
// ============================================

class ImageModal {
    constructor() {
        this.modal = null;
        this.closeButton = null;
        this.modalImage = null;
        this.buildingName = null;
        this.autoCloseTimer = null;
        this.currentBuilding = null;
        this.onCloseCallback = null;
        this.triggerSource = null;
        this.createModal();
    }

    createModal() {
        // Check if modal already exists
        if (document.getElementById('imageModal')) {
            this.modal = document.getElementById('imageModal');
            this.closeButton = document.getElementById('closeImageModal');
            this.modalImage = document.getElementById('modalBuildingImage');
            this.buildingName = document.getElementById('modalBuildingName');
            this.autoCloseTimerDiv = document.getElementById('autoCloseTimer');
            this.manualCloseBtn = document.getElementById('manualCloseBtn');
            
            // Re-attach event listeners
            this.attachEventListeners();
            return;
        }
        
        // Modal HTML is in components/image_modal.html
        // Wait for it to be loaded
        const checkModal = setInterval(() => {
            const modal = document.getElementById('imageModal');
            if (modal) {
                this.modal = modal;
                this.closeButton = document.getElementById('closeImageModal');
                this.modalImage = document.getElementById('modalBuildingImage');
                this.buildingName = document.getElementById('modalBuildingName');
                this.autoCloseTimerDiv = document.getElementById('autoCloseTimer');
                this.manualCloseBtn = document.getElementById('manualCloseBtn');
                this.attachEventListeners();
                clearInterval(checkModal);
            }
        }, 100);
    }

    attachEventListeners() {
        if (this.closeButton) {
            this.closeButton.addEventListener('click', () => this.close());
        }
        if (this.manualCloseBtn) {
            this.manualCloseBtn.addEventListener('click', () => this.close());
        }
        if (this.modal) {
            this.modal.addEventListener('click', (e) => {
                if (e.target === this.modal) this.close();
            });
        }
    }

    show(building, triggerSource = 'search', onCloseCallback = null) {
        this.currentBuilding = building;
        this.triggerSource = triggerSource;
        this.onCloseCallback = onCloseCallback;
        
        // Clear any existing timer
        if (this.autoCloseTimer) {
            clearInterval(this.autoCloseTimer);
            this.autoCloseTimer = null;
        }

        // Set building name
        if (this.buildingName) {
            this.buildingName.textContent = building.name;
        }
        
        // Load image
        this.loadImage(building);
        
        // Show modal
        if (this.modal) {
            this.modal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        }
        
        // Set auto-close only for search-triggered modals
        if (triggerSource === 'search') {
            this.startAutoClose(5);
            if (this.autoCloseTimerDiv) {
                this.autoCloseTimerDiv.style.display = 'block';
            }
        } else {
            if (this.autoCloseTimerDiv) {
                this.autoCloseTimerDiv.style.display = 'none';
            }
        }
    }

    loadImage(building) {
        const imagePath = `/static/campus-images/${building.image_filename}`;
        
        // Reset visibility
        if (this.modalImage) this.modalImage.style.display = 'none';
        const fallbackDiv = document.getElementById('imageFallback');
        if (fallbackDiv) fallbackDiv.style.display = 'none';
        
        // Create a new image object to test loading
        const img = new Image();
        
        img.onload = () => {
            if (this.modalImage) {
                this.modalImage.src = imagePath;
                this.modalImage.style.display = 'block';
            }
            if (fallbackDiv) fallbackDiv.style.display = 'none';
        };
        
        img.onerror = () => {
            if (this.modalImage) this.modalImage.style.display = 'none';
            if (fallbackDiv) {
                fallbackDiv.style.display = 'flex';
                fallbackDiv.innerHTML = `
                    <i class="fas fa-building" style="font-size: 48px; color: #00F0FF;"></i>
                    <p style="margin-top: 10px;">No image available for ${building.name}</p>
                    <small style="color: #666;">Image coming soon!</small>
                `;
            }
        };
        
        img.src = imagePath;
    }

    startAutoClose(seconds) {
        let timeLeft = seconds;
        this.updateTimerDisplay(timeLeft);
        
        this.autoCloseTimer = setInterval(() => {
            timeLeft--;
            this.updateTimerDisplay(timeLeft);
            
            if (timeLeft <= 0) {
                this.close();
            }
        }, 1000);
    }

    updateTimerDisplay(seconds) {
        if (this.autoCloseTimerDiv) {
            this.autoCloseTimerDiv.innerHTML = `<i class="fas fa-clock"></i> Closing in ${seconds} second${seconds !== 1 ? 's' : ''}...`;
        }
    }

    close() {
        // Clear timer if exists
        if (this.autoCloseTimer) {
            clearInterval(this.autoCloseTimer);
            this.autoCloseTimer = null;
        }
        
        // Hide modal
        if (this.modal) {
            this.modal.style.display = 'none';
            document.body.style.overflow = '';
        }
        
        // Execute callback if provided
        if (this.onCloseCallback && typeof this.onCloseCallback === 'function') {
            this.onCloseCallback(this.currentBuilding, this.triggerSource);
        }
        
        this.currentBuilding = null;
    }
}

// Initialize global image modal
let imageModal;
document.addEventListener('DOMContentLoaded', () => {
    imageModal = new ImageModal();
});

// Helper function to check if building has image
function buildingHasImage(building) {
    return building.image_filename && building.image_filename.trim() !== '';
}