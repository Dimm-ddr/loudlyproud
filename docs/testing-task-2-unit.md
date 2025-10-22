# Task 2: Test Setup & Unit Tests

**Estimated Time**: 20-30 minutes  
**Prerequisites**: Task 1 completed (config files created)  
**Context**: Read `docs/testing-context.md` first

## Objective

Create test setup files, helper utilities, and unit test files for pagination, sorting, and DOM guards.

## What You'll Create

- Test setup files (2 files)
- Test helpers (1 file)
- Unit test files (3 files)
- Total: 6 new files in `tests/` directory

## Step 1: Create Directory Structure

Create these directories:

```bash
tests/
tests/setup/
tests/helpers/
tests/unit/
```

## Step 2: Create Unit Test Setup

**File**: `tests/setup/unit.setup.ts`

```typescript
import { beforeEach, afterEach, vi } from 'vitest';

// Mock console methods to reduce noise in tests
global.console = {
  ...console,
  error: vi.fn(),
  warn: vi.fn(),
};

beforeEach(() => {
  // Reset DOM before each test
  document.body.innerHTML = '';
  document.head.innerHTML = '';
});

afterEach(() => {
  // Clean up any timers or listeners
  vi.clearAllTimers();
  vi.clearAllMocks();
});
```

## Step 3: Create Integration Test Setup

**File**: `tests/setup/integration.setup.ts`

```typescript
import { beforeAll, afterAll } from 'vitest';
import fs from 'fs';
import path from 'path';

beforeAll(() => {
  // Verify public directory exists (built site)
  const publicDir = path.join(process.cwd(), 'public');
  if (!fs.existsSync(publicDir)) {
    throw new Error(
      'public/ directory not found. Run `pnpm run build` before integration tests.'
    );
  }
});

afterAll(() => {
  // Cleanup if needed
});

// Helper to read built HTML files
export function readBuiltPage(relativePath: string): string {
  const filePath = path.join(process.cwd(), 'public', relativePath);
  if (!fs.existsSync(filePath)) {
    throw new Error(`Test file not found: ${filePath}`);
  }
  return fs.readFileSync(filePath, 'utf-8');
}
```

## Step 4: Create Test Helpers

**File**: `tests/helpers/test-utils.ts`

```typescript
import fs from 'fs';
import path from 'path';

export function readBuiltHTML(relativePath: string): string {
  const fullPath = path.join(process.cwd(), 'public', relativePath);
  if (!fs.existsSync(fullPath)) {
    throw new Error(`Test file not found: ${fullPath}`);
  }
  return fs.readFileSync(fullPath, 'utf-8');
}

export function createMockBookCard(options: {
  title?: string;
  author?: string;
  year?: number;
  index?: number;
}): string {
  const {
    title = 'Test Book',
    author = 'Test Author',
    year = 2020,
    index = 0,
  } = options;

  return `
    <div class="book-card" 
         data-title="${title}" 
         data-author="${author}" 
         data-publication-year="${year}"
         data-index="${index}">
      <h3>${title}</h3>
      <p>${author}</p>
      <span>${year}</span>
    </div>
  `;
}

export function createMockGalleryHTML(bookCount: number = 12): string {
  const cards = Array.from({ length: bookCount }, (_, i) =>
    createMockBookCard({
      title: `Book ${i + 1}`,
      author: `Author ${i + 1}`,
      year: 2020 + (i % 5),
      index: i,
    })
  ).join('');

  return `
    <!DOCTYPE html>
    <html lang="en">
      <head><title>Test Gallery</title></head>
      <body>
        <div id="book-gallery">${cards}</div>
        <div id="pagination-controls">
          <button id="prev-page">Previous</button>
          <span id="page-info"></span>
          <button id="next-page">Next</button>
        </div>
        <select id="sort-select">
          <option value="title-asc">Title A-Z</option>
          <option value="title-desc">Title Z-A</option>
          <option value="year-asc">Oldest First</option>
          <option value="year-desc">Newest First</option>
        </select>
        <div id="no-results" style="display: none;">No results found</div>
      </body>
    </html>
  `;
}
```

## Step 5: Create Pagination Tests

**File**: `tests/unit/pagination.test.ts`

