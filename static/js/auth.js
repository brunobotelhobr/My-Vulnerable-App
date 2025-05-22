// Authentication functions
const auth = {
    async login(username, password) {
        try {
            const formData = new URLSearchParams();
            formData.append('username', username);
            formData.append('password', password);

            const response = await fetch('/token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: formData
            });

            if (!response.ok) {
                throw new Error('Login failed');
            }

            const data = await response.json();
            // Parse the JWT to get the user ID
            const payload = JSON.parse(atob(data.access_token.split('.')[1]));
            
            // Store token and user ID in cookies
            document.cookie = `token=${data.access_token}; path=/`;
            document.cookie = `user_id=${payload.user_id}; path=/`;
            
            this.updateUI();
            window.location.href = '/home.html';
            return true;
        } catch (error) {
            console.error('Login error:', error);
            return false;
        }
    },

    async register(username, password) {
        try {
            const response = await fetch('/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Registration failed');
            }

            // After successful registration, automatically log in
            return await this.login(username, password);
        } catch (error) {
            console.error('Registration error:', error);
            throw error;
        }
    },

    getToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'token') {
                return value;
            }
        }
        return null;
    },

    getUserId() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'user_id') {
                return value;
            }
        }
        return null;
    },

    isLoggedIn() {
        return !!this.getToken();
    },

    logout() {
        // Remove cookies
        document.cookie = 'token=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT';
        document.cookie = 'user_id=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT';
        this.updateUI();
        window.location.href = '/login.html';
    },

    async apiRequest(url, method = 'GET', body = null) {
        const token = this.getToken();
        if (!token) {
            throw new Error('Not authenticated');
        }

        const options = {
            method,
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        };

        if (body) {
            options.body = JSON.stringify(body);
        }

        const response = await fetch(url, options);
        
        if (!response.ok) {
            if (response.status === 401) {
                throw new Error('Session expired');
            }
            throw new Error('Request failed');
        }

        return response.json();
    },

    updateUI() {
        const loggedIn = this.isLoggedIn();
        document.querySelectorAll('.guest-only').forEach(el => {
            el.style.display = loggedIn ? 'none' : 'flex';
        });
        document.querySelectorAll('.auth-only').forEach(el => {
            el.style.display = loggedIn ? 'flex' : 'none';
        });
    }
};

// Add Authorization header to all fetch requests
const originalFetch = window.fetch;
window.fetch = function(url, options = {}) {
    options.headers = options.headers || {};
    const token = auth.getToken();
    
    if (token && !url.endsWith('/token')) {
        options.headers['Authorization'] = `Bearer ${token}`;
    }
    
    return originalFetch(url, options);
};

// Check if user is logged in when accessing protected pages
if (document.querySelector('.auth-only')) {
    if (!auth.isLoggedIn()) {
        window.location.href = '/login.html';
    }
}

// Handle logout button click
document.getElementById('logoutButton')?.addEventListener('click', (e) => {
    e.preventDefault();
    auth.logout();
});

// Initialize UI
auth.updateUI();

// Export auth object
window.auth = auth; 