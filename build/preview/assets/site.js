// KiroCrew Cookbook: static preview behavior. No framework, no build step.
(function () {
  "use strict";

  // Clipboard with a fallback for iframes that block the async API.
  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text).catch(function () { return legacyCopy(text); });
    }
    return legacyCopy(text);
  }
  function legacyCopy(text) {
    return new Promise(function (resolve, reject) {
      var ta = document.createElement("textarea");
      ta.value = text;
      ta.setAttribute("readonly", "");
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand("copy") ? resolve() : reject(new Error("copy failed")); }
      catch (e) { reject(e); }
      finally { document.body.removeChild(ta); }
    });
  }
  function flash(btn, label) {
    var tip = btn.querySelector(".vc-copy__tip");
    if (tip) {
      tip.textContent = label;
      btn.classList.add("is-copied");
      setTimeout(function () { btn.classList.remove("is-copied"); tip.textContent = ""; }, 1600);
      return;
    }
    var span = btn.querySelector("[data-label]") || btn;
    var old = span.textContent;
    span.textContent = label;
    btn.setAttribute("aria-live", "polite");
    setTimeout(function () { span.textContent = old; }, 1600);
  }

  // Copy buttons on code blocks, prompts and the install snippet.
  document.querySelectorAll("[data-copy]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var host = btn.closest(".vc-code, .vc-prompt, .vc-snippet");
      var code = host && host.querySelector("code");
      if (!code) return;
      copyText(code.innerText.replace(/\n$/, "")).then(
        function () { flash(btn, "Copied"); },
        function () { flash(btn, "Press Ctrl+C"); }
      );
    });
  });

  // "Copy page" copies the page's Markdown source.
  document.querySelectorAll("[data-copy-page]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      fetch(btn.getAttribute("data-copy-page"))
        .then(function (r) { if (!r.ok) throw new Error(r.status); return r.text(); })
        .then(copyText)
        .then(function () { flash(btn, "Copied"); }, function () { flash(btn, "Copy failed"); });
    });
  });

  // Nav gets its bottom border only after scroll.
  var nav = document.querySelector(".vc-nav");
  if (nav) {
    var onScroll = function () { nav.classList.toggle("is-scrolled", window.scrollY > 4); };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  // Cmd/Ctrl+K or "/" jumps to recipe search.
  document.addEventListener("keydown", function (e) {
    var typing = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement && document.activeElement.tagName);
    if (((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") || (e.key === "/" && !typing)) {
      var input = document.getElementById("recipe-search");
      e.preventDefault();
      if (input) { input.focus(); input.select(); }
      else { var t = document.querySelector("[data-search-href]"); if (t) location.href = t.getAttribute("data-search-href"); }
    }
  });
  if (location.hash === "#search") {
    var si = document.getElementById("recipe-search");
    if (si) si.focus();
  }

  // Right TOC: mark the section currently in view.
  var tocLinks = Array.prototype.slice.call(document.querySelectorAll(".vc-toc a[href^='#']"));
  if (tocLinks.length && "IntersectionObserver" in window) {
    var byId = {};
    tocLinks.forEach(function (a) { byId[decodeURIComponent(a.hash.slice(1))] = a; });
    var visible = new Set();
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { en.isIntersecting ? visible.add(en.target.id) : visible.delete(en.target.id); });
      var first = tocLinks.find(function (a) { return visible.has(decodeURIComponent(a.hash.slice(1))); });
      if (first) {
        tocLinks.forEach(function (a) { a.classList.toggle("is-active", a === first); });
      }
    }, { rootMargin: "-72px 0px -60% 0px" });
    Object.keys(byId).forEach(function (id) { var h = document.getElementById(id); if (h) io.observe(h); });
  }

  // Recipe index filters: client-side over a JSON index built at build time.
  var dataEl = document.getElementById("recipe-index");
  if (dataEl) {
    var items = JSON.parse(dataEl.textContent);
    var grid = document.getElementById("recipe-grid");
    var empty = document.getElementById("recipe-empty");
    var count = document.getElementById("recipe-count");
    var input = document.getElementById("recipe-search");
    var state = { q: "", surface: "all", tags: new Set() };

    function apply() {
      var shown = 0;
      items.forEach(function (it) {
        var hay = (it.title + " " + it.description + " " + it.category + " " + it.tags.join(" ")).toLowerCase();
        var ok = (!state.q || hay.indexOf(state.q) !== -1)
          && (state.surface === "all" || it.surfaces.indexOf(state.surface) !== -1)
          && Array.from(state.tags).every(function (t) { return it.tags.indexOf(t) !== -1; });
        var card = document.getElementById("card-" + it.slug);
        card.hidden = !ok;
        if (ok) shown++;
      });
      empty.hidden = shown !== 0;
      grid.hidden = shown === 0;
      count.textContent = shown === items.length
        ? items.length + " recipes"
        : shown + " of " + items.length + " recipes";
    }

    input.addEventListener("input", function () { state.q = input.value.trim().toLowerCase(); apply(); });
    document.querySelectorAll("[data-surface]").forEach(function (b) {
      b.addEventListener("click", function () {
        state.surface = b.getAttribute("data-surface");
        document.querySelectorAll("[data-surface]").forEach(function (o) { o.setAttribute("aria-pressed", String(o === b)); });
        apply();
      });
    });
    document.querySelectorAll("[data-tag]").forEach(function (b) {
      b.addEventListener("click", function () {
        var t = b.getAttribute("data-tag");
        state.tags.has(t) ? state.tags.delete(t) : state.tags.add(t);
        b.setAttribute("aria-pressed", String(state.tags.has(t)));
        apply();
      });
    });
    document.getElementById("recipe-clear").addEventListener("click", function () {
      state = { q: "", surface: "all", tags: new Set() };
      input.value = "";
      document.querySelectorAll("[data-surface]").forEach(function (o) { o.setAttribute("aria-pressed", String(o.getAttribute("data-surface") === "all")); });
      document.querySelectorAll("[data-tag]").forEach(function (o) { o.setAttribute("aria-pressed", "false"); });
      apply();
      input.focus();
    });
    apply();
  }
})();
