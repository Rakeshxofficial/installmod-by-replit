// installMOD Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href && href !== '#' && href.length > 1) {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });

    // Theme toggle functionality
    const themeToggle = document.querySelector('.theme-toggle');
    const body = document.body;
    
    if (themeToggle) {
        // Check for saved theme preference
        const savedTheme = localStorage.getItem('theme') || 'light';
        body.setAttribute('data-theme', savedTheme);
        updateThemeIcon(savedTheme);
        
        themeToggle.addEventListener('click', function() {
            const currentTheme = body.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            body.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(newTheme);
        });
    }
    
    function updateThemeIcon(theme) {
        const icon = themeToggle.querySelector('i');
        if (theme === 'dark') {
            icon.className = 'fas fa-sun';
        } else {
            icon.className = 'fas fa-moon';
        }
    }

    // Hamburger menu functionality
    const hamburgerBtn = document.getElementById('hamburgerBtn');
    const sidebar = document.getElementById('newSidebar');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    const sidebarClose = document.getElementById('sidebarClose');

    if (hamburgerBtn && sidebar && sidebarOverlay) {
        hamburgerBtn.addEventListener('click', function() {
            sidebar.classList.add('active');
            sidebarOverlay.style.display = 'block';
            document.body.style.overflow = 'hidden';
        });

        function closeSidebar() {
            sidebar.classList.remove('active');
            sidebarOverlay.style.display = 'none';
            document.body.style.overflow = '';
        }

        if (sidebarClose) {
            sidebarClose.addEventListener('click', closeSidebar);
        }

        sidebarOverlay.addEventListener('click', closeSidebar);

        // Close sidebar on escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && sidebar.classList.contains('active')) {
                closeSidebar();
            }
        });
    }
    
    // Search modal functionality
    const searchModal = document.getElementById('searchModal');
    if (searchModal) {
        searchModal.addEventListener('shown.bs.modal', function() {
            const searchInput = searchModal.querySelector('input[name="q"]');
            if (searchInput) {
                searchInput.focus();
            }
        });
    }

    // Lazy loading for images
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });

        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }

    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.app-card, .news-card, .news-item');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });

    // Sidebar functionality
    function initializeSidebar() {
        const hamburgerBtn = document.getElementById('hamburgerBtn');
        const newSidebar = document.getElementById('newSidebar');
        const sidebarClose = document.getElementById('sidebarClose');
        const sidebarOverlay = document.getElementById('sidebarOverlay');
        

        
        function openSidebar() {
            if (newSidebar && sidebarOverlay) {
                newSidebar.classList.add('open');
                sidebarOverlay.style.display = 'block';
                document.body.style.overflow = 'hidden';
            }
        }
        
        function closeSidebar() {
            if (newSidebar && sidebarOverlay) {
                newSidebar.classList.remove('open');
                sidebarOverlay.style.display = 'none';
                document.body.style.overflow = '';
            }
        }
        
        // Hamburger button click
        if (hamburgerBtn) {
            hamburgerBtn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                openSidebar();
            });
        }
        
        // Close button click
        if (sidebarClose) {
            sidebarClose.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                closeSidebar();
            });
        }
        
        // Overlay click
        if (sidebarOverlay) {
            sidebarOverlay.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                closeSidebar();
            });
        }
        
        // Navigation item clicks
        const sidebarItems = document.querySelectorAll('.sidebar-item');
        sidebarItems.forEach(item => {
            item.addEventListener('click', function() {
                closeSidebar();
            });
        });
    }
    
    // Initialize sidebar
    initializeSidebar();

    // Download button functionality - only for buttons without href (actual links should work normally)
    const downloadButtons = document.querySelectorAll('button');
    downloadButtons.forEach(button => {
        // Skip logo/brand container and navigation links
        if (button.closest('.brand-container') || button.closest('.nav-link')) {
            return;
        }
        
        if (button.textContent && button.textContent.toLowerCase().includes('download') && !button.closest('a')) {
            button.addEventListener('click', function(e) {
                // Show download modal or redirect to download page
                const appName = this.textContent.replace('Download ', '').replace(' MOD APK', '').replace('(', '').replace(')', '');
                
                // Create download notification
                showNotification(`Download for ${appName} will start shortly...`, 'success');
                
                // Simulate download process
                setTimeout(() => {
                    showNotification(`${appName} download completed!`, 'info');
                }, 2000);
            });
        }
    });

    // No loading states on buttons - allow immediate form submission

    // Back to top button
    const backToTopBtn = document.createElement('button');
    backToTopBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
    backToTopBtn.className = 'btn btn-success back-to-top';
    backToTopBtn.style.cssText = `
        position: fixed;
        bottom: 90px;
        right: 20px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        display: none;
        z-index: 1001;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
    `;
    document.body.appendChild(backToTopBtn);

    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            backToTopBtn.style.display = 'block';
        } else {
            backToTopBtn.style.display = 'none';
        }
    });

    backToTopBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    // No search form interference - let forms submit naturally

    // Category filter functionality - simplified without loading states
    const categoryButtons = document.querySelectorAll('.category-btn');
    categoryButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Just track the click without loading spinners
            console.log('Category clicked:', this.textContent);
        });
    });

    // Error handling for images
    document.querySelectorAll('img').forEach(img => {
        img.addEventListener('error', function() {
            this.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgdmlld0JveD0iMCAwIDEwMCAxMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiBmaWxsPSIjRjVGNUY1Ii8+CjxwYXRoIGQ9Ik0zNSA2NUw1MCA0NUw2NSA2NUgzNVoiIGZpbGw9IiNDQ0NDQ0MiLz4KPGNpcmNsZSBjeD0iNDAiIGN5PSIzNSIgcj0iNSIgZmlsbD0iI0NDQ0NDQyIvPgo8L3N2Zz4=';
            this.alt = 'Image not available';
        });
    });

    // Performance monitoring
    if ('performance' in window) {
        window.addEventListener('load', function() {
            setTimeout(function() {
                const perfData = performance.getEntriesByType('navigation')[0];
                if (perfData.loadEventEnd - perfData.loadEventStart > 3000) {
                    console.log('Slow page load detected');
                }
            }, 0);
        });
    }
});

