// Application Client-Side UI Scripts

// Get current year for footer
document.addEventListener("DOMContentLoaded", () => {
  const year = document.getElementById("year");
  if (year) {
    year.textContent = new Date().getFullYear();
  }
});

// Clipboard Helper
document.addEventListener("DOMContentLoaded", () => {
  const copyInput = document.getElementById("copy-input");
  if (copyInput) {
    const copyButton = document.getElementById("copy-button");
    const copyText = document.getElementById("copy-text");
    const websiteInput = document.getElementById("website-input");

    if (copyButton && websiteInput) {
      copyButton.addEventListener("click", () => {
        navigator.clipboard.writeText(websiteInput.value).then(() => {
          if (copyText) copyText.textContent = "Copied";
          setTimeout(() => {
            if (copyText) copyText.textContent = "Copy";
          }, 2000);
        });
      });
    }
  }
});

// Search Bar Shortcuts (Ctrl+K or Cmd+K)
document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.getElementById("search-input");
  const searchButton = document.getElementById("search-button");

  function focusSearchInput() {
    if (searchInput) searchInput.focus();
  }

  if (searchButton && searchInput) {
    searchButton.addEventListener("click", focusSearchInput);
  }

  if (searchInput) {
    document.addEventListener("keydown", function (event) {
      if ((event.metaKey || event.ctrlKey) && event.key === "k") {
        event.preventDefault();
        focusSearchInput();
      }
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "/" && document.activeElement !== searchInput) {
        event.preventDefault();
        focusSearchInput();
      }
    });
  }
});
