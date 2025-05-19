  document.addEventListener("DOMContentLoaded", () => {
     const productsData = [
    { id: 1, name: "Ladies Handbag", price: 0.01, image: "static/images/handbag1.jpg", category: "Ladies" },
    { id: 2, name: "Men's Sneakers", price: 300, image: "static/images/mensneakers.jpeg", category: "Men" },
    { id: 3, name: "Kids Backpack", price: 90, image: "static/images/kidsbag.jpeg", category: "Children" },
    { id: 4, name: "Smartphone A15", price: 1200, image: "static/images/smartphone1.jpeg", category: "Mobile" },
    { id: 5, name: "Gold Earrings", price: 800, image: "static/images/earrings.jpg", category: "Jewelries" },
    { id: 6, name: "Bluetooth Speaker", price: 350, image: "static/images/speaker.jpeg", category: "Electronics" },
    { id: 7, name: "LED Table Lamp", price: 120, image: "static/images/lamp.jpeg", category: "Home" },
    { id: 8, name: "Ladies Sunglasses", price: 110, image: "static/images/sunglasses.jpeg", category: "Accessories" },
    { id: 9, name: "Men's T-shirt", price: 85, image: "static/images/tshirt_men.jpeg", category: "Men" },
    { id: 10, name: "Children’s Puzzle Game", price: 60, image: "static/images/puzzle.jpeg", category: "Children" },
    { id: 11, name: "Mobile Power Bank", price: 180, image: "static/images/powerbank.jpeg", category: "Mobile" },
    { id: 12, name: "Diamond Bracelet", price: 1200, image: "static/images/bracelet.jpeg", category: "Jewelries" },
    { id: 13, name: "Flat Screen TV 43\"", price: 2100, image: "static/images/tv.jpeg", category: "Electronics" },
    { id: 14, name: "Cushion Pillow Set", price: 150, image: "static/images/pillow.jpeg", category: "Home" },
    { id: 15, name: "Ladies Sandals", price: 130, image: "static/images/ladies_sandals.jpg", category: "Ladies" },
    { id: 16, name: "Men’s Leather Wallet", price: 95, image: "static/images/wallet.jpeg", category: "Men" },
    { id: 17, name: "Toy Car Set", price: 70, image: "static/images/toycar.jpeg", category: "Children" },
    { id: 18, name: "Smartwatch Pro", price: 650, image: "static/images/smartwatch.jpeg", category: "Mobile" },
    { id: 19, name: "Silver Necklace", price: 450, image: "static/images/necklace.jpeg", category: "Jewelries" },
    { id: 20, name: "Wireless Earbuds", price: 290, image: "static/images/earbuds.jpeg", category: "Electronics" },
    { id: 21, name: "Tablecloth Set", price: 85, image: "static/images/tablecloth.jpg", category: "Home" },
    { id: 22, name: "Ladies Watch", price: 320, image: "static/images/ladies_watch.png", category: "Accessories" },
    { id: 23, name: "Men’s Cap", price: 55, image: "static/images/mens_cap.jpeg", category: "Men" },
    { id: 24, name: "Building Blocks", price: 95, image: "static/images/blocks.jpeg", category: "Children" },
    { id: 25, name: "Android Charger", price: 45, image: "static/images/charger.jpeg", category: "Mobile" },
    { id: 26, name: "Pearl Ring", price: 750, image: "static/images/pearl_ring.jpg", category: "Jewelries" },
    { id: 27, name: "Bluetooth Keyboard", price: 270, image: "static/images/keyboard.jpeg", category: "Electronics" },
    { id: 28, name: "Curtain Set", price: 220, image: "static/images/curtains.jpeg", category: "Home" },
    { id: 29, name: "Ladies Purse", price: 140, image: "static/images/purse.jpeg", category: "Ladies" },
    { id: 30, name: "Men’s Belt", price: 90, image: "static/images/belt.jpeg", category: "Men" },
    { id: 31, name: "Kids Drawing Kit", price: 65, image: "static/images/drawingkit.png", category: "Children" },
    { id: 32, name: "iPhone Case", price: 80, image: "static/images/iphonecase.jpeg", category: "Mobile" },
    { id: 33, name: "Gold Plated Chain", price: 950, image: "static/images/chain.jpg", category: "Jewelries" },
    { id: 34, name: "Laptop Cooling Pad", price: 200, image: "static/images/coolingpad.jpg", category: "Electronics" },
    { id: 35, name: "Wall Clock", price: 160, image: "static/images/clock.jpg", category: "Home" },
    { id: 36, name: "Hair Scrunchies", price: 35, image: "static/images/scrunchies.jpeg", category: "Accessories" },
    { id: 37, name: "Men’s Cologne", price: 290, image: "static/images/cologne.jpg", category: "Men" },
    { id: 38, name: "Kids Story Book", price: 40, image: "static/images/storybook.jpeg", category: "Children" },
    { id: 39, name: "USB Type-C Cable", price: 50, image: "static/images/usb.jpeg", category: "Mobile" },
  { id: 40, name: "Gemstone Earrings", price: 680, image: "static/images/gem_earrings.jpeg", category: "Jewelries" },
  { id: 41, name: "Wireless Game Controller", price: 275, image: "static/images/wireless.jpg", category: "Gaming" },
  { id: 42, name: "Table Runner", price: 75, image: "static/images/tablerunner.jpg", category: "Home" },
  { id: 43, name: "Ladies Beanie Hat", price: 60, image: "static/images/beanie.jpeg", category: "Ladies" },
  { id: 44, name: "Men’s Dress Shirt", price: 200, image: "static/images/shirt.png", category: "Men" },
  { id: 45, name: "Kids Socks Set", price: 45, image: "static/images/socks.jpg", category: "Children" },
  { id: 46, name: "Wireless Charger", price: 240, image: "static/images/wireless_charger.png", category: "Mobile" },
  { id: 47, name: "Jade Bangle", price: 890, image: "static/images/jade_bangle.jpeg", category: "Jewelries" },
  { id: 48, name: "Bluetooth Mouse", price: 170, image: "static/images/mouse.jpeg", category: "Electronics" },
  { id: 49, name: "Floor Rug", price: 350, image: "static/images/rug.jpeg", category: "Home" },
  { id: 50, name: "Fashion Scarf", price: 100, image: "static/images/scarf.jpeg", category: "Accessories" },
  { id: 51, name: "Slippers", price: 150, image: "static/images/slippers.jpeg", category: "Footwear" },
  { id: 52, name: "Double Controller", price: 185, image: "static/images/doublecontroller.jpeg", category: "Gaming" },
  { id: 53, name: "2-in-1 Joypad", price: 105, image: "static/images/2in1.jpeg", category: "Gaming" },
  { id: 54, name: "Switch Gamepad", price: 688.90, image: "static/images/switch.jpeg", category: "Gaming" },
  { id: 55, name: "Adidas Predator", price: 150, image: "static/images/adidas_predator.jpeg", category: "Sports" }
];

    let cart = JSON.parse(localStorage.getItem("cart")) || [];

    function formatPrice(price) {
      return `GH₵${price.toFixed(2)}`;
    }

    function updateCartCount() {
      const countEl = document.getElementById("cart-count");
      if (countEl) {
        countEl.textContent = cart.reduce((sum, item) => sum + item.quantity, 0);
      }
    }

    function addToCart(id) {
      const item = productsData.find(p => p.id === parseInt(id));
      if (item) {
        const cartItem = cart.find(ci => ci.id === item.id);
        if (cartItem) {
          cartItem.quantity += 1;
        } else {
          cart.push({ ...item, quantity: 1 });
        }
        localStorage.setItem("cart", JSON.stringify(cart));
        updateCartCount();
      }
    }

    function renderProducts(products) {
      const productContainer = document.getElementById("productContainer");
      if (!productContainer) return;

      productContainer.innerHTML = "";
      products.forEach(product => {
        const card = document.createElement('div');
        card.className = `
          bg-white dark:bg-gray-800 
          text-gray-900 dark:text-gray-100 
          rounded-lg shadow-md 
          overflow-hidden 
          flex flex-col
          transition-transform transform hover:scale-105
        `;

        card.innerHTML = `
          <img src="${product.image}" alt="${product.name}" class="w-full h-48 object-cover" />
          <div class="p-4 flex flex-col flex-grow">
            <h3 class="text-lg font-semibold mb-2">${product.name}</h3>
            <p class="text-orange-500 font-bold text-xl mt-auto">${formatPrice(product.price)}</p>
            <button class="mt-4 bg-orange-500 text-white py-2 rounded hover:bg-orange-600 transition add-to-cart-btn" data-id="${product.id}">
              Add to Cart
            </button>
          </div>
        `;

        productContainer.appendChild(card);
      });

      document.querySelectorAll('.add-to-cart-btn').forEach(button => {
        button.addEventListener('click', e => {
          const productId = e.target.getAttribute('data-id');
          addToCart(productId);
        });
      });
    }

    function setupCategoryFilter() {
      const dropdown = document.getElementById("categorySelect");
      if (!dropdown) return;

      dropdown.addEventListener("change", () => {
        const category = dropdown.value;
        if (category === "All") {
          renderProducts(productsData);
        } else {
          const filtered = productsData.filter(p => p.category === category);
          renderProducts(filtered);
        }
      });
    }

    function setupAccountDropdown() {
      const btn = document.getElementById("accountDropdownBtn");
      const dropdown = document.getElementById("accountDropdown");
      if (!btn || !dropdown) return;

      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        dropdown.classList.toggle("hidden");
      });

      document.addEventListener("click", (e) => {
        if (!dropdown.classList.contains("hidden") && !dropdown.contains(e.target) && e.target !== btn) {
          dropdown.classList.add("hidden");
        }
      });
    }

    function searchProducts() {
      const queryInput = document.getElementById("searchInput");
      const query = queryInput?.value?.toLowerCase() || "";
      localStorage.setItem("searchQuery", query);
      const results = productsData.filter(p => p.name.toLowerCase().includes(query));
      renderProducts(results);
    }

    // Initial Load
    const savedQuery = localStorage.getItem("searchQuery");
    if (savedQuery) {
      const input = document.getElementById("searchInput");
      if (input) input.value = savedQuery;
      const results = productsData.filter(p => p.name.toLowerCase().includes(savedQuery));
      renderProducts(results);
    } else {
      renderProducts(productsData);
    }

    updateCartCount();
    setupAccountDropdown();
    setupCategoryFilter();

    const searchInput = document.getElementById("searchInput");
    if (searchInput) {
      searchInput.addEventListener("input", searchProducts);
    }
  });
