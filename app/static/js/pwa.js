/**
 * Campus Compass - PWA Installation & Offline Detection
 * Handles install prompt, offline status, and app updates
 */

class PWAManager {
    constructor() {
        this.deferredPrompt = null;
        this.isInstalled = false;
        this.isOffline = false;
        this.init();
    }
    
    init() {
        // Listen for beforeinstallprompt event
        window.addEventListener('beforeinstallprompt', (e) => {
            console.log('[PWA] beforeinstallprompt event fired');
            // Prevent Chrome 67 and earlier from automatically showing the prompt
            e.preventDefault();
            // Stash the event so it can be triggered later
            this.deferredPrompt = e;
            // Show custom install banner
            this.showInstallBanner();
        });
        
        // Listen for app installed event
        window.addEventListener('appinstalled', () => {
            console.log('[PWA] App was installed');
            this.isInstalled = true;
            this.hideInstallBanner();
            if (typeof notify !== 'undefined') {
                notify.success('Campus Compass installed successfully!');
            }
        });
        
        // Detect if app is running in standalone mode (installed PWA)
        if (window.matchMedia('(display-mode: standalone)').matches) {
            this.isInstalled = true;
            console.log('[PWA] Running as installed PWA');
        }
        
        // Also check for display-mode changes
        window.matchMedia('(display-mode: standalone)').addEventListener('change', (e) => {
            if (e.matches) {
                this.isInstalled = true;
                console.log('[PWA] Switched to standalone mode');
            }
        });
        
        // Listen for online/offline events
        window.addEventListener('online', () => this.handleOnline());
        window.addEventListener('offline', () => this.handleOffline());
        
        // Check initial online status
        if (!navigator.onLine) {
            this.handleOffline();
        }
        
        // Check for service worker updates
        this.checkForUpdates();
        
        // Debug: Check if PWA is installable
        this.checkInstallability();
    }
    
