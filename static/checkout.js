document.addEventListener('DOMContentLoaded', function () {
  let cart = [];
  const cartItemsContainer = document.getElementById('checkoutCartItems');
  const cartTotalDisplay = document.getElementById('cartTotal');
  const checkoutForm = document.getElementById('checkoutForm');

  // Fetch cart from server
  async function fetchCart() {
    try {
      const res = await fetch('/api/cart');
      const data = await res.json();
      cart = data.cart || [];
      renderCheckoutCart();
    } catch (err) {
      console.error('Failed to fetch cart:', err);
      cartItemsContainer.innerHTML = '<p class="text-center text-red-500">Failed to load cart.</p>';
    }
  }

  // Render the cart items on the checkout page
  function renderCheckoutCart() {
    cartItemsContainer.innerHTML = '';
    let total = 0;

    if (cart.length === 0) {
      cartItemsContainer.innerHTML = '<p class="text-center text-gray-500">Your cart is empty.</p>';
      cartTotalDisplay.textContent = 'GH₵ 0.00';
      return;
    }

    cart.forEach(item => {
      const div = document.createElement('div');
      div.className = 'flex justify-between items-center border-b py-4';

      const subtotal = item.product.price * item.quantity;
      total += subtotal;

      div.innerHTML = `
        <div class="flex items-center">
          <img src="${item.product.image}" alt="${item.product.name}" class="w-16 h-16 object-cover mr-4 rounded">
          <div>
            <h3 class="font-semibold">${item.product.name}</h3>
            <p class="text-sm text-gray-600">Quantity: ${item.quantity}</p>
          </div>
        </div>
        <div class="text-right">
          <p class="text-lg font-semibold">GH₵${subtotal.toFixed(2)}</p>
        </div>
      `;

      cartItemsContainer.appendChild(div);
    });

    cartTotalDisplay.textContent = `GH₵ ${total.toFixed(2)}`;
  }

  // Handle form submission
  checkoutForm.addEventListener('submit', async function (e) {
    e.preventDefault();

    // Fetch the latest cart before submission
    try {
      const res = await fetch('/api/cart');
      const data = await res.json();
      cart = data.cart || [];
    } catch (err) {
      alert('Failed to fetch cart. Please try again.');
      return;
    }

    // Calculate total
    let total = 0;
    cart.forEach(item => {
      total += item.product.price * item.quantity;
    });

    // Set total in hidden input (in case you need it server-side)
    document.getElementById('totalPriceInput').value = total;

    // Gather shipping form data
    const shippingData = {
      name: checkoutForm.shipping_name.value,
      phone: checkoutForm.shipping_phone.value,
      address: checkoutForm.shipping_address.value,
      region: checkoutForm.shipping_region.value,
      district: checkoutForm.shipping_district.value,
      town: checkoutForm.shipping_town.value,
      payment_method: document.getElementById('paymentMethod').value
    };

    // Simple validation
    if (!shippingData.name || !shippingData.phone || !shippingData.address ||
        !shippingData.region || !shippingData.district || !shippingData.town || !shippingData.payment_method) {
      alert("Please fill in all required fields including payment method.");
      return;
    }

    // Submit form to the backend
    checkoutForm.submit();
  });

  // Initial cart fetch on page load
  fetchCart();
});
