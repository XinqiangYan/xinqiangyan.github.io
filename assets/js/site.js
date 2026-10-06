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

  // Publication search + type filter + pagination
  var list = document.querySelector('[data-pub-list]');
  if (list) {
    var input = document.querySelector('[data-pub-search]');
    var group = document.querySelector('[data-filter-group="pubs"]');
    var empty = document.querySelector('[data-pub-empty]');
    var pager = document.querySelector('[data-pub-pager]');
    var count = document.querySelector('[data-pub-count]');
    var items = Array.prototype.slice.call(list.querySelectorAll('.pub'));
    var perPage = parseInt(list.dataset.perPage, 10) || 20;
    var type = 'all';
    var page = 1;

    var render = function (scroll) {
      var q = (input.value || '').trim().toLowerCase();
      var matches = items.filter(function (el) {
        return (type === 'all' || el.dataset.type === type) && (!q || el.dataset.search.indexOf(q) !== -1);
      });
      var pages = Math.max(1, Math.ceil(matches.length / perPage));
      page = Math.min(Math.max(1, page), pages);
      var from = (page - 1) * perPage, to = from + perPage;
      items.forEach(function (el) { el.hidden = true; });
      matches.slice(from, to).forEach(function (el) { el.hidden = false; });
      empty.hidden = matches.length !== 0;
      count.textContent = matches.length
        ? 'Showing ' + (from + 1) + '–' + Math.min(to, matches.length) + ' of ' + matches.length
        : '';

      pager.innerHTML = '';
      if (pages > 1) {
        var add = function (label, target, opts) {
          var b = document.createElement('button');
          b.type = 'button';
          b.className = 'chip' + (opts && opts.active ? ' is-active' : '');
          b.textContent = label;
          if (opts && opts.aria) b.setAttribute('aria-label', opts.aria);
          if (opts && opts.active) b.setAttribute('aria-current', 'page');
          b.disabled = target < 1 || target > pages;
          b.addEventListener('click', function () { page = target; render(true); });
          pager.appendChild(b);
        };
        add('←', page - 1, { aria: 'Previous page' });
        for (var i = 1; i <= pages; i++) {
          if (i === 1 || i === pages || Math.abs(i - page) <= 2) add(String(i), i, { active: i === page });
          else if (Math.abs(i - page) === 3) { var s = document.createElement('span'); s.textContent = '…'; s.className = 'muted'; pager.appendChild(s); }
        }
        add('→', page + 1, { aria: 'Next page' });
      }
      if (scroll) count.scrollIntoView({ behavior: 'smooth', block: 'center' });
    };

    input.addEventListener('input', function () { page = 1; render(); });
    group.addEventListener('click', function (e) {
      var btn = e.target.closest('[data-filter]');
      if (!btn) return;
      setActive(group, btn);
      type = btn.dataset.filter;
      page = 1;
      render();
    });
    render();
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
