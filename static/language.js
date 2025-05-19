
document.addEventListener('DOMContentLoaded', () => {
  const htmlEl = document.documentElement;
  const darkModeToggle = document.getElementById('darkModeToggle');
  const language = localStorage.getItem('language') || 'en'; // default

  applyLanguage(language);

  function applyLanguage(lang) {
    const translations = {
      en: {
        cartTitle: "Your cart is empty!",
        cartSubtitle: "Browse our categories and discover our best deals!",
        startShopping: "Start Shopping",
        checkout: "Checkout",
        cartSummary: "Cart Summary",
        total: "Total",
        darkMode: "Dark Mode",
        lightMode: "Light Mode",
        account: "Account",
        orders: "Orders",
        wishlist: "Wish List",
        settings: "Account Settings",
        addresses: "Addresses",
        paymentMethods: "Payment Methods"
      },
      fr: {
        cartTitle: "Votre panier est vide !",
        cartSubtitle: "Parcourez nos catégories et découvrez nos meilleures offres !",
        startShopping: "Commencer vos achats",
        checkout: "Passer à la caisse",
        cartSummary: "Résumé du panier",
        total: "Total",
        darkMode: "Mode Sombre",
        lightMode: "Mode Clair",
        account: "Compte",
        orders: "Commandes",
        wishlist: "Liste de souhaits",
        settings: "Paramètres du compte",
        addresses: "Adresses",
        paymentMethods: "Méthodes de paiement"
      }
    };

    const t = translations[lang];
    if (!t) return;

    if (document.querySelector('#cartEmptyMessage h2')) {
      document.querySelector('#cartEmptyMessage h2').textContent = t.cartTitle;
      document.querySelector('#cartEmptyMessage p').textContent = t.cartSubtitle;
      document.querySelector('#cartEmptyMessage button').textContent = t.startShopping;
    }

    if (document.querySelector('#cartSummary h3')) {
      document.querySelector('#cartSummary h3').textContent = t.cartSummary;
      document.querySelector('#cartTotalPrice').previousElementSibling.textContent = t.total + ":";
      document.querySelector('.checkout-btn').textContent = t.checkout;
    }

    const accountBtn = document.querySelector('#accountBtn');
    if (accountBtn) {
      accountBtn.childNodes[1].nodeValue = ` ${t.account}`;
    }

    const dropdownItems = document.querySelectorAll('#accountDropdown a');
    if (dropdownItems.length >= 5) {
      dropdownItems[0].innerHTML = `<i class="fas fa-box mr-2"></i> ${t.orders}`;
      dropdownItems[1].innerHTML = `<i class="fas fa-heart mr-2"></i> ${t.wishlist}`;
      dropdownItems[2].innerHTML = `<i class="fas fa-cog mr-2"></i> ${t.settings}`;
      dropdownItems[3].innerHTML = `<i class="fas fa-map-marker-alt mr-2"></i> ${t.addresses}`;
      dropdownItems[4].innerHTML = `<i class="fas fa-credit-card mr-2"></i> ${t.paymentMethods}`;
    }

    // Update dark mode toggle label
    if (darkModeToggle) {
      const isDark = htmlEl.classList.contains('dark');
      darkModeToggle.innerHTML = isDark
        ? `<i class="fas fa-sun"></i> ${t.lightMode}`
        : `<i class="fas fa-moon"></i> ${t.darkMode}`;
    }
  }

  // If language selector exists (account.html), bind change event
  const langSelector = document.getElementById('languageSelector');
  if (langSelector) {
    langSelector.addEventListener('change', (e) => {
      const newLang = e.target.value;
      localStorage.setItem('language', newLang);
      applyLanguage(newLang);
    });
  }
});