// Utility functions
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    `;
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDownloadCount(count) {
    if (count >= 1000000) {
        return (count / 1000000).toFixed(1) + 'M';
    } else if (count >= 1000) {
        return (count / 1000).toFixed(1) + 'K';
    }
    return count.toString();
}

// SEO and Analytics helpers
function trackEvent(eventName, eventData) {
    // Google Analytics tracking
    if (typeof gtag !== 'undefined') {
        gtag('event', eventName, eventData);
    }
    
    // Custom analytics
    console.log('Event tracked:', eventName, eventData);
}

// Track download clicks
document.addEventListener('click', function(e) {
    // Skip tracking for navigation elements
    if (e.target.closest('.brand-container') || e.target.closest('.navbar') || e.target.closest('.nav-link')) {
        return;
    }
    
    if (e.target.textContent && e.target.textContent.toLowerCase().includes('download')) {
        trackEvent('download_click', {
            app_name: e.target.textContent.replace('Download ', '').replace(' MOD APK', ''),
            page_url: window.location.href
        });
    }
});

// Track search queries
document.addEventListener('submit', function(e) {
    if (e.target.action && e.target.action.includes('search')) {
        const query = e.target.querySelector('input[name="q"]').value;
        trackEvent('search', {
            search_term: query,
            page_url: window.location.href
        });
    }
});

// Progressive Web App functionality
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/sw.js')
            .then(function(registration) {
                console.log('ServiceWorker registration successful');
            })
            .catch(function(err) {
                console.log('ServiceWorker registration failed: ', err);
            });
    });
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Alt + S to focus search
    if (e.altKey && e.key === 's') {
        e.preventDefault();
        const searchInput = document.querySelector('input[name="q"]');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // Escape to close modals
    if (e.key === 'Escape') {
        const openModal = document.querySelector('.modal.show');
        if (openModal) {
            bootstrap.Modal.getInstance(openModal).hide();
        }
        
        const openOffcanvas = document.querySelector('.offcanvas.show');
        if (openOffcanvas) {
            bootstrap.Offcanvas.getInstance(openOffcanvas).hide();
        }
    }
});

// Touch gestures for mobile
let touchStartX = 0;
let touchEndX = 0;

document.addEventListener('touchstart', function(e) {
    touchStartX = e.changedTouches[0].screenX;
});

document.addEventListener('touchend', function(e) {
    touchEndX = e.changedTouches[0].screenX;
    handleGesture();
});

function handleGesture() {
    const swipeThreshold = 50;
    const swipeDistance = touchEndX - touchStartX;
    
    if (Math.abs(swipeDistance) > swipeThreshold) {
        if (swipeDistance > 0) {
            // Swipe right - open sidebar
            const sidebar = document.getElementById('sidebarMenu');
            if (sidebar && !sidebar.classList.contains('show')) {
                new bootstrap.Offcanvas(sidebar).show();
            }
        }
    }
}

// Accessibility improvements
document.addEventListener('keydown', function(e) {
    if (e.key === 'Tab') {
        document.body.classList.add('keyboard-navigation');
    }
});

document.addEventListener('mousedown', function() {
    document.body.classList.remove('keyboard-navigation');
});

// Add skip to main content link
const skipLink = document.createElement('a');
skipLink.href = '#main-content';
skipLink.textContent = 'Skip to main content';
skipLink.className = 'sr-only sr-only-focusable';
skipLink.style.cssText = `
    position: absolute;
    top: -40px;
    left: 6px;
    background: #000;
    color: #fff;
    padding: 8px;
    text-decoration: none;
    z-index: 10000;
