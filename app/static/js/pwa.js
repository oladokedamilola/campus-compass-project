// Campus Compass - PWA Installation
// Version: v2.0.0 - Authentication-aware

let deferredPrompt;
const pwaPrompt = document.getElementById('pwaInstallPrompt');
const installBtn = document.getElementById('installPwaBtn');
const closeBtn = document.getElementById('closePwaPrompt');
const laterBtn = document.getElementById('laterPwaBtn');

// Check if running as installed PWA
function isAppInstalled() {
    return window.matchMedia('(display-mode: standalone)').matches || 
           window.navigator.standalone === true;
}

// Check if should show install prompt
function shouldShowPrompt() {
    if (isAppInstalled()) {
        console.log('[PWA] App already installed');
        return false;
    }
    
    const dismissed = localStorage.getItem('pwaPromptDismissed');
    if (dismissed) {
        const dismissedTime = parseInt(dismissed);
        const now = Date.now();
        const sevenDays = 7 * 24 * 60 * 60 * 1000;
        
        if (now - dismissedTime < sevenDays) {
            console.log('[PWA] Prompt dismissed recently');
            return false;
        }
    }
    
    return true;
}

// Listen for beforeinstallprompt event
window.addEventListener('beforeinstallprompt', (e) => {
    console.log('[PWA] beforeinstallprompt event fired');
    e.preventDefault();
    deferredPrompt = e;
    
    if (shouldShowPrompt()) {
        setTimeout(() => {
            if (pwaPrompt) {
                pwaPrompt.style.display = 'block';
                console.log('[PWA] Showing install prompt');
            }
        }, 3000);
    }
});

// Install button handler
if (installBtn) {
    installBtn.addEventListener('click', async () => {
        if (!deferredPrompt) {
            console.log('[PWA] No installation prompt available');
            if (typeof notify !== 'undefined') {
                notify.info('Tap the share button and select "Add to Home Screen"');
            }
            return;
        }
        
        deferredPrompt.prompt();
        const { outcome } = await deferredPrompt.userChoice;
        console.log(`[PWA] User response: ${outcome}`);
        
        if (pwaPrompt) pwaPrompt.style.display = 'none';
        deferredPrompt = null;
        
        if (outcome === 'accepted') {
            localStorage.removeItem('pwaPromptDismissed');
        }
    });
}

// Close button handler
if (closeBtn) {
    closeBtn.addEventListener('click', () => {
        if (pwaPrompt) pwaPrompt.style.display = 'none';
        localStorage.setItem('pwaPromptDismissed', Date.now().toString());
        console.log('[PWA] Prompt dismissed');
    });
}

// Later button handler
if (laterBtn) {
    laterBtn.addEventListener('click', () => {
        if (pwaPrompt) pwaPrompt.style.display = 'none';
        localStorage.setItem('pwaPromptDismissed', Date.now().toString());
        console.log('[PWA] Prompt postponed');
    });
}

// App installed event
window.addEventListener('appinstalled', () => {
    console.log('[PWA] Campus Compass installed!');
    if (pwaPrompt) pwaPrompt.style.display = 'none';
    localStorage.removeItem('pwaPromptDismissed');
    if (typeof notify !== 'undefined') {
        notify.success('Campus Compass installed! Access from home screen.');
    }
});

// Online/Offline detection
window.addEventListener('online', () => {
    console.log('[PWA] Back online');
    if (typeof notify !== 'undefined') {
        notify.success('Back online!');
    }
    // Reload to get fresh auth state
    window.location.reload();
});

window.addEventListener('offline', () => {
    console.log('[PWA] Offline mode');
    if (typeof notify !== 'undefined') {
        notify.warning('You are offline. Some features may be limited.');
    }
});

// Register service worker with force update
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js', { updateViaCache: 'none' })
            .then(registration => {
                console.log('[PWA] Service Worker registered with scope:', registration.scope);
                
                // Check for updates
                registration.addEventListener('updatefound', () => {
                    const newWorker = registration.installing;
                    console.log('[PWA] New service worker installing');
                    
                    newWorker.addEventListener('statechange', () => {
                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                            console.log('[PWA] Update available - reload to activate');
                            if (typeof notify !== 'undefined') {
                                notify.info('New version available. Reload to update.');
                            }
                        }
                    });
                });
            })
            .catch(error => {
                console.log('[PWA] Service Worker registration failed:', error);
            });
        
        // Handle controller changes
        let refreshing = false;
        navigator.serviceWorker.addEventListener('controllerchange', () => {
            if (refreshing) return;
            refreshing = true;
            console.log('[PWA] Service worker changed, reloading');
            window.location.reload();
        });
    });
}

// Log current mode
if (isAppInstalled()) {
    console.log('[PWA] Running as installed PWA');
}