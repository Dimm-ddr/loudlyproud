import { PaginationConfig, PaginationElements, PaginationState } from '../types/pagination';

export class Pagination {
  private elements: PaginationElements;
  private state: PaginationState;
  private books: HTMLElement[];

  constructor(elements: PaginationElements, config: PaginationConfig) {
    this.elements = elements;
    this.books = Array.from(this.elements.gallery.children) as HTMLElement[];

    this.state = {
      ...config,
      totalPages: Math.ceil(config.totalItems / config.itemsPerPage)
    };

    this.initializeEventListeners();
    this.renderPage();
  }

  private renderPage(): void {
    // Hide all books
    this.books.forEach(book => book.style.display = 'none');

    // Show books for current page
    const start = (this.state.currentPage - 1) * this.state.itemsPerPage;
    const end = start + this.state.itemsPerPage;
    this.books.slice(start, end).forEach(book => book.style.display = 'block');

    // Update page info
    this.elements.pageInfo.textContent =
      `Page ${this.state.currentPage} of ${this.state.totalPages}`;

    this.updateButtonStates();
    this.toggleNoResults();
  }

  private updateButtonStates(): void {
    // Previous button
    if (this.state.currentPage === 1) {
      this.elements.prevButton.classList.add('cursor-not-allowed', 'opacity-50');
      this.elements.prevButton.setAttribute('aria-disabled', 'true');
    } else {
      this.elements.prevButton.classList.remove('cursor-not-allowed', 'opacity-50');
      this.elements.prevButton.removeAttribute('aria-disabled');
    }

    // Next button
    if (this.state.currentPage === this.state.totalPages || this.state.totalPages === 0) {
      this.elements.nextButton.classList.add('cursor-not-allowed', 'opacity-50');
      this.elements.nextButton.setAttribute('aria-disabled', 'true');
    } else {
      this.elements.nextButton.classList.remove('cursor-not-allowed', 'opacity-50');
      this.elements.nextButton.removeAttribute('aria-disabled');
    }
  }

  private toggleNoResults(): void {
    if (this.state.totalPages === 0) {
      this.elements.noResults.classList.remove('hidden');
      this.elements.pagination.classList.add('hidden');
    } else {
      this.elements.noResults.classList.add('hidden');
      this.elements.pagination.classList.remove('hidden');
    }
  }

  private updatePagination(): void {
    // Implementation for updating pagination
  }

  private initializeEventListeners(): void {
    // Implementation for initializing event listeners
  }
} 