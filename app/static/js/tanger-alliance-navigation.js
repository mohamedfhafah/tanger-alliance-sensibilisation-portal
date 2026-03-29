class TangerAllianceNavigation {
    constructor() {
        this.sidebar = document.querySelector('.tanger-nav-sidebar');
        this.mainContent = document.querySelector('.tanger-nav-main-content');
        this.menuToggle = document.querySelector('.tanger-nav-menu-toggle');
        this.overlay = document.querySelector('.tanger-nav-overlay');
        this.expandables = document.querySelectorAll('.tanger-nav-menu-expandable');
        this.searchInput = document.querySelector('.tanger-nav-search input');
        this.mobileBreakpoint = 1080;

        if (!this.sidebar || !this.menuToggle) {
            return;
        }

        this.state = {
            collapsed: localStorage.getItem('ta-sidebar-collapsed') === 'true',
            mobileOpen: false
        };

        this.bind();
        this.restore();
        this.setActiveMenuItem();
        this.handleResize();
    }

    bind() {
        this.menuToggle.addEventListener('click', (event) => {
            event.preventDefault();
            if (window.innerWidth <= this.mobileBreakpoint) {
                this.toggleMobileMenu();
            } else {
                this.toggleSidebarCollapse();
            }
        });

        this.overlay?.addEventListener('click', () => this.closeMobileMenu());

        this.expandables.forEach((item) => {
            const trigger = item.querySelector('.tanger-nav-menu-link');
            trigger?.addEventListener('click', (event) => {
                event.preventDefault();
                const expanded = item.classList.toggle('expanded');
                trigger.setAttribute('aria-expanded', expanded ? 'true' : 'false');
            });
        });

        this.searchInput?.addEventListener('input', (event) => {
            this.filterNavigation(event.target.value);
        });

        window.addEventListener('resize', () => this.handleResize());
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') {
                this.closeMobileMenu();
                closeUserDropdown();
            }
        });
    }

    restore() {
        if (this.state.collapsed && window.innerWidth > this.mobileBreakpoint) {
            this.sidebar.classList.add('collapsed');
            this.mainContent?.classList.add('sidebar-collapsed');
        }
    }

    toggleSidebarCollapse() {
        this.state.collapsed = !this.state.collapsed;
        this.sidebar.classList.toggle('collapsed', this.state.collapsed);
        this.mainContent?.classList.toggle('sidebar-collapsed', this.state.collapsed);
        localStorage.setItem('ta-sidebar-collapsed', String(this.state.collapsed));
    }

    toggleMobileMenu() {
        this.state.mobileOpen = !this.state.mobileOpen;
        this.sidebar.classList.toggle('mobile-open', this.state.mobileOpen);
        this.overlay?.classList.toggle('active', this.state.mobileOpen);
        this.menuToggle.setAttribute('aria-expanded', this.state.mobileOpen ? 'true' : 'false');
        document.body.style.overflow = this.state.mobileOpen ? 'hidden' : '';
    }

    closeMobileMenu() {
        this.state.mobileOpen = false;
        this.sidebar?.classList.remove('mobile-open');
        this.overlay?.classList.remove('active');
        this.menuToggle?.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
    }

    handleResize() {
        if (window.innerWidth > this.mobileBreakpoint) {
            this.closeMobileMenu();
            this.sidebar.classList.toggle('collapsed', this.state.collapsed);
            this.mainContent?.classList.toggle('sidebar-collapsed', this.state.collapsed);
        } else {
            this.sidebar.classList.remove('collapsed');
            this.mainContent?.classList.remove('sidebar-collapsed');
        }
    }

    setActiveMenuItem() {
        const currentPath = window.location.pathname;
        const links = document.querySelectorAll('.tanger-nav-menu-link, .tanger-nav-submenu-link');

        links.forEach((link) => {
            const href = link.getAttribute('href');
            if (!href || href === '#') {
                return;
            }

            if (href === currentPath) {
                link.classList.add('active');
                const expandable = link.closest('.tanger-nav-menu-expandable');
                if (expandable) {
                    expandable.classList.add('expanded');
                    expandable.querySelector('.tanger-nav-menu-link')?.setAttribute('aria-expanded', 'true');
                }
            }
        });
    }

    filterNavigation(query) {
        const text = query.trim().toLowerCase();
        const items = document.querySelectorAll('.tanger-nav-menu-item');

        items.forEach((item) => {
            const label = item.textContent.toLowerCase();
            const match = !text || label.includes(text);
            item.style.display = match ? '' : 'none';

            if (match) {
                item.classList.add('search-result');
            } else {
                item.classList.remove('search-result');
            }
        });
    }
}

function toggleUserDropdown() {
    const trigger = document.querySelector('.tanger-nav-user');
    const menu = document.getElementById('userDropdownMenu');

    if (!trigger || !menu) {
        return;
    }

    const isOpen = menu.classList.contains('show');
    menu.classList.toggle('show', !isOpen);
    trigger.setAttribute('aria-expanded', !isOpen ? 'true' : 'false');

    if (!isOpen) {
        setTimeout(() => document.addEventListener('click', closeDropdownOnOutsideClick), 0);
    } else {
        document.removeEventListener('click', closeDropdownOnOutsideClick);
    }
}

function closeUserDropdown() {
    const trigger = document.querySelector('.tanger-nav-user');
    const menu = document.getElementById('userDropdownMenu');

    if (!trigger || !menu) {
        return;
    }

    menu.classList.remove('show');
    trigger.setAttribute('aria-expanded', 'false');
    document.removeEventListener('click', closeDropdownOnOutsideClick);
}

function closeDropdownOnOutsideClick(event) {
    const dropdown = document.querySelector('.tanger-nav-user-dropdown');
    if (dropdown && !dropdown.contains(event.target)) {
        closeUserDropdown();
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.tangerNavigation = new TangerAllianceNavigation();
});

window.toggleUserDropdown = toggleUserDropdown;
