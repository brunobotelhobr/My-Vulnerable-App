// Cart functionality
async function loadCart() {
    try {
        const response = await fetch('/api/cart');
        if (!response.ok) throw new Error('Failed to fetch cart');
        
        const items = await response.json();
        
        if (items.length === 0) {
            document.getElementById('cartContent').innerHTML = `
                <div class="cart-empty">
                    <i class="fas fa-shopping-cart"></i>
                    <p>Your cart is empty</p>
                    <a href="/" class="btn-primary">Continue Shopping</a>
                </div>
            `;
            return;
        }
        
        let subtotal = 0;
        const itemsHtml = items.map(item => {
            subtotal += item.price * item.quantity;
            return `
                <div class="cart-item">
                    <div class="item-details">
                        <div class="item-info">
                            <h3>${item.name}</h3>
                            <p>${item.description}</p>
                        </div>
                        <div class="item-controls">
                            <div class="item-quantity">
                                <button class="quantity-btn minus" onclick="updateQuantity(${item.id}, ${item.quantity - 1})">
                                    <i class="fas fa-minus"></i>
                                </button>
                                <input type="number" class="quantity-input" value="${item.quantity}" 
                                    min="1" onchange="updateQuantity(${item.id}, this.value)">
                                <button class="quantity-btn plus" onclick="updateQuantity(${item.id}, ${item.quantity + 1})">
                                    <i class="fas fa-plus"></i>
                                </button>
                            </div>
                            <div class="item-price">$${(item.price * item.quantity).toFixed(2)}</div>
                        </div>
                    </div>
                    <button class="remove-item" onclick="removeItem(${item.id})" title="Remove item">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
        }).join('');
        
        const shipping = 5.99;
        const tax = subtotal * 0.1;
        const total = subtotal + shipping + tax;
        
        document.getElementById('cartContent').innerHTML = `
            <div class="cart-items">
                ${itemsHtml}
            </div>
            <div class="cart-summary">
                <div class="summary-row">
                    <span>Subtotal</span>
                    <span>$${subtotal.toFixed(2)}</span>
                </div>
                <div class="summary-row">
                    <span>Shipping</span>
                    <span>$${shipping.toFixed(2)}</span>
                </div>
                <div class="summary-row">
                    <span>Tax (10%)</span>
                    <span>$${tax.toFixed(2)}</span>
                </div>
                <div class="summary-row total">
                    <span>Total</span>
                    <span>$${total.toFixed(2)}</span>
                </div>
                <button class="checkout-btn" onclick="checkout()">
                    <i class="fas fa-shopping-bag"></i> Proceed to Checkout
                </button>
            </div>
        `;
    } catch (error) {
        console.error('Error loading cart:', error);
        document.getElementById('cartContent').innerHTML = `
            <div class="cart-empty">
                <i class="fas fa-exclamation-circle"></i>
                <p>Error loading cart. Please try again.</p>
                <a href="/" class="btn-primary">
                    <i class="fas fa-home"></i> Return to Home
                </a>
            </div>
        `;
    }
}

async function updateQuantity(itemId, newQuantity) {
    if (newQuantity < 1) return;
    
    try {
        const response = await fetch(`/api/cart/${itemId}?quantity=${newQuantity}`, {
            method: 'PUT'
        });
        
        if (!response.ok) throw new Error('Failed to update quantity');
        
        loadCart();
        loadCartCount(); // Update cart count in navbar
    } catch (error) {
        console.error('Error updating quantity:', error);
        alert('Failed to update quantity. Please try again.');
    }
}

async function removeItem(itemId) {
    try {
        const response = await fetch(`/api/cart/${itemId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('Failed to remove item');
        
        loadCart();
        loadCartCount(); // Update cart count in navbar
    } catch (error) {
        console.error('Error removing item:', error);
        alert('Failed to remove item. Please try again.');
    }
}

async function backupCart() {
    try {
        const response = await fetch('/api/cart/export');
        if (!response.ok) throw new Error('Failed to backup cart');
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'cart-backup.json';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    } catch (error) {
        console.error('Error backing up cart:', error);
        alert('Failed to backup cart. Please try again.');
    }
}

async function restoreCart(event) {
    const file = event.target.files[0];
    if (!file) return;

    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/api/cart/import', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error('Failed to restore cart');
        
        loadCart();
        loadCartCount(); // Update cart count in navbar
    } catch (error) {
        console.error('Error restoring cart:', error);
        alert('Failed to restore cart. Please try again.');
    }
}

function checkout() {
    // Implement checkout functionality
    alert('Checkout functionality coming soon!');
}

// Initialize when the page loads
document.addEventListener('DOMContentLoaded', () => {
    if (!auth.isLoggedIn()) {
        window.location.href = '/login.html';
    } else {
        loadCart();
    }
}); 