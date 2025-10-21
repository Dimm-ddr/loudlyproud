export class Sorting {
  private elements: {
    gallery: HTMLElement;
    sortSelect: HTMLSelectElement;
  };

  private config: {
    currentSort: 'title_asc' | 'title_desc' | 'author_asc' | 'author_desc' | 'year_asc' | 'year_desc';
    onSort?: () => void;
  };

  private bookElements: { element: HTMLElement; title: string; author: string; year: number; }[] = [];

  constructor(config: { selectors: { gallery: string; sortSelect: string; }; onSort?: () => void; }) {
    const elements = {
      gallery: document.querySelector(config.selectors.gallery),
      sortSelect: document.querySelector(config.selectors.sortSelect),
    };

    Object.entries(elements).forEach(([key, element]) => {
      if (!element) {
        throw new Error(`Required element "${key}" not found using selector "${(config.selectors as any)[key]}"`);
      }
    });

    this.elements = elements as { gallery: HTMLElement; sortSelect: HTMLSelectElement; };
    this.config = { currentSort: this.elements.sortSelect.value as any, onSort: config.onSort };

    this.initializeBookElements();
    this.initializeEventListeners();
    this.applySort(this.config.currentSort);
  }

  private initializeBookElements(): void {
    this.bookElements = Array.from(this.elements.gallery.children).map((bookElement) => {
      const element = bookElement as HTMLElement;
      const title = (element.querySelector('.book-card h2 a')?.textContent) || '';
      const author = (element.querySelector('.book-authors')?.textContent) || '';
      let year = 0;
      const yearElement = element.querySelector('[data-publication-year]');
      if (yearElement) {
        const yearText = yearElement.getAttribute('data-publication-year');
        year = yearText ? parseInt(yearText, 10) : 0;
      }
      return { element, title, author, year };
    });
  }

  private initializeEventListeners(): void {
    this.elements.sortSelect.addEventListener('change', () => {
      const selectedSort = this.elements.sortSelect.value as typeof this.config.currentSort;
      this.applySort(selectedSort);
      if (this.config.onSort) this.config.onSort();
    });
  }

  private applySort(sortOption: typeof this.config.currentSort): void {
    this.config.currentSort = sortOption;
    const sortedElements = [...this.bookElements].sort((a, b) => {
      switch (sortOption) {
        case 'title_asc': return a.title.localeCompare(b.title);
        case 'title_desc': return b.title.localeCompare(a.title);
        case 'author_asc': return a.author.localeCompare(b.author);
        case 'author_desc': return b.author.localeCompare(a.author);
        case 'year_asc': return a.year - b.year;
        case 'year_desc': return b.year - a.year;
        default: return 0;
      }
    });
    while (this.elements.gallery.firstChild) this.elements.gallery.removeChild(this.elements.gallery.firstChild);
    sortedElements.forEach(item => this.elements.gallery.appendChild(item.element));
  }
}


