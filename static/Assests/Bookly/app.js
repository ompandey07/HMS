// ============================================
// BOOKLY - Hotel Management System
// Main JavaScript File
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Lucide Icons
    lucide.createIcons();

    // ============================================
    // Preloader
    // ============================================
    const preloader = document.getElementById('preloader');
    
    window.addEventListener('load', function() {
        setTimeout(() => {
            preloader.classList.add('fade-out');
            document.body.classList.remove('loading');
        }, 1500);
    });

    // ============================================
    // Scroll Progress Bar
    // ============================================
    const scrollProgress = document.getElementById('scrollProgress');
    
    window.addEventListener('scroll', function() {
        const scrollTop = window.scrollY;
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        const scrollPercent = (scrollTop / docHeight) * 100;
        scrollProgress.style.width = scrollPercent + '%';
    });

    // ============================================
    // Mobile Navigation
    // ============================================
    const mobileToggle = document.getElementById('mobileToggle');
    const navLinks = document.getElementById('navLinks');
    const navCloseBtn = document.getElementById('navCloseBtn');
    const mobileOverlay = document.getElementById('mobileOverlay');
    const navLinksItems = document.querySelectorAll('.nav-link');

    function openMobileNav() {
        navLinks.classList.add('active');
        mobileOverlay.classList.add('active');
        mobileToggle.classList.add('active');
        document.body.classList.add('nav-open');
    }

    function closeMobileNav() {
        navLinks.classList.remove('active');
        mobileOverlay.classList.remove('active');
        mobileToggle.classList.remove('active');
        document.body.classList.remove('nav-open');
    }

    mobileToggle.addEventListener('click', function() {
        if (navLinks.classList.contains('active')) {
            closeMobileNav();
        } else {
            openMobileNav();
        }
    });

    navCloseBtn.addEventListener('click', closeMobileNav);
    mobileOverlay.addEventListener('click', closeMobileNav);

    // Close nav when clicking on a link
    navLinksItems.forEach(link => {
        link.addEventListener('click', closeMobileNav);
    });

    // ============================================
    // Smooth Scroll for Navigation Links
    // ============================================
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // ============================================
    // Fade In Images on Scroll
    // ============================================
    const fadeImages = document.querySelectorAll('.fade-in-image');
    
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-visible');
                imageObserver.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.2,
        rootMargin: '0px 0px -50px 0px'
    });

    fadeImages.forEach(img => {
        imageObserver.observe(img);
    });

    // ============================================
    // Dashboard Widget Hover Effect
    // ============================================
    const dashboardWidget = document.querySelector('.dashboard-widget');
    
    if (dashboardWidget) {
        dashboardWidget.addEventListener('mousemove', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const rotateX = (y - centerY) / 30;
            const rotateY = (centerX - x) / 30;
            
            this.style.transform = `rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(20px)`;
        });
        
        dashboardWidget.addEventListener('mouseleave', function() {
            this.style.transform = 'rotateY(-8deg) rotateX(5deg)';
        });
    }

    // ============================================
    // Animate Progress Bars on Scroll
    // ============================================
    const progressBars = document.querySelectorAll('.progress-fill');
    
    const progressObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const progress = entry.target.style.getPropertyValue('--progress');
                entry.target.style.width = progress;
            }
        });
    }, {
        threshold: 0.5
    });

    progressBars.forEach(bar => {
        progressObserver.observe(bar);
    });

    // ============================================
    // Report Cards Animation
    // ============================================
    const reportCards = document.querySelectorAll('.report-card');
    
    const cardObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, index * 100);
                cardObserver.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1
    });

    reportCards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'all 0.5s ease';
        cardObserver.observe(card);
    });

    // ============================================
    // Step Cards Animation
    // ============================================
    const stepCards = document.querySelectorAll('.step-card');
    
    const stepObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, index * 150);
                stepObserver.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1
    });

    stepCards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(40px)';
        card.style.transition = 'all 0.6s ease';
        stepObserver.observe(card);
    });

    // ============================================
    // Feature Tags Animation
    // ============================================
    const featureTags = document.querySelectorAll('.feature-tag');
    
    const tagObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0) scale(1)';
                }, index * 50);
                tagObserver.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1
    });

    featureTags.forEach(tag => {
        tag.style.opacity = '0';
        tag.style.transform = 'translateY(20px) scale(0.9)';
        tag.style.transition = 'all 0.4s ease';
        tagObserver.observe(tag);
    });

    // ============================================
    // Dynamic Footer Copyright
    // ============================================
    const footerCopyright = document.getElementById('footerCopyright');
    const currentYear = new Date().getFullYear();
    footerCopyright.textContent = `© ${currentYear} Bookly. All rights reserved.`;

    // ============================================
    // Navbar Background on Scroll
    // ============================================
    const nav = document.querySelector('.nav');
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            nav.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.1)';
        } else {
            nav.style.boxShadow = 'none';
        }
    });

    // ============================================
    // Animate Stats on Scroll
    // ============================================
    const statValues = document.querySelectorAll('.stat-value');
    
    const statsObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = entry.target;
                const value = target.textContent;
                
                // Check if it's a number
                if (!isNaN(parseInt(value))) {
                    animateNumber(target, parseInt(value));
                }
                
                statsObserver.unobserve(target);
            }
        });
    }, {
        threshold: 0.5
    });

    function animateNumber(element, target) {
        let current = 0;
        const increment = target / 30;
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                element.textContent = target;
                clearInterval(timer);
            } else {
                element.textContent = Math.floor(current);
            }
        }, 30);
    }

    statValues.forEach(stat => {
        statsObserver.observe(stat);
    });

    // ============================================
    // Parallax Effect for Hero Background
    // ============================================
    window.addEventListener('scroll', function() {
        const scrolled = window.scrollY;
        const heroGrid = document.querySelector('.hero-grid');
        
        if (heroGrid && scrolled < window.innerHeight) {
            heroGrid.style.transform = `translateY(${scrolled * 0.3}px)`;
        }
    });

    // ============================================
    // Typing Effect for Slogan (Optional)
    // ============================================
    const slogan = document.querySelector('.hero-slogan');
    
    if (slogan) {
        const originalText = slogan.textContent;
        slogan.textContent = '';
        slogan.style.visibility = 'visible';
        
        setTimeout(() => {
            let i = 0;
            const typingInterval = setInterval(() => {
                if (i < originalText.length) {
                    slogan.textContent += originalText.charAt(i);
                    i++;
                } else {
                    clearInterval(typingInterval);
                }
            }, 50);
        }, 2000);
    }
});