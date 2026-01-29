// cart.js: AJAX add/remove/update cart and update navbar badge
function updateCartBadge(count) {
  const badge = document.querySelector('.nav-link[href="/cart/"] .badge');
  if (badge) {
    if (count > 0) {
      badge.textContent = count;
      badge.style.display = '';
    } else {
      badge.style.display = 'none';
    }
  }
}

function ajaxAddToCart(productId, onSuccess) {
  fetch(`/cart/add/${productId}/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCSRFToken(),
      'X-Requested-With': 'XMLHttpRequest',
    },
  })
    .then(r => r.json())
    .then(data => {
      updateCartBadge(data.cart_item_count);
      if (onSuccess) onSuccess(data);
    });
}

function ajaxRemoveFromCart(productId, onSuccess) {
  fetch(`/cart/remove/${productId}/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCSRFToken(),
      'X-Requested-With': 'XMLHttpRequest',
    },
  })
    .then(r => r.json())
    .then(data => {
      updateCartBadge(data.cart_item_count);
      if (onSuccess) onSuccess(data);
    });
}

function getCSRFToken() {
  const name = 'csrftoken';
  const cookies = document.cookie.split(';');
  for (let cookie of cookies) {
    cookie = cookie.trim();
    if (cookie.startsWith(name + '=')) {
      return decodeURIComponent(cookie.substring(name.length + 1));
    }
  }
  return '';
}
// Attach event listeners for add-to-cart buttons if present
window.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.btn-add-to-cart').forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      const productId = btn.dataset.productId;
      ajaxAddToCart(productId, () => {
        btn.textContent = 'Added!';
        setTimeout(() => { btn.textContent = 'Add to Cart'; }, 1200);
      });
    });
  });
});
