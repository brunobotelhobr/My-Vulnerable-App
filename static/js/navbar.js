// Navbar Component
function renderNavbar() {
    const navHtml = `
        <nav class="navbar">
            <div class="nav-container">
                <a href="/" class="nav-brand">FishingStore</a>
                <div class="nav-menu">
                    <div class="cart-icon" id="cartIcon">
                        <i class="fas fa-shopping-cart"></i>
                        <span class="cart-count">0</span>
                    </div>
                    <a href="/challenge.html" class="cart-icon">
                        <i class="fas fa-flag"></i>
                    </a>
                    <div class="user-menu">
                        <button class="user-menu-btn" id="userMenuBtn">
                            <i class="fas fa-user"></i>
                            <span>Account</span>
                            <i class="fas fa-chevron-down"></i>
                        </button>
                        <div class="user-menu-content" id="userMenuContent">
                            <a href="/profile.html" class="user-menu-item">
                                <i class="fas fa-user-circle"></i>My Address
                            </a>
                            <a href="/orders.html" class="user-menu-item">
                                <i class="fas fa-box"></i>Orders
                            </a>
                            <a href="/change-password.html" class="user-menu-item">
                                <i class="fas fa-key"></i>Change Password
                            </a>
                            <hr class="menu-divider">
                            <a href="#" class="user-menu-item" id="logoutButton">
                                <i class="fas fa-sign-out-alt"></i>Logout
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </nav>
    `;

    // Insert navbar at the beginning of the body
    document.body.insertAdjacentHTML('afterbegin', navHtml);

    // Setup event listeners
    setupNavbarEventListeners();
}

function setupNavbarEventListeners() {
    // User menu toggle
    const userMenuBtn = document.getElementById('userMenuBtn');
    const userMenuContent = document.getElementById('userMenuContent');

    if (userMenuBtn && userMenuContent) {
        userMenuBtn.addEventListener('click', () => {
            userMenuContent.classList.toggle('show');
        });

        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!userMenuBtn.contains(e.target) && !userMenuContent.contains(e.target)) {
                userMenuContent.classList.remove('show');
            }
        });
    }

    // Logout button
    const logoutButton = document.getElementById('logoutButton');
    if (logoutButton) {
        logoutButton.addEventListener('click', (e) => {
            e.preventDefault();
            auth.logout();
            window.location.href = '/';
        });
    }

    // Load cart count
    loadCartCount();
}

async function loadCartCount() {
    try {
        const response = await fetch('/api/cart/count');
        if (!response.ok) throw new Error('Failed to fetch cart count');
        
        const result = await response.json();
        const cartCount = document.querySelector('.cart-count');
        if (cartCount) {
            cartCount.textContent = result.count;
        }
    } catch (error) {
        console.error('Error loading cart count:', error);
    }
}

// Initialize navbar when the script loads
document.addEventListener('DOMContentLoaded', () => {
    if (auth.isLoggedIn()) {
        renderNavbar();
    }
}); 