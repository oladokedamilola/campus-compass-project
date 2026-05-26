/**
 * Campus Compass - AJAX Notification System
 * Toast-style notifications with auto-dismiss and progress bar
 */

class NotificationManager {
    constructor() {
        this.container = null;
        this.defaultDuration = 5000; // 5 seconds
        this.notificationTypes = {
            success: {
                icon: 'fa-check-circle',
                color: '#00E676',
                bgGradient: 'linear-gradient(135deg, rgba(0, 230, 118, 0.15), rgba(0, 230, 118, 0.05))'
            },
            error: {
                icon: 'fa-exclamation-circle',
                color: '#FF1744',
                bgGradient: 'linear-gradient(135deg, rgba(255, 23, 68, 0.15), rgba(255, 23, 68, 0.05))'
            },
            warning: {
                icon: 'fa-exclamation-triangle',
                color: '#FFD600',
                bgGradient: 'linear-gradient(135deg, rgba(255, 214, 0, 0.15), rgba(255, 214, 0, 0.05))'
            },
            info: {
                icon: 'fa-info-circle',
                color: '#00F0FF',
                bgGradient: 'linear-gradient(135deg, rgba(0, 240, 255, 0.15), rgba(0, 240, 255, 0.05))'
            }
        };
        
        this.init();
    }
    
    init() {
        this.createContainer();
        this.injectStyles();
    }
    
    createContainer() {
        // Check if container already exists
        if (document.getElementById('notification-container')) {
            this.container = document.getElementById('notification-container');
            return;
        }
        
        // Create notification container
        this.container = document.createElement('div');
        this.container.id = 'notification-container';
        this.container.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            z-index: 10000;
            display: flex;
            flex-direction: column;
            gap: 12px;
            pointer-events: none;
            max-width: 380px;
            width: calc(100% - 40px);
        `;
        
        document.body.appendChild(this.container);
    }
    
    injectStyles() {
        if (document.getElementById('notification-styles')) return;
        
        const styles = document.createElement('style');
        styles.id = 'notification-styles';
        styles.textContent = `
            .toast-notification {
                pointer-events: auto;
                background: var(--campus-gray-800);
                border-radius: 12px;
                padding: 0;
                margin-bottom: 0;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
                animation: slideInRight 0.3s ease forwards;
                overflow: hidden;
                position: relative;
                border: 1px solid transparent;
            }
            
            .toast-notification.hiding {
                animation: slideOutRight 0.3s ease forwards;
            }
            
            .toast-content {
                display: flex;
                align-items: flex-start;
                gap: 12px;
                padding: 14px 16px;
            }
            
            .toast-icon {
                flex-shrink: 0;
                font-size: 20px;
                margin-top: 2px;
            }
            
            .toast-message {
                flex: 1;
                font-family: 'Satoshi', sans-serif;
                font-size: 14px;
                line-height: 1.4;
                color: white;
            }
            
            .toast-message strong {
                display: block;
                margin-bottom: 2px;
                font-size: 14px;
            }
            
            .toast-close {
                background: none;
                border: none;
                color: var(--campus-gray-500);
                cursor: pointer;
                font-size: 14px;
                padding: 4px;
                transition: color 0.2s;
                flex-shrink: 0;
                margin-top: -2px;
            }
            
            .toast-close:hover {
                color: white;
            }
            
            .toast-progress {
                position: absolute;
                bottom: 0;
                left: 0;
                height: 3px;
                width: 100%;
                animation: progressShrink 5s linear forwards;
            }
            
            @keyframes slideInRight {
                from {
                    opacity: 0;
                    transform: translateX(100%);
                }
                to {
                    opacity: 1;
                    transform: translateX(0);
                }
            }
            
            @keyframes slideOutRight {
                from {
                    opacity: 1;
                    transform: translateX(0);
                }
                to {
                    opacity: 0;
                    transform: translateX(100%);
                }
            }
            
            @keyframes progressShrink {
                from {
                    width: 100%;
                }
                to {
                    width: 0%;
                }
            }
            
            @media (max-width: 600px) {
                #notification-container {
                    top: 70px;
                    right: 10px;
                    left: 10px;
                    max-width: none;
                    width: auto;
                }
                
                .toast-notification {
                    width: 100%;
                }
            }
        `;
        
        document.head.appendChild(styles);
    }
    
    /**
     * Show a notification
     * @param {string} message - The notification message
     * @param {string} type - 'success', 'error', 'warning', 'info'
     * @param {number} duration - Duration in milliseconds (default 5000)
     * @param {string} title - Optional title for the notification
     */
    show(message, type = 'info', duration = this.defaultDuration, title = null) {
        const typeConfig = this.notificationTypes[type] || this.notificationTypes.info;
        
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast-notification toast-${type}`;
        toast.style.borderColor = typeConfig.color;
        
