/* Accessible Sphinx/MyST-NB figure enlargement: no third-party dependency.
 * Inline SVGs are serialized to isolated image URLs to avoid duplicate IDs.
 */
(() => {
  "use strict";

  const initialize = () => {
    const content = document.querySelector(".content");
    if (!content || typeof HTMLDialogElement === "undefined") return;

    const dialog = document.createElement("dialog");
    dialog.className = "te-zoom-dialog";
    dialog.setAttribute("aria-label", "Expanded scientific figure");
    dialog.innerHTML = [
      '<div class="te-zoom-toolbar">',
      '  <span class="te-zoom-caption">Figure</span>',
      '  <div class="te-zoom-actions">',
      '    <button type="button" data-action="out" aria-label="Zoom out">−</button>',
      '    <output class="te-zoom-level" aria-live="polite">100%</output>',
      '    <button type="button" data-action="in" aria-label="Zoom in">+</button>',
      '    <button type="button" data-action="reset" aria-label="Reset zoom">Reset</button>',
      '    <button type="button" data-action="close" aria-label="Close enlarged figure">Close</button>',
      '  </div>',
      '</div>',
      '<div class="te-zoom-viewport" tabindex="0" aria-label="Scrollable enlarged figure">',
      '  <div class="te-zoom-stage"></div>',
      '</div>',
    ].join("");
    document.body.appendChild(dialog);

    const caption = dialog.querySelector(".te-zoom-caption");
    const stage = dialog.querySelector(".te-zoom-stage");
    const level = dialog.querySelector(".te-zoom-level");
    const viewport = dialog.querySelector(".te-zoom-viewport");
    let zoom = 1;
    let sourceFocus = null;
    let temporaryUrl = null;

    const updateZoom = () => {
      stage.style.width = Math.round(zoom * 100) + "%";
      level.textContent = Math.round(zoom * 100) + "%";
    };

    const close = () => {
      if (dialog.open) dialog.close();
    };

    const labelFor = (source) => {
      const figure = source.closest("figure, .figure");
      const description = figure?.querySelector("figcaption, .caption");
      return (
        source.getAttribute("alt") ||
        source.getAttribute("aria-label") ||
        source.querySelector?.("title")?.textContent ||
        description?.textContent?.trim() ||
        "Scientific figure"
      ).trim();
    };

    const open = (source, opener) => {
      if (dialog.open) close();
      if (temporaryUrl) {
        URL.revokeObjectURL(temporaryUrl);
        temporaryUrl = null;
      }
      stage.replaceChildren();
      const description = labelFor(source);
      const image = document.createElement("img");
      image.className = "te-zoom-media";
      image.alt = description;
      if (source instanceof SVGElement) {
        const xml = new XMLSerializer().serializeToString(source);
        temporaryUrl = URL.createObjectURL(
          new Blob([xml], { type: "image/svg+xml;charset=utf-8" })
        );
        image.src = temporaryUrl;
      } else {
        image.src = source.currentSrc || source.src;
      }
      stage.appendChild(image);
      caption.textContent = description;
      sourceFocus = opener;
      zoom = 1;
      updateZoom();
      dialog.showModal();
      viewport.scrollTo(0, 0);
      dialog.querySelector('[data-action="close"]').focus();
    };

    dialog.addEventListener("click", (event) => {
      const button = event.target.closest("button[data-action]");
      if (button) {
        switch (button.dataset.action) {
          case "in":
            zoom = Math.min(4, zoom + 0.25);
            updateZoom();
            break;
          case "out":
            zoom = Math.max(0.75, zoom - 0.25);
            updateZoom();
            break;
          case "reset":
            zoom = 1;
            updateZoom();
            viewport.scrollTo(0, 0);
            break;
          case "close":
            close();
            break;
          default:
            break;
        }
      } else if (event.target === dialog) {
        close();
      }
    });
    dialog.addEventListener("keydown", (event) => {
      if (event.target instanceof HTMLButtonElement) return;
      if (event.key === "+" || event.key === "=") {
        event.preventDefault();
        zoom = Math.min(4, zoom + 0.25);
        updateZoom();
      } else if (event.key === "-") {
        event.preventDefault();
        zoom = Math.max(0.75, zoom - 0.25);
        updateZoom();
      } else if (event.key === "0") {
        event.preventDefault();
        zoom = 1;
        updateZoom();
      }
    });
    dialog.addEventListener("close", () => {
      stage.replaceChildren();
      if (temporaryUrl) URL.revokeObjectURL(temporaryUrl);
      temporaryUrl = null;
      sourceFocus?.focus();
      sourceFocus = null;
    });

    const selectors = [
      "img[src]",
      ".cell_output svg",
      ".nboutput svg",
      ".output_area svg",
      "figure svg",
      ".figure svg",
    ];
    content.querySelectorAll(selectors.join(", ")).forEach((source) => {
      if (source.closest(".te-landing, .te-zoom-frame, button")) return;
      // Other linked figures keep their pre-existing navigation actions.
      const anchor = source.closest("a");
      if (anchor && !anchor.classList.contains("image-reference")) return;

      const display = anchor || source;
      const frame = document.createElement("span");
      frame.className = "te-zoom-frame";
      display.before(frame);
      frame.appendChild(display);

      const button = document.createElement("button");
      button.type = "button";
      button.className = "te-zoom-trigger";
      button.textContent = "Expand";
      button.setAttribute("aria-label", "Enlarge: " + labelFor(source));
      frame.appendChild(button);
      button.addEventListener("click", () => open(source, button));

      source.classList.add("te-zoomable-media");
      if (anchor) {
        anchor.addEventListener("click", (event) => {
          if (event.ctrlKey || event.metaKey) return;
          event.preventDefault();
          open(source, anchor);
        });
      } else {
        source.tabIndex = 0;
        source.setAttribute("role", "button");
        source.setAttribute("aria-label", "Enlarge: " + labelFor(source));
        source.addEventListener("click", () => open(source, source));
        source.addEventListener("keydown", (event) => {
          if (event.key !== "Enter" && event.key !== " ") return;
          event.preventDefault();
          open(source, source);
        });
      }
    });
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize, { once: true });
  } else {
    initialize();
  }
})();