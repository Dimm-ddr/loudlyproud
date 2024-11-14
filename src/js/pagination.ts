import { PaginationConfig, PaginationElements, PaginationState } from '../types/pagination';

export class Pagination {
  private elements: {
    gallery: HTMLElement;
    itemsPerPageSelect: HTMLSelectElement;
    prevButton: HTMLElement;
    nextButton: HTMLElement;
    pageInfo: HTMLElement;
    noResults: HTMLElement;
    pagination: HTMLElement;
  };

  private config: {
    itemsPerPage: number;
    currentPage: number;
    totalItems: number;
  };

  constructor(elements: any, config: any) {
    this.elements = elements;
    this.config = config;

    this.initializeEventListeners();
    this.updateDisplay();
  }

  private initializeEventListeners() {
    // Items per page change
    this.elements.itemsPerPageSelect.addEventListener('change', () => {
      this.config.itemsPerPage = parseInt(this.elements.itemsPerPageSelect.value);
      this.config.currentPage = 1; // Reset to first page when changing items per page
      this.updateDisplay();
    });

    // Navigation buttons
    this.elements.prevButton.addEventListener('click', () => this.previousPage());
    this.elements.nextButton.addEventListener('click', () => this.nextPage());
  }

  private updateDisplay(): void {
    // Hide all books
    Array.from(this.elements.gallery.children).forEach(book =>
      (book as HTMLElement).style.display = 'none'
    );

    // Show books for current page
    const start = (this.config.currentPage - 1) * this.config.itemsPerPage;
    const end = start + this.config.itemsPerPage;
    Array.from(this.elements.gallery.children)
      .slice(start, end)
      .forEach(book => (book as HTMLElement).style.display = 'block');

    // Update page info
    const totalPages = Math.ceil(this.config.totalItems / this.config.itemsPerPage);
    this.elements.pageInfo.textContent = `Page ${this.config.currentPage} of ${totalPages}`;

    this.updateButtonStates(totalPages);
    this.toggleNoResults(totalPages);
  }

  private updateButtonStates(totalPages: number): void {
    // Previous button
    if (this.config.currentPage === 1) {
      this.elements.prevButton.classList.add('cursor-not-allowed', 'opacity-50');
      this.elements.prevButton.setAttribute('aria-disabled', 'true');
    } else {
      this.elements.prevButton.classList.remove('cursor-not-allowed', 'opacity-50');
      this.elements.prevButton.removeAttribute('aria-disabled');
    }

    // Next button
    if (this.config.currentPage === totalPages || totalPages === 0) {
      this.elements.nextButton.classList.add('cursor-not-allowed', 'opacity-50');
      this.elements.nextButton.setAttribute('aria-disabled', 'true');
    } else {
      this.elements.nextButton.classList.remove('cursor-not-allowed', 'opacity-50');
      this.elements.nextButton.removeAttribute('aria-disabled');
    }
  }

  private toggleNoResults(totalPages: number): void {
    if (totalPages === 0) {
      this.elements.noResults.classList.remove('hidden');
      this.elements.pagination.classList.add('hidden');
    } else {
      this.elements.noResults.classList.add('hidden');
      this.elements.pagination.classList.remove('hidden');
    }
  }

  private previousPage(): void {
    if (this.config.currentPage > 1) {
      this.config.currentPage--;
      this.updateDisplay();
    }
  }

  private nextPage(): void {
    const totalPages = Math.ceil(this.config.totalItems / this.config.itemsPerPage);
    if (this.config.currentPage < totalPages) {
      this.config.currentPage++;
      this.updateDisplay();
    }
  }
}