    checkInstallability() {
        // Log if the app is installable
        if ('BeforeInstallPromptEvent' in window) {
            console.log('[PWA] BeforeInstallPromptEvent is supported');
        } else {
            console.log('[PWA] BeforeInstallPromptEvent is NOT supported. Check HTTPS and manifest.json');
        }
        
        // Check if service worker is registered
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.ready.then(() => {
                console.log('[PWA] Service worker is ready');
            });
        }
    }
    
    showInstallBanner() {
        // Check if banner was already dismissed
        if (localStorage.getItem('pwa_banner_dismissed') === 'true') {
            return;
        }
        
        // Don't show if already installed
        if (this.isInstalled) {
            return;
        }
        
        // Remove existing banner if any
        this.hideInstallBanner();
        
        // Create banner element
        const banner = document.createElement('div');
        banner.id = 'pwa-install-banner';
        banner.className = 'pwa-install-banner';
        banner.innerHTML = `
            <div class="pwa-banner-content">
                <div class="pwa-banner-icon">
                    <i class="fas fa-mobile-alt"></i>
                </div>
                <div class="pwa-banner-text">
                    <strong>Install Campus Compass</strong>
                    <span>Add to home screen for easy access</span>
                </div>
                <button id="pwa-install-btn" class="pwa-banner-install">
                    Install
                </button>
                <button id="pwa-dismiss-btn" class="pwa-banner-dismiss">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(banner);
        
        // Add styles
        this.injectBannerStyles();
        
        // Add event listeners
        const installBtn = document.getElementById('pwa-install-btn');
        const dismissBtn = document.getElementById('pwa-dismiss-btn');
        
        if (installBtn) {
            installBtn.addEventListener('click', () => {
                this.promptInstall();
            });
        }
        
        if (dismissBtn) {
            dismissBtn.addEventListener('click', () => {
                this.hideInstallBanner();
                localStorage.setItem('pwa_banner_dismissed', 'true');
            });
        }
    }
    
    injectBannerStyles() {
        if (document.getElementById('pwa-banner-styles')) return;
        
        const styles = document.createElement('style');
        styles.id = 'pwa-banner-styles';
        styles.textContent = `
            .pwa-install-banner {
                position: fixed;
                bottom: 20px;
                left: 20px;
                right: 20px;
                background: var(--campus-gray-800);
                border-radius: 16px;
                border: 1px solid var(--campus-accent);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
                z-index: 10000;
                animation: slideUp 0.3s ease;
            }
            
            .pwa-banner-content {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 12px 16px;
            }
            
            .pwa-banner-icon {
                width: 48px;
                height: 48px;
                background: var(--campus-accent-soft);
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .pwa-banner-icon i {
                font-size: 24px;
                color: var(--campus-accent);
            }
            
            .pwa-banner-text {
                flex: 1;
                display: flex;
                flex-direction: column;
            }
            
            .pwa-banner-text strong {
                font-size: 14px;
                margin-bottom: 2px;
                color: white;
            }
            
            .pwa-banner-text span {
                font-size: 12px;
                color: var(--campus-gray-400);
            }
            
            .pwa-banner-install {
                background: var(--campus-accent);
                color: var(--campus-primary-dark);
                border: none;
                padding: 8px 20px;
                border-radius: 30px;
                font-weight: 600;
                font-size: 14px;
                cursor: pointer;
                transition: all 0.2s;
            }
            
            .pwa-banner-install:hover {
                background: var(--campus-accent-dark);
                transform: scale(1.02);
            }
            
            .pwa-banner-dismiss {
                background: none;
                border: none;
                color: var(--campus-gray-500);
                cursor: pointer;
                padding: 8px;
                font-size: 14px;
            }
            
            .pwa-banner-dismiss:hover {
                color: white;
            }
            
            /* Offline indicator */
            .offline-indicator {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                background: #FF1744;
                color: white;
                text-align: center;
                padding: 8px;
                font-size: 12px;
                z-index: 10001;
                animation: slideDown 0.3s ease;
            }
            
            @keyframes slideUp {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            @keyframes slideDown {
                from {
                    opacity: 0;
                    transform: translateY(-20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            @media (min-width: 768px) {
                .pwa-install-banner {
                    left: auto;
                    right: 20px;
                    max-width: 380px;
                }
            }
        `;
        document.head.appendChild(styles);
    }
    
    promptInstall() {
        if (this.deferredPrompt) {
            // Show the install prompt
            this.deferredPrompt.prompt();
            // Wait for the user to respond to the prompt
            this.deferredPrompt.userChoice.then((choiceResult) => {
                if (choiceResult.outcome === 'accepted') {
                    console.log('[PWA] User accepted the install prompt');
                    if (typeof notify !== 'undefined') {
                        notify.success('Thank you for installing Campus Compass!');
                    }
                } else {
                    console.log('[PWA] User dismissed the install prompt');
                }
                this.deferredPrompt = null;
                this.hideInstallBanner();
            });
        } else {
            // Fallback: show instructions
            if (typeof notify !== 'undefined') {
                notify.info('Tap the Share button and select "Add to Home Screen"');
            }
        }
    }
    
    hideInstallBanner() {
        const banner = document.getElementById('pwa-install-banner');
        if (banner) {
            banner.remove();
        }
    }
    
    handleOffline() {
        if (this.isOffline) return;
        this.isOffline = true;
        
        // Show offline indicator
        const indicator = document.createElement('div');
        indicator.id = 'offline-indicator';
        indicator.className = 'offline-indicator';
        indicator.innerHTML = '<i class="fas fa-wifi"></i> You are offline. Cached map data is available.';
        document.body.insertBefore(indicator, document.body.firstChild);
        
        if (typeof notify !== 'undefined') {
            notify.warning('You are offline. Cached map data is available.', 3000);
        }
    }
    
    handleOnline() {
        if (!this.isOffline) return;
        this.isOffline = false;
        
        // Remove offline indicator
        const indicator = document.getElementById('offline-indicator');
        if (indicator) {
            indicator.remove();
        }
        
        if (typeof notify !== 'undefined') {
            notify.success('Back online! Campus Compass is fully functional.', 3000);
        }
        
        // Trigger background sync for pending favorites
        if ('serviceWorker' in navigator && 'SyncManager' in window) {
            navigator.serviceWorker.ready.then(registration => {
                registration.sync.register('sync-favorites');
            });
        }
    }
    
    checkForUpdates() {
        // Check for service worker updates
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.ready.then(registration => {
                registration.addEventListener('updatefound', () => {
                    const newWorker = registration.installing;
                    newWorker.addEventListener('statechange', () => {
                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                            // New update available
                            this.showUpdateNotification();
                        }
                    });
                });
            });
        }
    }
    
    showUpdateNotification() {
        const banner = document.createElement('div');
        banner.id = 'pwa-update-banner';
        banner.className = 'pwa-install-banner';
        banner.style.bottom = '80px';
        banner.innerHTML = `
            <div class="pwa-banner-content">
                <div class="pwa-banner-icon">
                    <i class="fas fa-download"></i>
                </div>
                <div class="pwa-banner-text">
                    <strong>Update Available</strong>
                    <span>A new version is ready. Refresh to update.</span>
                </div>
                <button id="pwa-update-btn" class="pwa-banner-install">
                    Refresh
                </button>
                <button id="pwa-update-dismiss" class="pwa-banner-dismiss">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(banner);
        
        document.getElementById('pwa-update-btn').addEventListener('click', () => {
            window.location.reload();
        });
        
        document.getElementById('pwa-update-dismiss').addEventListener('click', () => {
            banner.remove();
        });
    }
}

// Initialize PWA Manager when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.pwaManager = new PWAManager();
});