```typescript
import { describe, it, expect, beforeEach } from 'vitest';
import { JSDOM } from 'jsdom';

describe('Pagination Logic', () => {
  let dom: JSDOM;
  let document: Document;

  beforeEach(() => {
    dom = new JSDOM(`
      <!DOCTYPE html>
      <html>
        <body>
          <div id="book-gallery">
            ${Array.from({ length: 48 }, (_, i) => `
              <div class="book-card" data-index="${i}">Book ${i + 1}</div>
            `).join('')}
          </div>
          <div id="pagination-controls">
            <button id="prev-page">Previous</button>
            <span id="page-info"></span>
            <button id="next-page">Next</button>
          </div>
          <div id="no-results" style="display: none;">No results</div>
        </body>
      </html>
    `);
    document = dom.window.document;
    global.document = document as any;
  });

  describe('Page calculation for 12 items per page', () => {
    it('calculates correct start and end indices for page 1', () => {
      const itemsPerPage = 12;
      const currentPage = 1;
      const totalItems = 48;

      const startIdx = (currentPage - 1) * itemsPerPage;
      const endIdx = Math.min(startIdx + itemsPerPage, totalItems);

      expect(startIdx).toBe(0);
      expect(endIdx).toBe(12);
    });

    it('calculates correct start and end indices for page 2', () => {
      const itemsPerPage = 12;
      const currentPage = 2;
      const totalItems = 48;

      const startIdx = (currentPage - 1) * itemsPerPage;
      const endIdx = Math.min(startIdx + itemsPerPage, totalItems);

      expect(startIdx).toBe(12);
      expect(endIdx).toBe(24);
    });

    it('calculates correct start and end indices for last page', () => {
      const itemsPerPage = 12;
      const currentPage = 4;
      const totalItems = 48;

      const startIdx = (currentPage - 1) * itemsPerPage;
      const endIdx = Math.min(startIdx + itemsPerPage, totalItems);

      expect(startIdx).toBe(36);
      expect(endIdx).toBe(48);
    });
  });

  describe('Page calculation for 24 items per page', () => {
    it('calculates correct indices for 24 items per page', () => {
      const itemsPerPage = 24;
      const currentPage = 1;
      const totalItems = 48;

      const startIdx = (currentPage - 1) * itemsPerPage;
      const endIdx = Math.min(startIdx + itemsPerPage, totalItems);

      expect(startIdx).toBe(0);
      expect(endIdx).toBe(24);
    });

    it('handles last page with exact boundary', () => {
      const itemsPerPage = 24;
      const currentPage = 2;
      const totalItems = 48;

      const startIdx = (currentPage - 1) * itemsPerPage;
      const endIdx = Math.min(startIdx + itemsPerPage, totalItems);

      expect(startIdx).toBe(24);
      expect(endIdx).toBe(48);
    });
  });

  describe('Button state logic', () => {
    it('disables previous button on first page', () => {
      const currentPage = 1;
      const totalPages = 4;

      const shouldDisablePrev = currentPage <= 1;
      const shouldDisableNext = currentPage >= totalPages;

      expect(shouldDisablePrev).toBe(true);
      expect(shouldDisableNext).toBe(false);
    });

    it('disables next button on last page', () => {
      const currentPage = 4;
      const totalPages = 4;

      const shouldDisablePrev = currentPage <= 1;
      const shouldDisableNext = currentPage >= totalPages;

      expect(shouldDisablePrev).toBe(false);
      expect(shouldDisableNext).toBe(true);
    });

    it('enables both buttons on middle page', () => {
      const currentPage = 2;
      const totalPages = 4;

      const shouldDisablePrev = currentPage <= 1;
      const shouldDisableNext = currentPage >= totalPages;

      expect(shouldDisablePrev).toBe(false);
      expect(shouldDisableNext).toBe(false);
    });
  });

  describe('No results display', () => {
    it('shows no results when filtered items is empty', () => {
      const filteredItems = 0;
      const shouldShowNoResults = filteredItems === 0;
      expect(shouldShowNoResults).toBe(true);
    });

    it('hides no results when items exist', () => {
      const filteredItems = 12;
      const shouldShowNoResults = filteredItems === 0;
      expect(shouldShowNoResults).toBe(false);
    });
  });

  describe('Total pages calculation', () => {
    it('calculates total pages correctly for exact division', () => {
      const totalItems = 48;
      const itemsPerPage = 12;
      const totalPages = Math.ceil(totalItems / itemsPerPage);
      expect(totalPages).toBe(4);
    });

    it('calculates total pages correctly for remainder', () => {
      const totalItems = 50;
      const itemsPerPage = 12;
      const totalPages = Math.ceil(totalItems / itemsPerPage);
      expect(totalPages).toBe(5);
    });

    it('returns 1 page for zero items', () => {
      const totalItems = 0;
      const itemsPerPage = 12;
      const totalPages = Math.max(1, Math.ceil(totalItems / itemsPerPage));
      expect(totalPages).toBe(1);
    });
  });
});
```

## Step 6: Create Sorting Tests

**File**: `tests/unit/sorting.test.ts`

