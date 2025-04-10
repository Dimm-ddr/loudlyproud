import { Book } from "../types";

interface SortConfig {
    selectors: {
        gallery: string;
        sortSelect: string;
    };
    onSort?: () => void;
}

type SortOption = 'title_asc' | 'title_desc' | 'author_asc' | 'author_desc' | 'year_asc' | 'year_desc';

interface BookSortData {
    element: HTMLElement;
    title: string;
    author: string;
    year: number;
}

export class Sorting {
    private elements: {
        gallery: HTMLElement;
        sortSelect: HTMLSelectElement;
    };

    private config: {
        currentSort: SortOption;
        onSort?: () => void;
    };

    private bookElements: BookSortData[] = [];

    constructor(config: SortConfig) {
        // Get elements using provided selectors
        const elements = {
            gallery: document.querySelector(config.selectors.gallery),
            sortSelect: document.querySelector(config.selectors.sortSelect),
        };

        // Validate that all required elements exist
        Object.entries(elements).forEach(([key, element]) => {
            if (!element) {
                // Use type guard to check if key is valid
                const isValidKey = (k: string): k is keyof SortConfig['selectors'] => 
                    k in config.selectors;
                
                if (isValidKey(key)) {
                    throw new Error(
                        `Required element "${key}" not found using selector "${config.selectors[key]}"`,
                    );
                } else {
                    throw new Error(`Required element "${key}" not found with unknown selector`);
                }
            }
        });

        // Type assertion after validation
        this.elements = elements as {
            gallery: HTMLElement;
            sortSelect: HTMLSelectElement;
        };

        this.config = {
            currentSort: this.elements.sortSelect.value as SortOption,
            onSort: config.onSort,
        };

        this.initializeBookElements();
        this.initializeEventListeners();
        this.applySort(this.config.currentSort);
    }

    private initializeBookElements(): void {
        // Store original book elements with their sort data
        this.bookElements = Array.from(this.elements.gallery.children).map((bookElement) => {
            const element = bookElement as HTMLElement;
            
            // Extract title from element
            const titleElement = element.querySelector('.book-card h2 a');
            const title = titleElement ? titleElement.textContent || '' : '';
            
            // Extract author from element
            const authorElement = element.querySelector('.book-authors');
            const author = authorElement ? authorElement.textContent || '' : '';
            
            // Extract year from element
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
            const selectedSort = this.elements.sortSelect.value as SortOption;
            this.applySort(selectedSort);
            
            // Call onSort callback if provided
            if (this.config.onSort) {
                this.config.onSort();
            }
        });
    }

    private applySort(sortOption: SortOption): void {
        this.config.currentSort = sortOption;
        
        // Sort book elements based on the selected option
        const sortedElements = [...this.bookElements].sort((a, b) => {
            switch (sortOption) {
                case 'title_asc':
                    return a.title.localeCompare(b.title);
                case 'title_desc':
                    return b.title.localeCompare(a.title);
                case 'author_asc':
                    return a.author.localeCompare(b.author);
                case 'author_desc':
                    return b.author.localeCompare(a.author);
                case 'year_asc':
                    return a.year - b.year;
                case 'year_desc':
                    return b.year - a.year;
                default:
                    return 0;
            }
        });

        // Remove all current child elements
        while (this.elements.gallery.firstChild) {
            this.elements.gallery.removeChild(this.elements.gallery.firstChild);
        }

        // Append sorted elements back to the gallery
        sortedElements.forEach(item => {
            this.elements.gallery.appendChild(item.element);
        });
    }
} 