/* Progressive, one-time scroll reveals. Never change page content or navigation. */
(() => {
  "use strict";

  const initialize = () => {
    const root = document.documentElement;
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
    if (reducedMotion.matches || !("IntersectionObserver" in window)) return;

    // Main scientific content and the homepage; exclude sidebar/TOC and
    // navigation controls to keep documents usable throughout scrolling.
    const selectors = [
      ".te-section-heading",
      ".te-feature",
      ".te-demo",
      ".te-footer-panel",
      ".te-chart-panel",
      ".content article .admonition",
      ".content article .cell",
      ".content article .sd-card",
      ".content article > section > section"
    ];

    const elements = [...document.querySelectorAll(selectors.join(","))];
    if (!elements.length) return;

    const observer = new IntersectionObserver((entries, activeObserver) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        entry.target.classList.add("te-visible");
        activeObserver.unobserve(entry.target);
      }
    }, { threshold: 0.08, rootMargin: "0px 0px -4% 0px" });

    elements.forEach(element => {
      element.classList.add("te-reveal");
      // Never conceal initial-viewport content while observers initialize.
      if (element.getBoundingClientRect().top < window.innerHeight * 0.88) {
        element.classList.add("te-visible");
      }
      observer.observe(element);
    });
    root.dataset.teRevealReady = "true";

    reducedMotion.addEventListener?.("change", event => {
      if (event.matches) {
        root.removeAttribute("data-te-reveal-ready");
        observer.disconnect();
      }
    });
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize, { once: true });
  } else {
    initialize();
  }
})();