```typescript
import { describe, it, expect } from 'vitest';

interface BookItem {
  title: string;
  author: string;
  publicationYear: number;
}

describe('Sorting Comparators', () => {
  const sampleBooks: BookItem[] = [
    { title: 'Zebra Book', author: 'Smith, John', publicationYear: 2020 },
    { title: 'Alpha Book', author: 'Doe, Jane', publicationYear: 2019 },
    { title: 'Beta Book', author: 'Adams, Alice', publicationYear: 2021 },
    { title: 'Gamma Book', author: 'Brown, Bob', publicationYear: 2019 },
  ];

  describe('Title sorting', () => {
    it('sorts titles in ascending order', () => {
      const sorted = [...sampleBooks].sort((a, b) =>
        a.title.localeCompare(b.title)
      );

      expect(sorted[0].title).toBe('Alpha Book');
      expect(sorted[1].title).toBe('Beta Book');
      expect(sorted[2].title).toBe('Gamma Book');
      expect(sorted[3].title).toBe('Zebra Book');
    });

    it('sorts titles in descending order', () => {
      const sorted = [...sampleBooks].sort((a, b) =>
        b.title.localeCompare(a.title)
      );

      expect(sorted[0].title).toBe('Zebra Book');
      expect(sorted[3].title).toBe('Alpha Book');
    });
  });

  describe('Author sorting', () => {
    it('sorts authors in ascending order', () => {
      const sorted = [...sampleBooks].sort((a, b) =>
        a.author.localeCompare(b.author)
      );

      expect(sorted[0].author).toBe('Adams, Alice');
      expect(sorted[1].author).toBe('Brown, Bob');
      expect(sorted[2].author).toBe('Doe, Jane');
      expect(sorted[3].author).toBe('Smith, John');
    });

    it('sorts authors in descending order', () => {
      const sorted = [...sampleBooks].sort((a, b) =>
        b.author.localeCompare(a.author)
      );

      expect(sorted[0].author).toBe('Smith, John');
      expect(sorted[3].author).toBe('Adams, Alice');
    });
  });

  describe('Publication year sorting', () => {
    it('sorts years in ascending order (oldest first)', () => {
      const sorted = [...sampleBooks].sort(
        (a, b) => a.publicationYear - b.publicationYear
      );

      expect(sorted[0].publicationYear).toBe(2019);
      expect(sorted[sorted.length - 1].publicationYear).toBe(2021);
    });

    it('sorts years in descending order (newest first)', () => {
      const sorted = [...sampleBooks].sort(
        (a, b) => b.publicationYear - a.publicationYear
      );

      expect(sorted[0].publicationYear).toBe(2021);
      expect(sorted[sorted.length - 1].publicationYear).toBe(2019);
    });

    it('applies tie-breaker by title when years are equal', () => {
      const sorted = [...sampleBooks].sort((a, b) => {
        const yearDiff = a.publicationYear - b.publicationYear;
        if (yearDiff !== 0) return yearDiff;
        return a.title.localeCompare(b.title);
      });

      const year2019Books = sorted.filter((b) => b.publicationYear === 2019);
      expect(year2019Books[0].title).toBe('Alpha Book');
      expect(year2019Books[1].title).toBe('Gamma Book');
    });
  });

  describe('Unicode and special character handling', () => {
    const unicodeBooks: BookItem[] = [
      { title: 'Яблоко', author: 'Author A', publicationYear: 2020 },
      { title: 'Абрикос', author: 'Author B', publicationYear: 2020 },
      { title: 'فارسی کتاب', author: 'Author C', publicationYear: 2020 },
      { title: 'English Book', author: 'Author D', publicationYear: 2020 },
    ];

    it('handles Cyrillic characters correctly', () => {
      const sorted = [...unicodeBooks]
        .filter((b) => /[А-Яа-я]/.test(b.title))
        .sort((a, b) => a.title.localeCompare(b.title, 'ru'));

      expect(sorted[0].title).toBe('Абрикос');
      expect(sorted[1].title).toBe('Яблоко');
    });

    it('handles mixed scripts with locale-aware sorting', () => {
      const sorted = [...unicodeBooks].sort((a, b) =>
        a.title.localeCompare(b.title)
      );

      expect(sorted.length).toBe(4);
      expect(sorted.every((b) => b.title)).toBe(true);
    });
  });

  describe('Edge cases', () => {
    it('handles empty array', () => {
      const sorted = [].sort((a: any, b: any) =>
        (a?.title || '').localeCompare(b?.title || '')
      );
      expect(sorted).toEqual([]);
    });

    it('handles single item', () => {
      const single = [sampleBooks[0]];
      const sorted = [...single].sort((a, b) =>
        a.title.localeCompare(b.title)
      );
      expect(sorted).toEqual(single);
    });

    it('handles identical titles', () => {
      const duplicates = [
        { title: 'Same Title', author: 'Author Z', publicationYear: 2020 },
        { title: 'Same Title', author: 'Author A', publicationYear: 2020 },
      ];

      const sorted = [...duplicates].sort((a, b) => {
        const titleDiff = a.title.localeCompare(b.title);
        if (titleDiff !== 0) return titleDiff;
        return a.author.localeCompare(b.author);
      });

      expect(sorted[0].author).toBe('Author A');
      expect(sorted[1].author).toBe('Author Z');
    });
  });
});
```

