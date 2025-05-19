document.addEventListener('DOMContentLoaded', () => {
  const cartItemsContainer = document.getElementById('cartItemsContainer');
  const cartItemsList = document.getElementById('cartItemsList');
  const cartEmptyMessage = document.getElementById('cartEmptyMessage');
  const cartTotalEl = document.getElementById('cartTotalPrice');
  const cartCountEl = document.getElementById('cartCount');
  const cartCountElMobile = document.getElementById('cartCountMobile');

  function getCart() {
    return JSON.parse(localStorage.getItem('cart')) || [];
  }

  function saveCart(cart) {
    localStorage.setItem('cart', JSON.stringify(cart));
    document.dispatchEvent(new CustomEvent('cartUpdated'));
  }

  function updateCartCount() {
    const cart = getCart();
    let cartCount = 0;
    for (const item of cart) {
      cartCount += item.quantity || 1;
    }
    if (cartCountEl) cartCountEl.innerText = cartCount;
    if (cartCountElMobile) cartCountElMobile.innerText = cartCount;
  }

  function renderCart() {
    const cart = getCart();
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

      const subtotal = item.price * item.quantity;
      total += subtotal;

      li.innerHTML = `
        <div class="flex items-center gap-4">
          <img src="${item.image}" alt="${item.name}" class="w-20 h-20 object-cover rounded" />
          <div>
            <h4 class="font-semibold">${item.name}</h4>
            <p class="text-sm text-gray-500 dark:text-gray-400">Price: GH₵${item.price}</p>
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
      li.querySelector('.decrease-btn').addEventListener('click', () => {
        if (item.quantity > 1) {
          item.quantity--;
        } else {
          cart.splice(index, 1);
        }
        saveCart(cart);
        renderCart();
      });

      li.querySelector('.increase-btn').addEventListener('click', () => {
        item.quantity++;
        saveCart(cart);
        renderCart();
      });

      // Remove item
      li.querySelector('.remove-btn').addEventListener('click', () => {
        cart.splice(index, 1);
        saveCart(cart);
        renderCart();
      });

      cartItemsList.appendChild(li);
    });

    if (cartTotalEl) {
      cartTotalEl.textContent = `Total: GH₵${total.toFixed(2)}`;
    }

    updateCartCount(); // Update count when cart is rendered
  }

  // Listen for cart updates from other scripts/pages
  document.addEventListener('cartUpdated', updateCartCount);

  renderCart(); // Initial render
});
