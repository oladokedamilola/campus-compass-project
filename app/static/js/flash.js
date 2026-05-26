// Campus Compass - Flash Message System
// Handles display, auto-dismiss, and manual dismissal of flash messages

class FlashMessage {
    constructor() {
        this.container = document.getElementById('flash-container');
        this.defaultDuration = 7000; // 7 seconds
        this.messageTypes = {
            success: { icon: 'fa-check-circle', color: '#00E676' },
            error: { icon: 'fa-exclamation-circle', color: '#FF1744' },
            warning: { icon: 'fa-exclamation-triangle', color: '#FFD600' },
            info: { icon: 'fa-info-circle', color: '#00F0FF' }
        };
    }
    
    show(message, type = 'info', duration = this.defaultDuration) {
        const typeConfig = this.messageTypes[type] || this.messageTypes.info;
        
        // Create flash element
        const flash = document.createElement('div');
        flash.className = `flash-message flash-${type}`;
        flash.innerHTML = `
            <div class="flash-icon">
                <i class="fas ${typeConfig.icon}"></i>
            </div>
            <div class="flash-content">
                <p>${this.escapeHtml(message)}</p>
            </div>
            <button class="flash-close" onclick="this.closest('.flash-message').remove()">
                <i class="fas fa-times"></i>
            </button>
            <div class="flash-progress-bar"></div>
        `;
        
        // Add styles inline (ensures visibility)
        flash.style.cssText = `
            background: rgba(13, 13, 13, 0.95);
            backdrop-filter: blur(12px);
            border: 1px solid ${typeConfig.color};
            border-radius: 12px;
            padding: 12px 16px;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 12px;
            min-width: 280px;
            max-width: 450px;
            position: relative;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
            animation: slideInDown 0.3s ease;
        `;
        
        // Icon styling
        const iconDiv = flash.querySelector('.flash-icon');
        iconDiv.style.cssText = `
            flex-shrink: 0;
            color: ${typeConfig.color};
            font-size: 20px;
        `;
        
        // Content styling
        const contentDiv = flash.querySelector('.flash-content');
        contentDiv.style.cssText = `
            flex: 1;
            color: white;
            font-family: 'Satoshi', sans-serif;
            font-size: 14px;
            line-height: 1.4;
        `;
        
        const contentP = flash.querySelector('.flash-content p');
        contentP.style.margin = '0';
        
        // Close button styling
        const closeBtn = flash.querySelector('.flash-close');
        closeBtn.style.cssText = `
            background: none;
            border: none;
            color: #9E9E9E;
            cursor: pointer;
            font-size: 14px;
            padding: 4px;
            transition: color 0.2s;
            flex-shrink: 0;
        `;
        closeBtn.onmouseover = () => closeBtn.style.color = 'white';
        closeBtn.onmouseout = () => closeBtn.style.color = '#9E9E9E';
        
        // Progress bar styling
        const progressBar = flash.querySelector('.flash-progress-bar');
        progressBar.style.cssText = `
            position: absolute;
            bottom: 0;
            left: 0;
            height: 3px;
            background: ${typeConfig.color};
            width: 100%;
            animation: shrink ${duration / 1000}s linear forwards;
        `;
        
        // Add to container
        this.container.appendChild(flash);
        
        // Auto-dismiss after duration
        const timeout = setTimeout(() => {
            if (flash && flash.parentNode) {
                this.fadeOut(flash);
            }
        }, duration);
        
        // Store timeout on flash element for potential manual dismissal override
        flash.dataset.timeoutId = timeout;
        
        return flash;
    }
    
    success(message, duration = 7000) {
        return this.show(message, 'success', duration);
    }
    
    error(message, duration = 7000) {
        return this.show(message, 'error', duration);
    }
    
    warning(message, duration = 7000) {
        return this.show(message, 'warning', duration);
    }
    
    info(message, duration = 7000) {
        return this.show(message, 'info', duration);
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    fadeOut(element) {
        element.style.animation = 'slideOutUp 0.3s ease forwards';
        setTimeout(() => {
            if (element && element.parentNode) {
                element.remove();
            }
        }, 300);
    }
    
    // Display flash messages from Flask's flash() function
    displayFromFlashes(messages) {
        if (messages && messages.length) {
            messages.forEach(msg => {
                this.show(msg.message, msg.category);
            });
        }
    }
}

// Initialize flash system
const flash = new FlashMessage();

// Auto-display flashed messages from server (injected via template)
document.addEventListener('DOMContentLoaded', () => {
    if (typeof flashedMessages !== 'undefined' && flashedMessages.length) {
        flash.displayFromFlashes(flashedMessages);
    }
});

// Add CSS animations to document if not present
if (!document.querySelector('#flash-animations')) {
    const style = document.createElement('style');
    style.id = 'flash-animations';
    style.textContent = `
        @keyframes slideInDown {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes slideOutUp {
            from {
                opacity: 1;
                transform: translateY(0);
            }
            to {
                opacity: 0;
                transform: translateY(-20px);
            }
        }
        
        @keyframes shrink {
            from {
                width: 100%;
            }
            to {
                width: 0%;
            }
        }
        
        .flash-container {
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 9999;
            display: flex;
            flex-direction: column;
            align-items: center;
            pointer-events: none;
            width: auto;
            max-width: 90vw;
        }
        
        .flash-message {
            pointer-events: auto;
            position: relative;
        }
        
        @media (max-width: 600px) {
            .flash-container {
                top: 10px;
                width: calc(100% - 20px);
                max-width: none;
            }
            
            .flash-message {
                width: 100%;
                max-width: none;
            }
        }
    `;
    document.head.appendChild(style);
}