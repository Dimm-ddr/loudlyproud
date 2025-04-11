// src/js/sorting.ts
var Sorting = class {
  constructor(config) {
    this.bookElements = [];
    const elements = {
      gallery: document.querySelector(config.selectors.gallery),
      sortSelect: document.querySelector(config.selectors.sortSelect)
    };
    Object.entries(elements).forEach(([key, element]) => {
      if (!element) {
        const isValidKey = (k) => k in config.selectors;
        if (isValidKey(key)) {
          throw new Error(
            `Required element "${key}" not found using selector "${config.selectors[key]}"`
          );
        } else {
          throw new Error(`Required element "${key}" not found with unknown selector`);
        }
      }
    });
    this.elements = elements;
    this.config = {
      currentSort: this.elements.sortSelect.value,
      onSort: config.onSort
    };
    this.initializeBookElements();
    this.initializeEventListeners();
    this.applySort(this.config.currentSort);
  }
  initializeBookElements() {
    this.bookElements = Array.from(this.elements.gallery.children).map((bookElement) => {
      const element = bookElement;
      const titleElement = element.querySelector(".book-card h2 a");
      const title = titleElement ? titleElement.textContent || "" : "";
      const authorElement = element.querySelector(".book-authors");
      const author = authorElement ? authorElement.textContent || "" : "";
      let year = 0;
      const yearElement = element.querySelector("[data-publication-year]");
      if (yearElement) {
        const yearText = yearElement.getAttribute("data-publication-year");
        year = yearText ? parseInt(yearText, 10) : 0;
      }
      return { element, title, author, year };
    });
  }
  initializeEventListeners() {
    this.elements.sortSelect.addEventListener("change", () => {
      const selectedSort = this.elements.sortSelect.value;
      this.applySort(selectedSort);
      if (this.config.onSort) {
        this.config.onSort();
      }
    });
  }
  applySort(sortOption) {
    this.config.currentSort = sortOption;
    const sortedElements = [...this.bookElements].sort((a, b) => {
      switch (sortOption) {
        case "title_asc":
          return a.title.localeCompare(b.title);
        case "title_desc":
          return b.title.localeCompare(a.title);
        case "author_asc":
          return a.author.localeCompare(b.author);
        case "author_desc":
          return b.author.localeCompare(a.author);
        case "year_asc":
          return a.year - b.year;
        case "year_desc":
          return b.year - a.year;
        default:
          return 0;
      }
    });
    while (this.elements.gallery.firstChild) {
      this.elements.gallery.removeChild(this.elements.gallery.firstChild);
    }
    sortedElements.forEach((item) => {
      this.elements.gallery.appendChild(item.element);
    });
  }
};
export {
  Sorting
};
//# sourceMappingURL=sorting.js.map
