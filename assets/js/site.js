(function () {
  // Mobile navigation
  var toggle = document.querySelector('[data-nav-toggle]');
  var nav = document.querySelector('[data-nav]');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open);
      toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    });
  }

  // Product category filter
  var productGroup = document.querySelector('[data-filter-group="products"]');
  var productGrid = document.querySelector('[data-filter-target="products"]');
  if (productGroup && productGrid) {
    productGroup.addEventListener('click', function (e) {
      var btn = e.target.closest('[data-filter]');
      if (!btn) return;
      setActive(productGroup, btn);
      var f = btn.dataset.filter;
      productGrid.querySelectorAll('[data-cat]').forEach(function (el) {
        el.hidden = f !== 'all' && el.dataset.cat !== f;
      });
    });
  }

  // Publication search + type filter
  var list = document.querySelector('[data-pub-list]');
  if (list) {
    var input = document.querySelector('[data-pub-search]');
    var group = document.querySelector('[data-filter-group="pubs"]');
    var empty = document.querySelector('[data-pub-empty]');
    var type = 'all';
    var apply = function () {
      var q = (input.value || '').trim().toLowerCase();
      var shown = 0;
      list.querySelectorAll('.pub').forEach(function (el) {
        var ok = (type === 'all' || el.dataset.type === type) && (!q || el.dataset.search.indexOf(q) !== -1);
        el.hidden = !ok;
        if (ok) shown++;
      });
      empty.hidden = shown !== 0;
    };
    input.addEventListener('input', apply);
    group.addEventListener('click', function (e) {
      var btn = e.target.closest('[data-filter]');
      if (!btn) return;
      setActive(group, btn);
      type = btn.dataset.filter;
      apply();
    });
  }

  // Prefill the inquiry email with the product name (from ?product=...)
  var inquiry = document.querySelector('[data-inquiry-link]');
  var product = new URLSearchParams(location.search).get('product');
  if (inquiry && product) {
    inquiry.href = inquiry.href
      .replace('subject=Product%20inquiry', 'subject=' + encodeURIComponent('Inquiry: ' + product))
      .replace('Product%3A', 'Product%3A%20' + encodeURIComponent(product));
  }

  function setActive(group, btn) {
    group.querySelectorAll('[data-filter]').forEach(function (b) { b.classList.toggle('is-active', b === btn); });
  }
})();
