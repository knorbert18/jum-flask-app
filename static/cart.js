document.addEventListener('DOMContentLoaded', () => {
  const cartItemsContainer = document.getElementById('cartItemsContainer');
  const cartItemsList = document.getElementById('cartItemsList');
  const cartEmptyMessage = document.getElementById('cartEmptyMessage');
  const cartTotalEl = document.getElementById('cartTotalPrice');
  const cartCountEl = document.getElementById('cartCount');
  const cartCountElMobile = document.getElementById('cartCountMobile');

  let cart = [];

  async function fetchCart() {
    try {
      const res = await fetch('/api/cart');
      const data = await res.json();
      cart = data.cart || [];
      renderCart();
    } catch (err) {
      console.error('Failed to fetch cart:', err);
    }
  }

  async function updateCartItem(productId, quantity) {
    try {
      await fetch('/api/cart/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: productId, quantity })
      });
    } catch (err) {
      console.error('Error updating item:', err);
    }
  }

  async function removeCartItem(productId) {
    try {
      await fetch('/api/cart/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: productId })
      });
    } catch (err) {
      console.error('Error removing item:', err);
    }
  }

  function updateCartCount() {
    const cartCount = cart.reduce((sum, item) => sum + item.quantity, 0);
    if (cartCountEl) cartCountEl.innerText = cartCount;
    if (cartCountElMobile) cartCountElMobile.innerText = cartCount;
  }

  function renderCart() {
    cartItemsList.innerHTML = '';
    let total = 0;

    if (cart.length === 0) {
      cartItemsContainer.classList.add('hidden');
      cartEmptyMessage.classList.remove('hidden');
    } else {
      cartItemsContainer.classList.remove('hidden');
      cartEmptyMessage.classList.add('hidden');
    }

    cart.forEach((item, index) => {
      const li = document.createElement('li');
      li.className = 'flex items-center justify-between bg-white dark:bg-gray-800 p-4 rounded shadow';

      const subtotal = item.product.price * item.quantity;
      total += subtotal;

      li.innerHTML = `
        <div class="flex items-center gap-4">
          <img src="${item.product.image}" alt="${item.product.name}" class="w-20 h-20 object-cover rounded" />
          <div>
            <h4 class="font-semibold">${item.product.name}</h4>
            <p class="text-sm text-gray-500 dark:text-gray-400">Price: GH₵${item.product.price}</p>
            <div class="flex items-center mt-2">
              <button class="px-2 py-1 bg-gray-200 dark:bg-gray-700 rounded decrease-btn">-</button>
              <span class="mx-2">${item.quantity}</span>
              <button class="px-2 py-1 bg-gray-200 dark:bg-gray-700 rounded increase-btn">+</button>
            </div>
          </div>
        </div>
        <div class="flex flex-col items-end gap-2">
          <span class="font-bold">GH₵${subtotal.toFixed(2)}</span>
          <button class="text-red-500 hover:underline remove-btn">
            <i class="fas fa-trash-alt"></i> Remove
          </button>
        </div>
      `;

      // Quantity adjustment
      li.querySelector('.decrease-btn').addEventListener('click', async () => {
        if (item.quantity > 1) {
          item.quantity--;
          await updateCartItem(item.product_id, item.quantity);
        } else {
          cart.splice(index, 1);
          await removeCartItem(item.product_id);
        }
        await fetchCart();
      });

      li.querySelector('.increase-btn').addEventListener('click', async () => {
        item.quantity++;
        await updateCartItem(item.product_id, item.quantity);
        await fetchCart();
      });

      li.querySelector('.remove-btn').addEventListener('click', async () => {
        cart.splice(index, 1);
        await removeCartItem(item.product_id);
        await fetchCart();
      });

      cartItemsList.appendChild(li);
    });

    if (cartTotalEl) {
      cartTotalEl.textContent = `Total: GH₵${total.toFixed(2)}`;
    }

    updateCartCount();
  }

  // Load cart on page load
  fetchCart();
});
