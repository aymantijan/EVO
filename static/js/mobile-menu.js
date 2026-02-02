/**
 * MOBILE MENU TOGGLE
 * Ajouter ce script à votre base.html pour activer le menu hamburger
 */

document.addEventListener('DOMContentLoaded', function() {
    // Créer le bouton hamburger s'il n'existe pas
    const navbar = document.querySelector('.navbar-container');
    const navbarMenu = document.querySelector('.navbar-menu');
    
    if (navbar && navbarMenu) {
        // Vérifier si le bouton n'existe pas déjà
        if (!document.querySelector('.navbar-toggle')) {
            const toggleButton = document.createElement('button');
            toggleButton.className = 'navbar-toggle';
            toggleButton.innerHTML = '<i class="fas fa-bars"></i>';
            toggleButton.setAttribute('aria-label', 'Toggle navigation menu');
            toggleButton.setAttribute('aria-expanded', 'false');
            
            // Insérer le bouton après le logo
            const navbarBrand = document.querySelector('.navbar-brand');
            if (navbarBrand) {
                navbarBrand.insertAdjacentElement('afterend', toggleButton);
            }
            
            // Toggle menu visibility
            toggleButton.addEventListener('click', function() {
                navbarMenu.classList.toggle('active');
                const isExpanded = navbarMenu.classList.contains('active');
                
                // Changer l'icône
                const icon = toggleButton.querySelector('i');
                if (isExpanded) {
                    icon.classList.remove('fa-bars');
                    icon.classList.add('fa-times');
                    toggleButton.setAttribute('aria-expanded', 'true');
                } else {
                    icon.classList.remove('fa-times');
                    icon.classList.add('fa-bars');
                    toggleButton.setAttribute('aria-expanded', 'false');
                }
            });
            
            // Fermer le menu quand on clique sur un lien
            const menuLinks = navbarMenu.querySelectorAll('a');
            menuLinks.forEach(link => {
                link.addEventListener('click', function() {
                    if (window.innerWidth <= 768) {
                        navbarMenu.classList.remove('active');
                        const icon = toggleButton.querySelector('i');
                        icon.classList.remove('fa-times');
                        icon.classList.add('fa-bars');
                        toggleButton.setAttribute('aria-expanded', 'false');
                    }
                });
            });
            
            // Fermer le menu si on clique en dehors
            document.addEventListener('click', function(event) {
                if (window.innerWidth <= 768) {
                    const isClickInsideNav = navbar.contains(event.target);
                    if (!isClickInsideNav && navbarMenu.classList.contains('active')) {
                        navbarMenu.classList.remove('active');
                        const icon = toggleButton.querySelector('i');
                        icon.classList.remove('fa-times');
                        icon.classList.add('fa-bars');
                        toggleButton.setAttribute('aria-expanded', 'false');
                    }
                }
            });
            
            // Gérer le redimensionnement de la fenêtre
            window.addEventListener('resize', function() {
                if (window.innerWidth > 768) {
                    navbarMenu.classList.remove('active');
                    const icon = toggleButton.querySelector('i');
                    icon.classList.remove('fa-times');
                    icon.classList.add('fa-bars');
                    toggleButton.setAttribute('aria-expanded', 'false');
                }
            });
        }
    }
});

/**
 * PREVENT ZOOM ON INPUT FOCUS (iOS)
 */
document.addEventListener('DOMContentLoaded', function() {
    const inputs = document.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        // S'assurer que la taille de police est au moins 16px sur mobile
        if (window.innerWidth <= 768) {
            const fontSize = window.getComputedStyle(input).fontSize;
            const fontSizeValue = parseInt(fontSize);
            if (fontSizeValue < 16) {
                input.style.fontSize = '16px';
            }
        }
    });
});

/**
 * SMOOTH SCROLL POUR LES ANCRES
 */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
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

/**
 * ORIENTATION CHANGE HANDLER
 */
window.addEventListener('orientationchange', function() {
    // Recharger certains éléments après changement d'orientation
    setTimeout(function() {
        window.scrollTo(0, 0);
    }, 100);
});

/**
 * TOUCH FEEDBACK POUR MEILLEURE UX MOBILE
 */
document.addEventListener('DOMContentLoaded', function() {
    const touchableElements = document.querySelectorAll('button, .btn, a');
    
    touchableElements.forEach(element => {
        element.addEventListener('touchstart', function() {
            this.style.opacity = '0.7';
        });
        
        element.addEventListener('touchend', function() {
            this.style.opacity = '1';
        });
        
        element.addEventListener('touchcancel', function() {
            this.style.opacity = '1';
        });
    });
});

/**
 * FIX VIEWPORT HEIGHT SUR MOBILE (pour 100vh)
 */
function setVH() {
    const vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', `${vh}px`);
}

setVH();
window.addEventListener('resize', setVH);
window.addEventListener('orientationchange', setVH);