document.addEventListener('DOMContentLoaded', function () {
  let cart = JSON.parse(localStorage.getItem('cart')) || [];
  const cartItemsContainer = document.getElementById('checkoutCartItems');
  const cartTotalDisplay = document.getElementById('cartTotal');
  const checkoutForm = document.getElementById('checkoutForm');

  function renderCheckoutCart() {
    cartItemsContainer.innerHTML = '';
    let total = 0;

    if (cart.length === 0) {
      cartItemsContainer.innerHTML = '<p class="text-center text-gray-500">Your cart is empty.</p>';
      return;
    }

    cart.forEach(item => {
      const div = document.createElement('div');
      div.className = 'flex justify-between items-center border-b py-4';
      const subtotal = item.price * item.quantity;
      total += subtotal;

      div.innerHTML = `
        <div class="flex items-center">
          <img src="${item.image}" alt="${item.name}" class="w-16 h-16 object-cover mr-4 rounded">
          <div>
            <h3 class="font-semibold">${item.name}</h3>
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

  checkoutForm.addEventListener('submit', function (e) {
  e.preventDefault();

  // Calculate total again (or reuse variable)
  let total = 0;
  cart.forEach(item => {
    total += item.price * item.quantity;
  });

  // Set total in hidden input (in pesewas, if needed)
  document.getElementById('totalPriceInput').value = total;

  const shippingData = {
    name: checkoutForm.shipping_name.value,
    phone: checkoutForm.shipping_phone.value,
    address: checkoutForm.shipping_address.value,
    region: checkoutForm.shipping_region.value,
    district: checkoutForm.shipping_district.value,
    town: checkoutForm.shipping_town.value,
    payment_method: document.getElementById('paymentMethod').value
  };

  if (!shippingData.name || !shippingData.phone || !shippingData.address ||
      !shippingData.region || !shippingData.district || !shippingData.town || !shippingData.payment_method) {
    alert("Please fill in all required fields including payment method.");
    return;
  }

  localStorage.setItem('cart', JSON.stringify(cart));
  localStorage.setItem('shipping', JSON.stringify(shippingData));

  // Now submit the form normally with total included
  checkoutForm.submit();
});


  // Pre-fill form if data exists in localStorage
  const savedShipping = JSON.parse(localStorage.getItem('shipping')) || {};
  checkoutForm.shipping_name.value = savedShipping.name || '';
  checkoutForm.shipping_phone.value = savedShipping.phone || '';
  checkoutForm.shipping_address.value = savedShipping.address || '';
  checkoutForm.shipping_region.value = savedShipping.region || '';
  checkoutForm.shipping_district.value = savedShipping.district || '';
  checkoutForm.shipping_town.value = savedShipping.town || '';
  document.getElementById('paymentMethod').value = savedShipping.payment_method || '';

  renderCheckoutCart();
});