`;

skipLink.addEventListener('focus', function() {
    this.style.top = '6px';
});

skipLink.addEventListener('blur', function() {
    this.style.top = '-40px';
});

document.body.insertBefore(skipLink, document.body.firstChild);

// Add main content ID
const mainContent = document.querySelector('.main-content');
if (mainContent) {
    mainContent.id = 'main-content';
}

// ===== LAYOUT STABILITY & ADSENSE MANAGEMENT =====

// Simple AdSense stability without complex monitoring
function initAdSenseStability() {
    // Just ensure scrollbar space is reserved
    preventScrollbarShifts();
}

// Prevent scrollbar-induced layout shifts
function preventScrollbarShifts() {
    // Ensure scrollbar space is always reserved
    if (document.documentElement.scrollHeight <= window.innerHeight) {
        document.documentElement.style.overflowY = 'scroll';
    }
}

// Handle header transparency during scroll
function initHeaderScrollEffect() {
    const header = document.querySelector('.header');
    if (!header) return;
    
    let ticking = false;
    
    function updateHeader() {
        const scrolled = window.pageYOffset > 10;
        header.classList.toggle('scrolled', scrolled);
        ticking = false;
    }
    
    function requestTick() {
        if (!ticking) {
            requestAnimationFrame(updateHeader);
            ticking = true;
        }
    }
    
    window.addEventListener('scroll', requestTick, { passive: true });
}

// Basic image loading without layout interference
function stabilizeImageLoading() {
    // Removed problematic image styling that breaks layout
}

// Initialize all stability measures
function initLayoutStability() {
    initAdSenseStability();
    preventScrollbarShifts();
    initHeaderScrollEffect();
    stabilizeImageLoading();
    
    // Re-run stability checks on window resize
    let resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(function() {
            preventScrollbarShifts();
            stabilizeImageLoading();
        }, 250);
    }, { passive: true });
}

// Start layout stability system
initLayoutStability();
