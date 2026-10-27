/* Thunder Apps Studio — site.js
   Small, dependency-free behaviour for every page:
   nav menu + dropdown, frosted nav border, shelf arrows, stat counters,
   back-to-top. */
(function () {
    "use strict";

    var nav = document.querySelector(".nav");

    // ---- Mobile menu ----
    var toggle = document.querySelector(".nav-toggle");
    if (nav && toggle) {
        toggle.addEventListener("click", function () {
            var open = nav.classList.toggle("is-open");
            toggle.setAttribute("aria-expanded", String(open));
        });
    }

    // ---- "Pages" dropdown ----
    var dropdowns = document.querySelectorAll(".nav-dropdown");
    dropdowns.forEach(function (dd) {
        var button = dd.querySelector("button");
        button.addEventListener("click", function (event) {
            event.stopPropagation();
            var open = !dd.classList.contains("is-open");
            closeDropdowns();
            dd.classList.toggle("is-open", open);
            button.setAttribute("aria-expanded", String(open));
        });
    });
    function closeDropdowns() {
        dropdowns.forEach(function (dd) {
            dd.classList.remove("is-open");
            dd.querySelector("button").setAttribute("aria-expanded", "false");
        });
    }
    document.addEventListener("click", function (event) {
        if (!event.target.closest(".nav-dropdown")) closeDropdowns();
    });
    document.addEventListener("keydown", function (event) {
        if (event.key !== "Escape") return;
        closeDropdowns();
        if (nav && nav.classList.contains("is-open")) {
            nav.classList.remove("is-open");
            toggle.setAttribute("aria-expanded", "false");
            toggle.focus();
        }
    });

    // ---- Nav hairline + back-to-top, driven by scroll position ----
    var toTop = document.querySelector(".to-top");
    function onScroll() {
        var y = window.scrollY;
        if (nav) nav.classList.toggle("is-scrolled", y > 4);
        if (toTop) toTop.classList.toggle("is-visible", y > 300);
    }
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
    if (toTop) {
        toTop.addEventListener("click", function () {
            window.scrollTo({ top: 0, behavior: "smooth" });
        });
    }

    // ---- Shelves: prev / next buttons scroll one page ----
    document.querySelectorAll("[data-shelf]").forEach(function (shelf) {
        var id = shelf.id;
        var prev = document.querySelector('[data-shelf-prev="' + id + '"]');
        var next = document.querySelector('[data-shelf-next="' + id + '"]');
        if (!prev || !next) return;

        function update() {
            var max = shelf.scrollWidth - shelf.clientWidth - 2;
            prev.disabled = shelf.scrollLeft <= 2;
            next.disabled = shelf.scrollLeft >= max;
            var hidden = max <= 0;
            prev.parentNode.hidden = hidden;
        }
        function page(direction) {
            shelf.scrollBy({ left: direction * shelf.clientWidth * 0.9, behavior: "smooth" });
        }
        prev.addEventListener("click", function () { page(-1); });
        next.addEventListener("click", function () { page(1); });
        shelf.addEventListener("scroll", update, { passive: true });
        window.addEventListener("resize", update);
        update();
    });

    // ---- Stat counters count up once, when they come into view ----
    var counters = document.querySelectorAll("[data-count]");
    var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    function format(n) { return Math.round(n).toLocaleString("en-US"); }
    function run(el) {
        var target = parseFloat(el.getAttribute("data-count"));
        if (reduceMotion) { el.textContent = format(target); return; }
        var start = null;
        var duration = 1400;
        function frame(t) {
            if (start === null) start = t;
            var p = Math.min((t - start) / duration, 1);
            var eased = 1 - Math.pow(1 - p, 3);
            el.textContent = format(target * eased);
            if (p < 1) requestAnimationFrame(frame);
        }
        requestAnimationFrame(frame);
    }
    if (counters.length) {
        if ("IntersectionObserver" in window) {
            var io = new IntersectionObserver(function (entries) {
                entries.forEach(function (entry) {
                    if (!entry.isIntersecting) return;
                    io.unobserve(entry.target);
                    run(entry.target);
                });
            }, { threshold: 0.4 });
            counters.forEach(function (el) { io.observe(el); });
        } else {
            counters.forEach(run);
        }
    }
})();
