// src/js/pagination.ts
var Pagination = class {
  constructor(config) {
    const elements = {
      gallery: document.querySelector(config.selectors.gallery),
      itemsPerPageSelect: document.querySelector(
        config.selectors.itemsPerPageSelect
      ),
      prevButton: document.querySelector(config.selectors.prevButton),
      nextButton: document.querySelector(config.selectors.nextButton),
      pageInfo: document.querySelector(config.selectors.pageInfo),
      noResults: document.querySelector(config.selectors.noResults),
      pagination: document.querySelector(config.selectors.pagination)
    };
    Object.entries(elements).forEach(([key, element]) => {
      if (!element) {
        throw new Error(
          `Required element "${key}" not found using selector "${config.selectors[key]}"`
        );
      }
    });
    this.elements = elements;
    this.config = {
      itemsPerPage: config.itemsPerPage || parseInt(this.elements.itemsPerPageSelect.value),
      currentPage: config.currentPage || 1,
      totalItems: config.totalItems || this.elements.gallery.children.length
    };
    this.initializeEventListeners();
    this.updateDisplay();
  }
  initializeEventListeners() {
    this.elements.itemsPerPageSelect.addEventListener("change", () => {
      this.config.itemsPerPage = parseInt(
        this.elements.itemsPerPageSelect.value
      );
      this.config.currentPage = 1;
      this.updateDisplay();
    });
    this.elements.prevButton.addEventListener(
      "click",
      () => this.previousPage()
    );
    this.elements.nextButton.addEventListener("click", () => this.nextPage());
  }
  updateDisplay() {
    Array.from(this.elements.gallery.children).forEach(
      (book) => book.style.display = "none"
    );
    const start = (this.config.currentPage - 1) * this.config.itemsPerPage + 1;
    const end = Math.min(
      this.config.currentPage * this.config.itemsPerPage,
      this.config.totalItems
    );
    Array.from(this.elements.gallery.children).slice(start - 1, end).forEach((book) => book.style.display = "block");
    this.elements.pageInfo.textContent = `${start}-${end} of ${this.config.totalItems}`;
    const totalPages = Math.ceil(
      this.config.totalItems / this.config.itemsPerPage
    );
    this.updateButtonStates(totalPages);
    this.toggleNoResults(totalPages);
  }
  updateButtonStates(totalPages) {
    if (this.config.currentPage === 1) {
      this.elements.prevButton.classList.add(
        "cursor-not-allowed",
        "opacity-50"
      );
      this.elements.prevButton.setAttribute("aria-disabled", "true");
    } else {
      this.elements.prevButton.classList.remove(
        "cursor-not-allowed",
        "opacity-50"
      );
      this.elements.prevButton.removeAttribute("aria-disabled");
    }
    if (this.config.currentPage === totalPages || totalPages === 0) {
      this.elements.nextButton.classList.add(
        "cursor-not-allowed",
        "opacity-50"
      );
      this.elements.nextButton.setAttribute("aria-disabled", "true");
    } else {
      this.elements.nextButton.classList.remove(
        "cursor-not-allowed",
        "opacity-50"
      );
      this.elements.nextButton.removeAttribute("aria-disabled");
    }
  }
  toggleNoResults(totalPages) {
    if (totalPages === 0) {
      this.elements.noResults.classList.remove("hidden");
      this.elements.pagination.classList.add("hidden");
    } else {
      this.elements.noResults.classList.add("hidden");
      this.elements.pagination.classList.remove("hidden");
    }
  }
  previousPage() {
    if (this.config.currentPage > 1) {
      this.config.currentPage--;
      this.updateDisplay();
    }
  }
  nextPage() {
    const totalPages = Math.ceil(
      this.config.totalItems / this.config.itemsPerPage
    );
    if (this.config.currentPage < totalPages) {
      this.config.currentPage++;
      this.updateDisplay();
    }
  }
};
export {
  Pagination
};
//# sourceMappingURL=pagination.js.map
