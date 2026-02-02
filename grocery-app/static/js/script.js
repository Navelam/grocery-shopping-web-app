// ==================== CART FUNCTIONS ====================

// Add product to cart
function addToCart(productId, productName) {
    fetch(`/add-to-cart/${productId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin'
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            showNotification(`✅ "${productName}" added to cart!`, 'success');
            updateCartCount();
        } else {
            showNotification('❌ Failed to add to cart', 'error');
        }
    })
    .catch(err => {
        showNotification('❌ Error adding to cart', 'error');
        console.error(err);
    });
}

// Update cart item count badge
function updateCartCount() {
    fetch('/cart_count')
        .then(res => res.json())
        .then(data => {
            const badge = document.getElementById('cart-count-badge');
            if (badge) badge.innerText = data.count;
        })
        .catch(err => console.error(err));
}

// Increase / Decrease quantity (LIVE price update)
function updateQuantity(cartId, newQty) {
    fetch(`/update_quantity/${cartId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
        body: JSON.stringify({ quantity: parseInt(newQty) })
    })
    .then(res => res.json())
    .then(data => {
        if (!data.success) {
            showNotification(data.message || '❌ Update failed', 'error');
            return;
        }

        const qtyEl = document.getElementById(`qty-${cartId}`);
        const row = document.getElementById(`row-${cartId}`);
        const totalEl = document.getElementById(`total-${cartId}`);

        const price = parseFloat(
            row.querySelector('.item-price').dataset.price
        );

        qtyEl.innerText = newQty;
        totalEl.innerText = `₹${(price * newQty).toFixed(2)}`;

        updateCartSummary();
        showNotification('✅ Quantity updated', 'success');
    })
    .catch(err => console.error(err));
}

// Remove item from cart
function removeFromCart(cartId) {
    if (!confirm('Remove this item from cart?')) return;

    fetch(`/remove_from_cart/${cartId}`, {
        method: 'POST',
        credentials: 'same-origin'
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            document.getElementById(`row-${cartId}`).remove();
            updateCartSummary();
            updateCartCount();
            showNotification('✅ Item removed', 'success');
        } else {
            showNotification(data.message || '❌ Remove failed', 'error');
        }
    })
    .catch(err => console.error(err));
}

// ==================== CART SUMMARY ====================

function updateCartSummary() {
    let subtotal = 0;

    document.querySelectorAll('.item-total').forEach(el => {
        subtotal += parseFloat(el.innerText.replace('₹', '')) || 0;
    });

    document.getElementById('subtotal').innerText = `₹${subtotal.toFixed(2)}`;
    document.getElementById('grand-total').innerText = `₹${subtotal.toFixed(2)}`;
}

// ==================== FORM VALIDATION ====================

function validateEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;

    let isValid = true;

    form.querySelectorAll('input[required]').forEach(input => {
        input.classList.remove('error');

        if (!input.value.trim()) {
            input.classList.add('error');
            isValid = false;
        }

        if (input.type === 'email' && !validateEmail(input.value)) {
            input.classList.add('error');
            isValid = false;
        }
    });

    return isValid;
}

// ==================== SEARCH & FILTER ====================

function filterByCategory(category) {
    window.location.href =
        category === 'all' ? '/products' : `/products?category=${category}`;
}

function searchProducts() {
    const input = document.getElementById('search-input');
    if (!input || !input.value.trim()) return;

    window.location.href = `/products?search=${encodeURIComponent(input.value)}`;
}

// ==================== CHECKOUT ====================

function confirmCheckout() {
    if (!validateForm('checkout-form')) return false;
    return confirm('✅ Confirm your order?');
}

// ==================== NOTIFICATIONS ====================

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.textContent = message;

    Object.assign(notification.style, {
        position: 'fixed',
        top: '80px',
        right: '1rem',
        zIndex: 1000,
        animation: 'slideIn 0.3s ease'
    });

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 2000);
}

// ==================== PAGE ANIMATIONS ====================

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.card, .alert').forEach((el, i) => {
        el.style.animation = `fadeIn 0.5s ease ${i * 0.1}s both`;
    });
});

// ==================== CSS ANIMATIONS ====================

const style = document.createElement('style');
style.textContent = `
@keyframes fadeIn {
    from { opacity:0; transform:translateY(10px); }
    to { opacity:1; transform:translateY(0); }
}
@keyframes slideIn {
    from { transform:translateX(400px); opacity:0; }
    to { transform:translateX(0); opacity:1; }
}
@keyframes slideOut {
    from { transform:translateX(0); opacity:1; }
    to { transform:translateX(400px); opacity:0; }
}
input.error {
    border-color:#ef4444;
    background-color:#fee2e2;
}
`;
document.head.appendChild(style);
