/* Progressive animation of Furo's native checkbox-based navigation tree.
 * The checkbox and label remain the source of truth. Without JS/WAAPI, Furo's
 * original CSS display toggling stays intact. Nothing is hidden on page load.
 */
(() => {
  "use strict";

  const DURATION = 680;
  const EASING = "cubic-bezier(0.22, 1, 0.36, 1)";

  function init() {
    const tree = document.querySelector(".sidebar-tree");
    if (!tree) return;

    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
    const groups = tree.querySelectorAll("li.has-children");
    const active = new WeakMap();

    groups.forEach((group) => {
      const checkbox = group.querySelector(":scope > input.toctree-checkbox");
      const label = group.querySelector(":scope > label");
      const subtree = group.querySelector(":scope > ul");
      if (!checkbox || !label || !subtree) return;

      // Preserve the original Furo checkbox/label click behavior, while making
      // its expander separately keyboard operable and descriptively named.
      label.tabIndex = 0;
      label.setAttribute("role", "button");
      label.setAttribute(
        "aria-label",
        checkbox.getAttribute("aria-label") || "Toggle section"
      );
      const updateExpanded = () => {
        label.setAttribute("aria-expanded", String(checkbox.checked));
      };
      updateExpanded();

      label.addEventListener("keydown", (event) => {
        if (event.key !== "Enter" && event.key !== " ") return;
        event.preventDefault();
        checkbox.click();
      });

      checkbox.addEventListener("change", () => {
        updateExpanded();
        if (reduced.matches || typeof subtree.animate !== "function") return;

        const previous = active.get(group);
        const currentHeight = previous
          ? subtree.getBoundingClientRect().height
          : null;
        const currentOpacity = previous
          ? parseFloat(getComputedStyle(subtree).opacity)
          : 1;

        if (previous) {
          active.delete(group);
          previous.cancel();
        }

        // Furo immediately applies display:none for closed groups. Override
        // only during this animation, so the closing subtree can be measured.
        group.classList.add("te-nav-animating");
        const fullHeight = subtree.scrollHeight;
        const from = currentHeight === null
          ? (checkbox.checked ? 0 : fullHeight)
          : currentHeight;
        const to = checkbox.checked ? fullHeight : 0;

        subtree.style.overflow = "hidden";
        const animation = subtree.animate(
          [
            { height: `${from}px`, opacity: String(
                currentHeight === null ? (checkbox.checked ? 0 : 1) : currentOpacity
              ) },
            { height: `${to}px`, opacity: checkbox.checked ? "1" : "0" }
          ],
          { duration: DURATION, easing: EASING, fill: "both" }
        );
        active.set(group, animation);

        const cleanup = () => {
          if (active.get(group) !== animation) return;
          active.delete(group);
          group.classList.remove("te-nav-animating");
          subtree.style.overflow = "";
        };
        animation.onfinish = cleanup;
        animation.oncancel = cleanup;
      });
    });

    reduced.addEventListener?.("change", (event) => {
      if (!event.matches) return;
      // Animations stop at once if reduced motion is selected mid-session.
      groups.forEach((group) => {
        const running = active.get(group);
        if (!running) return;
        active.delete(group);
        running.cancel();
        group.classList.remove("te-nav-animating");
        const ul = group.querySelector(":scope > ul");
        if (ul) ul.style.overflow = "";
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();
