/*
 * TANGER ALLIANCE MODERN NAVIGATION SYSTEM - JAVASCRIPT
 * Phase 3: Interactive Navigation Controller
 * Features: Smooth animations, responsive behavior, accessibility support
 */

class TangerAllianceNavigation {
    constructor() {
        this.init();
        this.bindEvents();
        this.handleResponsive();
    }

    init() {
        this.elements = {
            sidebar: document.querySelector('.tanger-nav-sidebar'),
            menuToggle: document.querySelector('.tanger-nav-menu-toggle'),
            overlay: document.querySelector('.tanger-nav-overlay'),
            mainContent: document.querySelector('.tanger-nav-main-content'),
            expandableItems: document.querySelectorAll('.tanger-nav-menu-expandable'),
            menuLinks: document.querySelectorAll('.tanger-nav-menu-link'),
            submenuLinks: document.querySelectorAll('.tanger-nav-submenu-link')
        };

        this.state = {
            sidebarCollapsed: localStorage.getItem('tanger-nav-collapsed') === 'true',
            mobileMenuOpen: false,
            expandedMenus: JSON.parse(localStorage.getItem('tanger-nav-expanded') || '[]')
        };

        this.applyInitialState();
    }

    applyInitialState() {
        // Apply sidebar collapse state
        if (this.state.sidebarCollapsed && window.innerWidth > 768) {
            this.elements.sidebar?.classList.add('collapsed');
        }

        // Restore expanded menus
        this.state.expandedMenus.forEach(menuId => {
            const menuItem = document.querySelector(`[data-menu-id="${menuId}"]`);
            if (menuItem) {
                menuItem.classList.add('expanded');
            }
        });

        // Set active menu items
        this.setActiveMenuItem();
    }