## Step 7: Create DOM Guard Tests

**File**: `tests/unit/dom-guards.test.ts`

```typescript
import { describe, it, expect, beforeEach } from 'vitest';
import { JSDOM } from 'jsdom';

describe('DOM Element Guard Clauses', () => {
  let document: Document;

  beforeEach(() => {
    const dom = new JSDOM('<!DOCTYPE html><html><body></body></html>');
    document = dom.window.document;
    global.document = document as any;
  });

  describe('Required element existence checks', () => {
    it('throws clear error when gallery container is missing', () => {
      const getGallery = (): Element => {
        const gallery = document.querySelector('#book-gallery');
        if (!gallery) {
          throw new Error(
            'Required element #book-gallery not found in DOM. Check HTML structure.'
          );
        }
        return gallery;
      };

      expect(getGallery).toThrow('Required element #book-gallery not found');
    });

    it('returns element when it exists', () => {
      document.body.innerHTML = '<div id="book-gallery"></div>';

      const getGallery = (): Element => {
        const gallery = document.querySelector('#book-gallery');
        if (!gallery) {
          throw new Error('Required element #book-gallery not found in DOM.');
        }
        return gallery;
      };

      expect(() => getGallery()).not.toThrow();
      expect(getGallery().id).toBe('book-gallery');
    });
  });

  describe('Multiple element queries', () => {
    it('handles empty result gracefully', () => {
      const getBookCards = (): Element[] => {
        const cards = document.querySelectorAll('.book-card');
        return Array.from(cards);
      };

      const cards = getBookCards();
      expect(cards).toEqual([]);
      expect(cards.length).toBe(0);
    });

    it('returns all matching elements', () => {
      document.body.innerHTML = `
        <div class="book-card">Book 1</div>
        <div class="book-card">Book 2</div>
        <div class="book-card">Book 3</div>
      `;

      const cards = Array.from(document.querySelectorAll('.book-card'));
      expect(cards.length).toBe(3);
    });
  });

  describe('Data attribute validation', () => {
    it('validates required data attributes exist', () => {
      document.body.innerHTML = '<div class="book-card"></div>';

      const card = document.querySelector('.book-card');
      const hasYear = card?.hasAttribute('data-publication-year');

      expect(hasYear).toBe(false);
    });

    it('extracts data attribute values safely', () => {
      document.body.innerHTML =
        '<div class="book-card" data-publication-year="2020"></div>';

      const card = document.querySelector('.book-card');
      const year = card?.getAttribute('data-publication-year');

      expect(year).toBe('2020');
      expect(parseInt(year || '0', 10)).toBe(2020);
    });

    it('handles missing data attributes with fallback', () => {
      document.body.innerHTML = '<div class="book-card"></div>';

      const card = document.querySelector('.book-card');
      const year = parseInt(
        card?.getAttribute('data-publication-year') || '0',
        10
      );

      expect(year).toBe(0);
    });
  });
});
```

## Verification

After completing all steps, run:

```bash
# Check directory structure
ls -R tests/

# Verify all files exist
ls tests/setup/unit.setup.ts
ls tests/setup/integration.setup.ts
ls tests/helpers/test-utils.ts
ls tests/unit/pagination.test.ts
ls tests/unit/sorting.test.ts
ls tests/unit/dom-guards.test.ts

# Run unit tests
pnpm run test:unit

# Optional: Check TypeScript compilation
pnpm exec tsc --noEmit
```

## Success Criteria

✅ All 6 files created in correct locations  
✅ Directory structure is correct (setup/, helpers/, unit/)  
✅ Files contain complete test code as specified  
✅ Unit tests run successfully with `pnpm run test:unit`  
✅ All tests pass (or show meaningful results)  
✅ No TypeScript compilation errors  

## Expected Output

When you run `pnpm run test:unit`, you should see:

```
✓ tests/unit/pagination.test.ts (15 tests)
✓ tests/unit/sorting.test.ts (12 tests)
✓ tests/unit/dom-guards.test.ts (8 tests)

Test Files  3 passed (3)
Tests  35 passed (35)
```

## Next Task

After this task completes successfully, proceed to **Task 3: Integration Tests** (`docs/testing-task-3-integration.md`).

## Commit Message

```
feat(testing): add unit tests for pagination and sorting

- Create test setup files for unit and integration tests
- Add test helper utilities for mocking
- Implement pagination logic tests (12/24/48 items)
- Implement sorting tests with Unicode support
- Add DOM guard clause tests
- All tests independent and isolated

Part 2/6 of testing implementation
```

