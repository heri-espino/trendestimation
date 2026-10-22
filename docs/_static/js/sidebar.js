/* Gentle sidebar expand/collapse without replacing Furo navigation.
 * Furo owns checkbox states, tree semantics, URLs and browser history.
 */
(() => {
  "use strict";

  const setup = () => {
    const sidebar = document.querySelector(".sidebar-tree");
    if (!sidebar || !Element.prototype.animate) return;

    const preference = window.matchMedia("(prefers-reduced-motion: reduce)");
    const running = new WeakMap();

    const reset = (submenu) => {
      submenu.style.removeProperty("display");
      submenu.style.removeProperty("height");
      submenu.style.removeProperty("overflow");
      submenu.style.removeProperty("opacity");
    };

    sidebar.addEventListener("change", (event) => {
      const input = event.target;
      if (!(input instanceof HTMLInputElement) ||
          !input.classList.contains("toctree-checkbox")) return;

      const parent = input.closest("li.has-children");
      const submenu = Array.from(parent?.children || []).find(
        (child) => child.tagName === "UL"
      );
      if (!submenu) return;

      running.get(submenu)?.cancel();
      reset(submenu);
      if (preference.matches) return;

      const expanding = input.checked;
      // When unchecked, Furo immediately applies display:none. Restore
      // display temporarily so its actual natural height can be measured.
      submenu.style.display = "block";
      const naturalHeight = submenu.scrollHeight;
      if (!naturalHeight) {
        reset(submenu);
        return;
      }
      submenu.style.overflow = "hidden";

      const animation = submenu.animate(
        expanding
          ? [
              { height: "0px", opacity: 0 },
              { height: `${naturalHeight}px`, opacity: 1 }
            ]
          : [
              { height: `${naturalHeight}px`, opacity: 1 },
              { height: "0px", opacity: 0 }
            ],
        {
          duration: 560,
          easing: "cubic-bezier(0.22, 1, 0.36, 1)"
        }
      );
      running.set(submenu, animation);
      const finish = () => {
        if (running.get(submenu) !== animation) return;
        running.delete(submenu);
        reset(submenu);
      };
      animation.addEventListener("finish", finish, { once: true });
      animation.addEventListener("cancel", finish, { once: true });
    });

    preference.addEventListener?.("change", (event) => {
      if (!event.matches) return;
      sidebar.querySelectorAll("li.has-children > ul").forEach((submenu) => {
        running.get(submenu)?.cancel();
        reset(submenu);
      });
    });
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", setup, { once: true });
  } else {
    setup();
  }
})();
