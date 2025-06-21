// Performance optimizations for INSTALLMOD.COM

// Lazy loading for images
document.addEventListener('DOMContentLoaded', function() {
    // Intersection Observer for lazy loading
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                observer.unobserve(img);
            }
        });
    });

    // Observe all lazy images
    document.querySelectorAll('img[data-src]').forEach(img => {
        imageObserver.observe(img);
    });

    // Preload critical resources
    const preloadCriticalResources = () => {
        // Preload next page resources on hover
        document.querySelectorAll('a[href]').forEach(link => {
            link.addEventListener('mouseenter', () => {
                const linkUrl = link.href;
                if (linkUrl && !link.dataset.preloaded) {
                    const preloadLink = document.createElement('link');
                    preloadLink.rel = 'prefetch';
                    preloadLink.href = linkUrl;
                    document.head.appendChild(preloadLink);
                    link.dataset.preloaded = 'true';
                }
            });
        });
    };

    // Initialize preloading
    preloadCriticalResources();

    // Service Worker registration for caching
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
            navigator.serviceWorker.register('/static/js/sw.js')
                .then(registration => {
                    console.log('SW registered: ', registration);
                })
                .catch(registrationError => {
                    console.log('SW registration failed: ', registrationError);
                });
        });
    }
});

// Resource hints for better performance
function addResourceHints() {
    const hints = [
        { rel: 'dns-prefetch', href: '//fonts.googleapis.com' },
        { rel: 'dns-prefetch', href: '//cdnjs.cloudflare.com' },
        { rel: 'dns-prefetch', href: '//cdn.jsdelivr.net' }
    ];

    hints.forEach(hint => {
        const link = document.createElement('link');
        link.rel = hint.rel;
        link.href = hint.href;
        document.head.appendChild(link);
    });
}

// Initialize performance optimizations
addResourceHints();