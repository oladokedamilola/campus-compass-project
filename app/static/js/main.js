// Campus Compass - Main JavaScript
// PWA registration and common utilities

// ============================================
// PRELOADER MANAGER - Minimum display time: 4 seconds
// ============================================
(function() {
    let startTime = Date.now();
    let isHidden = false;
    const MIN_DISPLAY_TIME = 4000; // 4 seconds minimum display
    let hideTimeout = null;
    
    // Function to hide preloader
    function hidePreloader() {
        const preloader = document.getElementById('general-preloader');
        if (preloader && !preloader.classList.contains('hide') && !isHidden) {
            isHidden = true;
            preloader.classList.add('hide');
            setTimeout(() => {
                if (preloader.parentNode) {
                    preloader.remove();
                }
            }, 500);
        }
    }
    
    // Function to check if minimum time has passed
    function tryHidePreloader() {
        const elapsed = Date.now() - startTime;
        
        if (elapsed >= MIN_DISPLAY_TIME) {
            // Minimum time passed, can hide
            if (document.readyState !== 'loading') {
                hidePreloader();
            } else {
                // Wait for DOM to be ready
                document.addEventListener('DOMContentLoaded', function() {
                    hidePreloader();
                });
            }
        } else {
            // Wait remaining time
            const remaining = MIN_DISPLAY_TIME - elapsed;
            if (hideTimeout) clearTimeout(hideTimeout);
            hideTimeout = setTimeout(() => {
                if (document.readyState !== 'loading') {
                    hidePreloader();
                } else {
                    document.addEventListener('DOMContentLoaded', function() {
                        hidePreloader();
                    });
                }
            }, remaining);
        }
    }
    
    // Start the preloader timer
    function startPreloaderTimer() {
        // Check if preloader exists
        const preloader = document.getElementById('general-preloader');
        if (!preloader) return;
        
        // Reset start time
        startTime = Date.now();
        isHidden = false;
        
        // Ensure preloader is visible
        preloader.classList.remove('hide');
        preloader.style.display = 'flex';
        preloader.style.opacity = '1';
        preloader.style.visibility = 'visible';
        
        // Wait for page to load
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function() {
                tryHidePreloader();
            });
        } else {
            tryHidePreloader();
        }
        
        // Ensure it hides even if something goes wrong (max 6 seconds)
        setTimeout(() => {
            if (!isHidden) {
                hidePreloader();
            }
        }, MIN_DISPLAY_TIME + 2000);
    }
    
    // Initialize preloader on page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', startPreloaderTimer);
    } else {
        startPreloaderTimer();
    }
    
    // Show preloader before page unload (for navigation)
    window.addEventListener('beforeunload', function() {
        const preloader = document.getElementById('general-preloader');
        if (preloader) {
            // Reset preloader for next page
            preloader.classList.remove('hide');
            preloader.style.display = 'flex';
            preloader.style.opacity = '1';
            preloader.style.visibility = 'visible';
            isHidden = false;
            startTime = Date.now();
        }
    });
})();

// ============================================
// SERVICE WORKER REGISTRATION
// ============================================
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('Service Worker registered with scope:', registration.scope);
            })
            .catch(error => {
                console.log('Service Worker registration failed:', error);
            });
    });
}

// ============================================
// PWA INSTALLATION DETECTION
// ============================================
if (window.matchMedia('(display-mode: standalone)').matches) {
    console.log('App is running as installed PWA');
}

// Listen for app installed event
window.addEventListener('appinstalled', () => {
    console.log('PWA was installed');
});

// ============================================
// PAGE TRANSITION HANDLER (for better UX)
// ============================================
// Add loading class to body when navigating
document.addEventListener('click', function(e) {
    // Check if clicked element is a link
    let target = e.target;
    while (target && target.tagName !== 'A') {
        target = target.parentElement;
    }
    
    if (target && target.href && target.href.indexOf(window.location.origin) === 0) {
        // Internal link - show preloader
        const preloader = document.getElementById('general-preloader');
        if (preloader) {
            preloader.classList.remove('hide');
            preloader.style.display = 'flex';
            preloader.style.opacity = '1';
            preloader.style.visibility = 'visible';
        }
    }
});