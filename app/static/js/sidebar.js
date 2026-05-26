// Campus Compass - Sidebar Navigation System
// Handles sidebar toggle for mobile and desktop

class SidebarManager {
    constructor() {
        this.sidebar = document.getElementById('sidebar');
        this.overlay = document.getElementById('sidebar-overlay');
        this.toggleBtn = document.getElementById('toggle-sidebar-btn');
        this.closeBtn = document.getElementById('close-sidebar-btn');
        
        this.isMobile = window.innerWidth < 768;
        this.isOpen = window.innerWidth >= 1024; // Desktop: open by default
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.handleResize();
        this.applyInitialState();
        
        // Watch for window resize
        window.addEventListener('resize', () => this.handleResize());
    }
    
    setupEventListeners() {
        // Toggle button click
        if (this.toggleBtn) {
            this.toggleBtn.addEventListener('click', () => this.toggle());
        }
        
        // Close button click (mobile only)
        if (this.closeBtn) {
            this.closeBtn.addEventListener('click', () => this.close());
        }
        
        // Overlay click (close on tap outside)
        if (this.overlay) {
            this.overlay.addEventListener('click', () => this.close());
        }
        
        // Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen && this.isMobile) {
                this.close();
            }
        });
    }
    
    handleResize() {
        const wasMobile = this.isMobile;
        this.isMobile = window.innerWidth < 768;
        
        if (this.isMobile) {
            // Mobile mode
            if (wasMobile !== this.isMobile) {
                // Just switched to mobile, close sidebar
                this.close();
                this.applyMobileStyles();
            }
        } else {
            // Tablet or Desktop mode
            const isDesktop = window.innerWidth >= 1024;
            
            if (isDesktop) {
                // Desktop: sidebar open by default
                if (!this.isOpen) {
                    this.open(false); // Open without animation on resize
                }
                this.applyDesktopStyles();
            } else {
                // Tablet: sidebar collapsed by default (can be toggled)
                if (this.isOpen && wasMobile) {
                    this.close(false);
                }
                this.applyTabletStyles();
            }
        }
    }
    
    applyInitialState() {
        if (this.isMobile) {
            this.close(false);
            this.applyMobileStyles();
        } else if (window.innerWidth >= 1024) {
            this.open(false);
            this.applyDesktopStyles();
        } else {
            this.close(false);
            this.applyTabletStyles();
        }
    }
    
    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }
    
    open(animate = true) {
        this.isOpen = true;
        
        if (this.sidebar) {
            if (this.isMobile) {
                this.sidebar.classList.add('open');
                if (this.overlay) this.overlay.classList.add('active');
                document.body.style.overflow = 'hidden';
            } else {
                this.sidebar.classList.add('expanded');
                this.sidebar.classList.remove('collapsed');
                
                // Adjust main content margin
                const main = document.querySelector('.user-main');
                if (main) main.style.marginLeft = '280px';
            }
        }
    }
    
    close(animate = true) {
        this.isOpen = false;
        
        if (this.sidebar) {
            if (this.isMobile) {
                this.sidebar.classList.remove('open');
                if (this.overlay) this.overlay.classList.remove('active');
                document.body.style.overflow = '';
            } else {
                this.sidebar.classList.remove('expanded');
                this.sidebar.classList.add('collapsed');
                
                // Adjust main content margin
                const main = document.querySelector('.user-main');
                if (main) main.style.marginLeft = '80px';
            }
        }
    }
    
    applyMobileStyles() {
        if (this.sidebar) {
            this.sidebar.style.position = 'fixed';
            this.sidebar.style.left = '-280px';
            this.sidebar.style.top = '0';
            this.sidebar.style.bottom = '0';
            this.sidebar.style.width = '280px';
            this.sidebar.style.zIndex = '1001';
            this.sidebar.style.transition = 'left 0.3s ease';
            
            // When open, left: 0
            const style = document.createElement('style');
            style.textContent = `
                .user-sidebar.open {
                    left: 0 !important;
                }
                .sidebar-overlay.active {
                    display: block !important;
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    applyDesktopStyles() {
        if (this.sidebar) {
            this.sidebar.style.position = 'fixed';
            this.sidebar.style.left = '0';
            this.sidebar.style.top = '0';
            this.sidebar.style.bottom = '0';
            this.sidebar.style.width = '280px';
            this.sidebar.style.zIndex = '1000';
            this.sidebar.style.transition = 'width 0.3s ease';
            
            const main = document.querySelector('.user-main');
            if (main) main.style.marginLeft = '280px';
            main.style.transition = 'margin-left 0.3s ease';
        }
    }
    
    applyTabletStyles() {
        if (this.sidebar) {
            this.sidebar.style.position = 'fixed';
            this.sidebar.style.left = '0';
            this.sidebar.style.top = '0';
            this.sidebar.style.bottom = '0';
            this.sidebar.style.width = '80px';
            this.sidebar.style.zIndex = '1000';
            
            // Hide text labels on tablet
            const spans = this.sidebar.querySelectorAll('.sidebar-link span');
            spans.forEach(span => span.style.display = 'none');
            
            const main = document.querySelector('.user-main');
            if (main) main.style.marginLeft = '80px';
            
            // On hover, expand tooltip-like behavior can be added
        }
    }
}

// Initialize sidebar when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.sidebarManager = new SidebarManager();
});