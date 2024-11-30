// src/js/pagination.ts
var Pagination = class {
  constructor(elements, config) {
    this.elements = elements;
    this.config = config;
    this.initializeEventListeners();
    this.updateDisplay();
  }
  initializeEventListeners() {
    this.elements.itemsPerPageSelect.addEventListener("change", () => {
      this.config.itemsPerPage = parseInt(this.elements.itemsPerPageSelect.value);
      this.config.currentPage = 1;
      this.updateDisplay();
    });
    this.elements.prevButton.addEventListener("click", () => this.previousPage());
    this.elements.nextButton.addEventListener("click", () => this.nextPage());
  }
  updateDisplay() {
    Array.from(this.elements.gallery.children).forEach(
      (book) => book.style.display = "none"
    );
    const start = (this.config.currentPage - 1) * this.config.itemsPerPage;
    const end = start + this.config.itemsPerPage;
    Array.from(this.elements.gallery.children).slice(start, end).forEach((book) => book.style.display = "block");
    const totalPages = Math.ceil(this.config.totalItems / this.config.itemsPerPage);
    this.elements.pageInfo.textContent = `Page ${this.config.currentPage} of ${totalPages}`;
    this.updateButtonStates(totalPages);
    this.toggleNoResults(totalPages);
  }
  updateButtonStates(totalPages) {
    if (this.config.currentPage === 1) {
      this.elements.prevButton.classList.add("cursor-not-allowed", "opacity-50");
      this.elements.prevButton.setAttribute("aria-disabled", "true");
    } else {
      this.elements.prevButton.classList.remove("cursor-not-allowed", "opacity-50");
      this.elements.prevButton.removeAttribute("aria-disabled");
    }
    if (this.config.currentPage === totalPages || totalPages === 0) {
      this.elements.nextButton.classList.add("cursor-not-allowed", "opacity-50");
      this.elements.nextButton.setAttribute("aria-disabled", "true");
    } else {
      this.elements.nextButton.classList.remove("cursor-not-allowed", "opacity-50");
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
    const totalPages = Math.ceil(this.config.totalItems / this.config.itemsPerPage);
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
