(() => {
  const root = document.documentElement;
  const params = new URLSearchParams(location.search);

  if (params.get("shot") === "1") {
    root.classList.add("shot");
  }

  const page = root.dataset.page || "";
  document.querySelectorAll("[data-nav]").forEach((link) => {
    if (link.dataset.nav === page) {
      link.setAttribute("aria-current", "page");
    }
  });

  document.querySelectorAll("[data-copy-url]").forEach((button) => {
    button.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(location.href);
        const original = button.textContent;
        button.textContent = "Ссылка скопирована";
        setTimeout(() => (button.textContent = original), 1400);
      } catch (_) {}
    });
  });
})();
