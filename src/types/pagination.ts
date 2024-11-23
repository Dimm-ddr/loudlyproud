export interface PaginationConfig {
  itemsPerPage: number;
  currentPage: number;
  totalItems: number;
}

export interface PaginationElements {
  gallery: HTMLElement;
  itemsPerPageSelect: HTMLSelectElement;
  prevButton: HTMLButtonElement;
  nextButton: HTMLButtonElement;
  pageInfo: HTMLElement;
  noResults: HTMLElement;
  pagination: HTMLElement;
}

export interface PaginationState extends PaginationConfig {
  totalPages: number;
} 