        // Set titles based on type if not provided
        const defaultTitles = {
            success: 'Success!',
            error: 'Error!',
            warning: 'Warning!',
            info: 'Notice'
        };
        const finalTitle = title || defaultTitles[type] || 'Notice';
        
        toast.innerHTML = `
            <div class="toast-content" style="background: ${typeConfig.bgGradient}">
                <div class="toast-icon" style="color: ${typeConfig.color}">
                    <i class="fas ${typeConfig.icon}"></i>
                </div>
                <div class="toast-message">
                    <strong>${this.escapeHtml(finalTitle)}</strong>
                    <div>${this.escapeHtml(message)}</div>
                </div>
                <button class="toast-close" onclick="this.closest('.toast-notification').remove()">
                    <i class="fas fa-times"></i>
                </button>
                <div class="toast-progress" style="background: ${typeConfig.color}; animation-duration: ${duration / 1000}s;"></div>
            </div>
        `;
        
        // Add to container
        this.container.appendChild(toast);
        
        // Auto-dismiss after duration
        const timeout = setTimeout(() => {
            this.dismiss(toast);
        }, duration);
        
        // Store timeout on toast for cleanup
        toast._timeout = timeout;
        
        // Add close button handler (already handled inline)
        
        return toast;
    }
    
    /**
     * Dismiss a notification with animation
     * @param {HTMLElement} toast - The toast element to dismiss
     */
    dismiss(toast) {
        if (!toast || !toast.parentNode) return;
        
        // Clear timeout if exists
        if (toast._timeout) {
            clearTimeout(toast._timeout);
        }
        
        toast.classList.add('hiding');
        
        setTimeout(() => {
            if (toast && toast.parentNode) {
                toast.remove();
            }
        }, 300);
    }
    
    /**
     * Dismiss all notifications
     */
    dismissAll() {
        const toasts = this.container.querySelectorAll('.toast-notification');
        toasts.forEach(toast => this.dismiss(toast));
    }
    
    /**
     * Success notification
     * @param {string} message 
     * @param {number} duration 
     */
    success(message, duration = 5000) {
        return this.show(message, 'success', duration);
    }
    
    /**
     * Error notification
     * @param {string} message 
     * @param {number} duration 
     */
    error(message, duration = 6000) {
        return this.show(message, 'error', duration);
    }
    
    /**
     * Warning notification
     * @param {string} message 
     * @param {number} duration 
     */
    warning(message, duration = 5000) {
        return this.show(message, 'warning', duration);
    }
    
    /**
     * Info notification
     * @param {string} message 
     * @param {number} duration 
     */
    info(message, duration = 4000) {
        return this.show(message, 'info', duration);
    }
    
    /**
     * Escape HTML to prevent XSS
     * @param {string} text 
     * @returns {string}
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Create global notification instance
const notify = new NotificationManager();

// Make it available globally
window.notify = notify;

// Intercept fetch errors to show network notifications
const originalFetch = window.fetch;
window.fetch = function(...args) {
    return originalFetch.apply(this, args)
        .catch(error => {
            console.error('Fetch error:', error);
            notify.error('Network error. Please check your connection.');
            throw error;
        });
};

// Auto-handle AJAX response errors (for forms using fetch)
document.addEventListener('DOMContentLoaded', () => {
    // Add global error handler for unhandled rejections
    window.addEventListener('unhandledrejection', (event) => {
        if (event.reason && event.reason.message) {
            notify.error('Something went wrong. Please try again.');
        }
    });
});