    bindEvents() {
        // Mobile menu toggle
        this.elements.menuToggle?.addEventListener('click', (e) => {
            e.preventDefault();
            this.toggleMobileMenu();
        });

        // Overlay click to close mobile menu
        this.elements.overlay?.addEventListener('click', () => {
            this.closeMobileMenu();
        });

        // Expandable menu items
        this.elements.expandableItems?.forEach(item => {
            const link = item.querySelector('.tanger-nav-menu-link');
            link?.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleExpandableMenu(item);
            });
        });

        // Window resize handling
        window.addEventListener('resize', () => {
            this.handleResponsive();
        });

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardNavigation(e);
        });

        // Search functionality
        const searchInput = document.querySelector('.tanger-nav-search input');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.handleSearch(e.target.value);
            });
        }

        // User menu interactions
        const userMenu = document.querySelector('.tanger-nav-user');
        if (userMenu) {
            userMenu.addEventListener('click', () => {
                this.toggleUserMenu();
            });
        }

        // Touch event handling
        let touchStartX = 0;
        let touchEndX = 0;

        this.elements.sidebar?.addEventListener('touchstart', (e) => {
            touchStartX = e.changedTouches[0].screenX;
        });

        this.elements.sidebar?.addEventListener('touchend', (e) => {
            touchEndX = e.changedTouches[0].screenX;
            this.handleSwipeGesture(touchStartX, touchEndX);
        });
    }

    toggleMobileMenu() {
        this.state.mobileMenuOpen = !this.state.mobileMenuOpen;
        
        if (this.state.mobileMenuOpen) {
            this.elements.sidebar?.classList.add('mobile-open');
            this.elements.overlay?.classList.add('active');
            document.body.style.overflow = 'hidden';
        } else {
            this.closeMobileMenu();
        }
    }

    closeMobileMenu() {
        this.state.mobileMenuOpen = false;
        this.elements.sidebar?.classList.remove('mobile-open');
        this.elements.overlay?.classList.remove('active');
        document.body.style.overflow = '';
    }

    toggleSidebarCollapse() {
        if (window.innerWidth <= 768) return; // Don't collapse on mobile

        this.state.sidebarCollapsed = !this.state.sidebarCollapsed;
        
        if (this.state.sidebarCollapsed) {
            this.elements.sidebar?.classList.add('collapsed');
        } else {
            this.elements.sidebar?.classList.remove('collapsed');
        }

        // Store state
        localStorage.setItem('tanger-nav-collapsed', this.state.sidebarCollapsed.toString());
        
        // Trigger resize event for content adaptation
        window.dispatchEvent(new Event('resize'));
    }

    toggleExpandableMenu(menuItem) {
        const menuId = menuItem.getAttribute('data-menu-id');
        const isExpanded = menuItem.classList.contains('expanded');
        
        if (isExpanded) {
            menuItem.classList.remove('expanded');
            this.state.expandedMenus = this.state.expandedMenus.filter(id => id !== menuId);
        } else {
            menuItem.classList.add('expanded');
            this.state.expandedMenus.push(menuId);
        }

        // Store expanded state
        localStorage.setItem('tanger-nav-expanded', JSON.stringify(this.state.expandedMenus));
        
        // Animate expansion
        this.animateMenuExpansion(menuItem, !isExpanded);
    }

    animateMenuExpansion(menuItem, expanding) {
        const submenu = menuItem.querySelector('.tanger-nav-submenu');
        if (!submenu) return;

        if (expanding) {
            // Calculate height and animate
            submenu.style.display = 'block';
            const height = submenu.scrollHeight;
            submenu.style.maxHeight = '0';
            submenu.offsetHeight; // Force reflow
            submenu.style.maxHeight = height + 'px';
            
            setTimeout(() => {
                submenu.style.maxHeight = '';
            }, 300);
        } else {
            submenu.style.maxHeight = submenu.scrollHeight + 'px';
            submenu.offsetHeight; // Force reflow
            submenu.style.maxHeight = '0';
        }
    }

    setActiveMenuItem() {
        const currentPath = window.location.pathname;
        
        // Remove existing active states
        document.querySelectorAll('.tanger-nav-menu-link.active, .tanger-nav-submenu-link.active')
            .forEach(link => link.classList.remove('active'));
        
        // Find and set active menu item
        const activeLink = document.querySelector(`[href="${currentPath}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
            
            // If it's a submenu item, expand parent and mark as active
            const parentExpandable = activeLink.closest('.tanger-nav-menu-expandable');
            if (parentExpandable) {
                parentExpandable.classList.add('expanded');
                const parentLink = parentExpandable.querySelector('.tanger-nav-menu-link');
                parentLink?.classList.add('active');
            }
        }
    }

    handleResponsive() {
        const isMobile = window.innerWidth <= 768;
        
        if (isMobile) {
            // Mobile behavior
            this.elements.sidebar?.classList.remove('collapsed');
            if (!this.state.mobileMenuOpen) {
                this.elements.sidebar?.classList.remove('mobile-open');
            }
        } else {
            // Desktop behavior
            this.closeMobileMenu();
            if (this.state.sidebarCollapsed) {
                this.elements.sidebar?.classList.add('collapsed');
            }
        }
    }

    handleKeyboardNavigation(e) {
        // ESC key to close mobile menu
        if (e.key === 'Escape' && this.state.mobileMenuOpen) {
            this.closeMobileMenu();
        }
        
        // Arrow key navigation in menu
        if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
            const focusedElement = document.activeElement;
            if (focusedElement.closest('.tanger-nav-menu')) {
                e.preventDefault();
                this.navigateMenuWithKeyboard(e.key === 'ArrowDown' ? 1 : -1);
            }
        }
        
        // Enter/Space to activate menu items
        if ((e.key === 'Enter' || e.key === ' ') && 
            document.activeElement.classList.contains('tanger-nav-menu-link')) {
            e.preventDefault();
            document.activeElement.click();
        }
    }

    navigateMenuWithKeyboard(direction) {
        const menuItems = Array.from(document.querySelectorAll(
            '.tanger-nav-menu-link, .tanger-nav-submenu-link'
        )).filter(item => !item.closest('.tanger-nav-submenu') || 
                         item.closest('.expanded'));
        
        const currentIndex = menuItems.indexOf(document.activeElement);
        const nextIndex = Math.max(0, Math.min(menuItems.length - 1, currentIndex + direction));
        
        menuItems[nextIndex]?.focus();
    }

    handleSearch(query) {
        if (!query.trim()) {
            this.clearSearchHighlight();
            return;
        }
        
        const menuItems = document.querySelectorAll('.tanger-nav-menu-text, .tanger-nav-submenu-link');
        let hasResults = false;
        
        menuItems.forEach(item => {
            const text = item.textContent.toLowerCase();
            const matches = text.includes(query.toLowerCase());
            
            if (matches) {
                hasResults = true;
                this.highlightSearchResult(item);
                
                // Expand parent menu if it's a submenu item
                const parentExpandable = item.closest('.tanger-nav-menu-expandable');
                if (parentExpandable) {
                    parentExpandable.classList.add('expanded');
                }
            } else {
                this.removeSearchHighlight(item);
            }
        });
        
        // Show "no results" indicator if needed
        this.toggleNoResultsIndicator(!hasResults);
    }

    highlightSearchResult(element) {
        element.classList.add('search-highlighted');
        element.closest('.tanger-nav-menu-item')?.classList.add('search-result');
    }

    removeSearchHighlight(element) {
        element.classList.remove('search-highlighted');
        element.closest('.tanger-nav-menu-item')?.classList.remove('search-result');
    }

    clearSearchHighlight() {
        document.querySelectorAll('.search-highlighted, .search-result')
            .forEach(el => el.classList.remove('search-highlighted', 'search-result'));
        this.toggleNoResultsIndicator(false);
    }

    toggleNoResultsIndicator(show) {
        let indicator = document.querySelector('.search-no-results');
        
        if (show && !indicator) {
            indicator = document.createElement('div');
            indicator.className = 'search-no-results';
            indicator.innerHTML = `
                <div style="padding: 1rem; text-align: center; color: rgba(255,255,255,0.6);">
                    <i class="fas fa-search"></i>
                    <p style="margin: 0.5rem 0 0 0; font-size: 0.875rem;">Aucun résultat trouvé</p>
                </div>
            `;
            document.querySelector('.tanger-nav-menu')?.appendChild(indicator);
        } else if (!show && indicator) {
            indicator.remove();
        }
    }

    toggleUserMenu() {
        // User menu dropdown functionality
        const userMenu = document.querySelector('.tanger-nav-user');
        const dropdown = userMenu?.querySelector('.user-dropdown');
        
        if (dropdown) {
            dropdown.classList.toggle('active');
        }
    }

    // Enhanced touch and responsive handling methods
    handleSwipeGesture(startX, endX) {
        const swipeThreshold = 50;
        const swipeDistance = endX - startX;
        
        if (window.innerWidth <= 768) {
            if (swipeDistance > swipeThreshold && startX < 20) {
                // Swipe right from left edge - open menu
                if (!this.state.mobileMenuOpen) {
                    this.toggleMobileMenu();
                }
            } else if (swipeDistance < -swipeThreshold && this.state.mobileMenuOpen) {
                // Swipe left - close menu
                this.closeMobileMenu();
            }
        }
    }

    handleResize() {
        // Debounced resize handler for better performance
        const isMobile = window.innerWidth <= 768;
        const isTablet = window.innerWidth <= 1024 && window.innerWidth > 768;
        
        if (isMobile !== this.wasMobile) {
            this.wasMobile = isMobile;
            
            if (isMobile) {
                // Switched to mobile
                this.elements.sidebar?.classList.remove('collapsed');
                this.closeMobileMenu();
            } else {
                // Switched to desktop
                this.closeMobileMenu();
                if (this.state.sidebarCollapsed) {
                    this.elements.sidebar?.classList.add('collapsed');
                }
            }
        }
        
        // Update content area margin based on screen size
        this.updateContentMargin();
    }

    updateContentMargin() {
        if (!this.elements.mainContent) return;
        
        const screenWidth = window.innerWidth;
        let marginLeft = '0px';
        
        if (screenWidth > 1440) {
            marginLeft = this.state.sidebarCollapsed ? '65px' : '320px';
        } else if (screenWidth > 1024) {
            marginLeft = this.state.sidebarCollapsed ? '65px' : '280px';
        } else if (screenWidth > 768) {
            marginLeft = '250px';
        }
        
        this.elements.mainContent.style.marginLeft = marginLeft;
    }

    handleFocusTrap(e) {
        if (!this.state.mobileMenuOpen) return;
        
        const focusableElements = this.elements.sidebar?.querySelectorAll(
            'a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        
        if (!focusableElements?.length) return;
        
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];
        
        if (e.shiftKey && document.activeElement === firstElement) {
            e.preventDefault();
            lastElement.focus();
        } else if (!e.shiftKey && document.activeElement === lastElement) {
            e.preventDefault();
            firstElement.focus();
        }
    }

    handleMediaQueryChange(e) {
        if (e.matches) {
            // Mobile view
            this.closeMobileMenu();
            this.elements.sidebar?.classList.remove('collapsed');
        } else {
            // Desktop view
            if (this.state.sidebarCollapsed) {
                this.elements.sidebar?.classList.add('collapsed');
            }
        }
    }

    // Touch event optimization
    optimizeTouch() {
        // Add touch-action CSS for better touch performance
        if ('ontouchstart' in window) {
            document.body.style.touchAction = 'manipulation';
            
            // Add touch-friendly classes
            this.elements.sidebar?.classList.add('touch-optimized');
            this.elements.menuToggle?.classList.add('touch-optimized');
        }
    }

    // Responsive breakpoint detection
    getBreakpoint() {
        const width = window.innerWidth;
        
        if (width >= 1440) return 'xl';
        if (width >= 1024) return 'lg';
        if (width >= 768) return 'md';
        if (width >= 576) return 'sm';
        return 'xs';
    }

    // Debounce utility for performance
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Media query listener for system preferences
    initMediaQueries() {
        // Reduced motion preference
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
        prefersReducedMotion.addEventListener('change', (e) => {
            document.body.classList.toggle('reduced-motion', e.matches);
        });
        
        // High contrast preference
        const prefersHighContrast = window.matchMedia('(prefers-contrast: high)');
        prefersHighContrast.addEventListener('change', (e) => {
            document.body.classList.toggle('high-contrast', e.matches);
        });
        
        // Dark mode preference
        const prefersDarkMode = window.matchMedia('(prefers-color-scheme: dark)');
        prefersDarkMode.addEventListener('change', (e) => {
            document.body.classList.toggle('auto-dark-mode', e.matches);
        });
    }

    // Performance monitoring
    trackPerformance() {
        if ('performance' in window && 'mark' in performance) {
            performance.mark('tanger-nav-init-start');
        }
    }

    // Accessibility announcements
    announceToScreenReader(message) {
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'polite');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.className = 'tanger-nav-sr-only';
        announcement.textContent = message;
        
        document.body.appendChild(announcement);
        
        setTimeout(() => {
            document.body.removeChild(announcement);
        }, 1000);
    }

    // Enhanced initialization with performance tracking
    enhancedInit() {
        this.trackPerformance();
        this.optimizeTouch();
        this.initMediaQueries();
        this.wasMobile = window.innerWidth <= 768;
        
        // Performance mark
        if ('performance' in window && 'mark' in performance) {
            performance.mark('tanger-nav-init-end');
            performance.measure('tanger-nav-init', 'tanger-nav-init-start', 'tanger-nav-init-end');
        }
    }
}

// Search result highlighting styles
const searchStyles = document.createElement('style');
searchStyles.textContent = `
    .search-highlighted {
        background: rgba(0, 188, 212, 0.3) !important;
        border-radius: 4px;
        padding: 2px 4px;
        margin: -2px -4px;
    }
    
    .search-result {
        background: rgba(0, 188, 212, 0.1);
        border-left: 3px solid #00BCD4;
    }
`;
document.head.appendChild(searchStyles);

// Initialize navigation when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.tangerNavigation = new TangerAllianceNavigation();
});

// User Dropdown Functionality
function toggleUserDropdown() {
    const userElement = document.querySelector('.tanger-nav-user');
    const dropdownMenu = document.getElementById('userDropdownMenu');
    
    if (!userElement || !dropdownMenu) return;
    
    const isExpanded = userElement.getAttribute('aria-expanded') === 'true';
    
    if (isExpanded) {
        closeUserDropdown();
    } else {
        openUserDropdown();
    }
}

function openUserDropdown() {
    const userElement = document.querySelector('.tanger-nav-user');
    const dropdownMenu = document.getElementById('userDropdownMenu');
    
    if (!userElement || !dropdownMenu) return;
    
    userElement.setAttribute('aria-expanded', 'true');
    dropdownMenu.classList.add('show');
    
    // Close dropdown when clicking outside
    setTimeout(() => {
        document.addEventListener('click', closeDropdownOnOutsideClick);
    }, 0);
}

function closeUserDropdown() {
    const userElement = document.querySelector('.tanger-nav-user');
    const dropdownMenu = document.getElementById('userDropdownMenu');
    
    if (!userElement || !dropdownMenu) return;
    
    userElement.setAttribute('aria-expanded', 'false');
    dropdownMenu.classList.remove('show');
    
    document.removeEventListener('click', closeDropdownOnOutsideClick);
}

function closeDropdownOnOutsideClick(event) {
    const dropdown = document.querySelector('.tanger-nav-user-dropdown');
    
    if (!dropdown || dropdown.contains(event.target)) return;
    
    closeUserDropdown();
}

// Keyboard navigation for dropdown
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeUserDropdown();
    }
});

// Global utility functions
window.TangerNav = {
    toggle: () => window.tangerNavigation?.toggleSidebarCollapse(),
    expand: (menuId) => window.tangerNavigation?.expandMenu(menuId),
    collapse: (menuId) => window.tangerNavigation?.collapseMenu(menuId),
    navigate: (url) => window.tangerNavigation?.navigateToPage(url),
    toggleUserDropdown: toggleUserDropdown
};

// Make dropdown function globally available
window.toggleUserDropdown = toggleUserDropdown;

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TangerAllianceNavigation;
}
