// Campus Compass - PWA Installation

let deferredPrompt;
const pwaPrompt = document.getElementById('pwaInstallPrompt');
const installBtn = document.getElementById('installPwaBtn');
const closeBtn = document.getElementById('closePwaPrompt');
const laterBtn = document.getElementById('laterPwaBtn');

function isMobileOrTablet() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) || 
           window.innerWidth <= 1024;
}

function isAppInstalled() {
    return window.matchMedia('(display-mode: standalone)').matches || 
           window.navigator.standalone === true;
}

function shouldShowPrompt() {
    if (isAppInstalled()) {
        console.log('[PWA] App already installed');
        return false;
    }
    
    if (!isMobileOrTablet()) {
        console.log('[PWA] Not a mobile or tablet device');
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

// Install button click handler
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
        console.log(`[PWA] User response to install prompt: ${outcome}`);
        
        if (pwaPrompt) pwaPrompt.style.display = 'none';
        deferredPrompt = null;
    });
}

// Close button click handler
if (closeBtn) {
    closeBtn.addEventListener('click', () => {
        if (pwaPrompt) pwaPrompt.style.display = 'none';
        localStorage.setItem('pwaPromptDismissed', Date.now().toString());
        console.log('[PWA] Prompt dismissed');
    });
}

// Later button click handler
if (laterBtn) {
    laterBtn.addEventListener('click', () => {
        if (pwaPrompt) pwaPrompt.style.display = 'none';
        localStorage.setItem('pwaPromptDismissed', Date.now().toString());
        console.log('[PWA] Prompt postponed');
    });
}

// App installed event
window.addEventListener('appinstalled', () => {
    console.log('[PWA] Campus Compass was installed successfully!');
    if (pwaPrompt) pwaPrompt.style.display = 'none';
    localStorage.removeItem('pwaPromptDismissed');
    if (typeof notify !== 'undefined') {
        notify.success('Campus Compass installed! You can now access it from your home screen.');
    }
});

// Check if already installed
if (isAppInstalled()) {
    console.log('[PWA] Running as installed PWA');
}

// Online/Offline detection (optional - keep this for user experience)
window.addEventListener('online', () => {
    console.log('[PWA] Back online');
    if (typeof notify !== 'undefined') {
        notify.success('Back online! Campus Compass is fully functional.');
    }
});

window.addEventListener('offline', () => {
    console.log('[PWA] Offline');
    if (typeof notify !== 'undefined') {
        notify.warning('You are offline. Cached map data is still available.');
    }
});

// Register service worker
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('[PWA] Service Worker registered with scope:', registration.scope);
            })
            .catch(error => {
                console.log('[PWA] Service Worker registration failed:', error);
            });
    });
}