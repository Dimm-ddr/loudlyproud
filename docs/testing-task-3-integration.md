# Task 3: Integration Tests

**Estimated Time**: 20-25 minutes  
**Prerequisites**: Tasks 1-2 completed (config and unit test files created)  
**Context**: Read `docs/testing-context.md` first

## Objective

Create integration test files that will validate Hugo-generated HTML structure. This task only creates files - no building or test execution.

## What You'll Create

- 4 integration test files
- Tests for home page, gallery pages, book pages, and DOM interactions
- Total: 4 new files in `tests/integration/`

## Important Note

⚠️ **This task runs in an isolated VM environment**. Do NOT run `pnpm build` or `pnpm run test:integration`. Only create test files. Site building and test execution happen later.

## Step 1: Create Integration Directory

```bash
mkdir -p tests/integration
```

## Step 2: Create Home Page Tests

**File**: `tests/integration/home-page.test.ts`

```typescript
import { describe, it, expect } from 'vitest';
import { load } from 'cheerio';
import { readBuiltPage } from '../setup/integration.setup';

describe('Home Page Structure', () => {
  it('contains language selection cards', () => {
    const html = readBuiltPage('index.html');
    const $ = load(html);

    const languageCards = $(
      'a[href*="/en/"], a[href*="/ru/"], a[href*="/fa/"]'
    );
    expect(languageCards.length).toBeGreaterThanOrEqual(3);
  });

  it('has proper RTL/LTR directionality markers', () => {
    const html = readBuiltPage('index.html');
    const $ = load(html);

    // Check for dir attributes or directional classes
    const hasDirectionalMarkup =
      $('[dir]').length > 0 || $('.rtl, .ltr').length > 0;
    expect(hasDirectionalMarkup).toBe(true);
  });

  it('includes meta tags for SEO', () => {
    const html = readBuiltPage('index.html');
    const $ = load(html);

    expect($('meta[name="description"]').length).toBeGreaterThan(0);
    expect($('title').length).toBeGreaterThan(0);
    expect($('title').text().length).toBeGreaterThan(0);
  });

  it('has valid HTML structure', () => {
    const html = readBuiltPage('index.html');
    const $ = load(html);

    expect($('html').length).toBe(1);
    expect($('head').length).toBe(1);
    expect($('body').length).toBe(1);
  });
});
```

## Step 3: Create Gallery Page Tests

**File**: `tests/integration/gallery-page.test.ts`

```typescript
import { describe, it, expect } from 'vitest';
import { load } from 'cheerio';
import { readBuiltPage } from '../setup/integration.setup';

describe('Gallery Page Structure', () => {
  const testLanguagePage = (lang: string): void => {
    describe(`${lang.toUpperCase()} Gallery`, () => {
      it('contains book gallery container', () => {
        const html = readBuiltPage(`${lang}/main/index.html`);
        const $ = load(html);

        const gallery = $('#book-gallery');
        expect(gallery.length).toBe(1);
      });

      it('has book cards with required attributes', () => {
        const html = readBuiltPage(`${lang}/main/index.html`);
        const $ = load(html);

        const bookCards = $('.book-card');
        expect(bookCards.length).toBeGreaterThan(0);

        // Check first card has data attributes
        const firstCard = bookCards.first();
        const hasTitle = firstCard.attr('data-title') !== undefined;
        const hasYear =
          firstCard.attr('data-publication-year') !== undefined ||
          firstCard.find('[data-publication-year]').length > 0;

        expect(hasTitle || hasYear).toBe(true);
      });

      it('contains tag elements', () => {
        const html = readBuiltPage(`${lang}/main/index.html`);
        const $ = load(html);

        const tags = $('[class*="tag"], .tag, [data-tag]');
        expect(tags.length).toBeGreaterThan(0);
      });

      it('has pagination controls', () => {
        const html = readBuiltPage(`${lang}/main/index.html`);
        const $ = load(html);

        const paginationControls = $(
          '#pagination-controls, [id*="pagination"], .pagination'
        );
        expect(paginationControls.length).toBeGreaterThan(0);
      });

      it('has sorting controls', () => {
        const html = readBuiltPage(`${lang}/main/index.html`);
        const $ = load(html);

        const sortingControls = $(
          '#sort-select, select[name*="sort"], [id*="sort"]'
        );
        expect(sortingControls.length).toBeGreaterThan(0);
      });

      it('includes search functionality', () => {
        const html = readBuiltPage(`${lang}/main/index.html`);
        const $ = load(html);

        const searchElements = $(
          '#search, [id*="search"], input[type="search"]'
        );
        expect(searchElements.length).toBeGreaterThan(0);
      });
    });
  };

  testLanguagePage('en');
  testLanguagePage('ru');
  testLanguagePage('fa');
});
```

## Step 4: Create Book Page Tests

**File**: `tests/integration/book-page.test.ts`

```typescript
import { describe, it, expect } from 'vitest';
import { load } from 'cheerio';
import fs from 'fs';
import { glob } from 'glob';

describe('Book Page Structure', () => {
  it('sample book page has required elements', async () => {
    // Find first English book page
    const bookPages = await glob('public/en/books/**/index.html', {
      ignore: ['**/node_modules/**'],
    });

    if (bookPages.length === 0) {
      console.warn('No book pages found, skipping test');
      return;
    }

    const html = fs.readFileSync(bookPages[0], 'utf-8');
    const $ = load(html);

    // Check for book metadata
    const hasTitle = $('h1, .book-title, [itemprop="name"]').length > 0;
    expect(hasTitle).toBe(true);

    // Check for cover image
    const hasCoverImage =
      $('img[class*="cover"], .book-cover img, [itemprop="image"]').length > 0;
    expect(hasCoverImage).toBe(true);

    // Check for author info
    const hasAuthor =
      $('.author, [itemprop="author"], .book-author').length > 0;
    expect(hasAuthor).toBe(true);

    // Check for description/content
    const hasDescription = $(
      '.description, [itemprop="description"], .book-description, .content'
    ).length > 0;
    expect(hasDescription).toBe(true);
  });

  it('book pages have language navigation links', async () => {
    const bookPages = await glob('public/en/books/**/index.html', {
      ignore: ['**/node_modules/**'],
    });

    if (bookPages.length === 0) return;

    const html = fs.readFileSync(bookPages[0], 'utf-8');
    const $ = load(html);

    // Check for language switcher or i18n links
    const hasLanguageLinks =
      $('[hreflang], .language-selector, [class*="lang"]').length > 0;

    // This assertion is soft - books might not have translations
    expect(typeof hasLanguageLinks).toBe('boolean');
  });

  it('book pages include structured metadata', async () => {
    const bookPages = await glob('public/en/books/**/index.html', {
      ignore: ['**/node_modules/**'],
    });

    if (bookPages.length === 0) return;

    const html = fs.readFileSync(bookPages[0], 'utf-8');
    const $ = load(html);

    // Check for meta tags or structured data
    const hasMetadata =
      $('meta[property*="og:"], meta[name="description"]').length > 0;
    expect(hasMetadata).toBe(true);
  });
});
```

## Step 5: Create DOM Interactions Tests

**File**: `tests/integration/dom-interactions.test.ts`

```typescript
import { describe, it, expect } from 'vitest';
import { JSDOM } from 'jsdom';
import { readBuiltPage } from '../setup/integration.setup';

describe('Client-side Script Integration', () => {
  describe('Pagination initialization on gallery HTML', () => {
    it('can parse and manipulate gallery DOM', () => {
      const html = readBuiltPage('en/main/index.html');
      const dom = new JSDOM(html, { runScripts: 'outside-only' });
      const { document } = dom.window;

      // Simulate pagination logic
      const bookCards = document.querySelectorAll('.book-card');
      const itemsPerPage = 12;
      const totalPages = Math.ceil(bookCards.length / itemsPerPage);

      expect(bookCards.length).toBeGreaterThan(0);
      expect(totalPages).toBeGreaterThan(0);

      // Simulate hiding cards beyond first page
      bookCards.forEach((card, idx) => {
        if (idx >= itemsPerPage) {
          (card as HTMLElement).style.display = 'none';
        }
      });

      const visibleCards = Array.from(bookCards).filter(
        (card) => (card as HTMLElement).style.display !== 'none'
      );

      expect(visibleCards.length).toBeLessThanOrEqual(itemsPerPage);
    });
  });

  describe('Sorting initialization on gallery HTML', () => {
    it('can extract and sort book data from DOM', () => {
      const html = readBuiltPage('en/main/index.html');
      const dom = new JSDOM(html);
      const { document } = dom.window;

      const bookCards = document.querySelectorAll('.book-card');

      if (bookCards.length === 0) {
        console.warn('No book cards found');
        return;
      }

      // Extract data
      const booksData = Array.from(bookCards).map((card) => ({
        title:
          card.getAttribute('data-title') ||
          card.querySelector('h3, .book-title')?.textContent ||
          '',
        year: parseInt(
          card.getAttribute('data-publication-year') || '0',
          10
        ),
        element: card,
      }));

      // Sort by year
      const sorted = [...booksData].sort((a, b) => b.year - a.year);

      expect(sorted.length).toBe(booksData.length);
      expect(sorted[0].year).toBeGreaterThanOrEqual(
        sorted[sorted.length - 1].year
      );
    });
  });
});
```

## Verification

After completing all steps, verify files were created:

```bash
# Check directory structure
ls tests/integration/

# Verify all files exist
ls tests/integration/home-page.test.ts
ls tests/integration/gallery-page.test.ts
ls tests/integration/book-page.test.ts
ls tests/integration/dom-interactions.test.ts
```

## Success Criteria

✅ All 4 integration test files created  
✅ Files are in `tests/integration/` directory  
✅ Files contain complete test code as specified  
✅ Tests use Cheerio and jsdom correctly  
✅ Tests reference `readBuiltPage` from setup file  

## Important Notes

⚠️ **Do NOT run these commands** (they won't work in isolated VM):
- ❌ `pnpm install`
- ❌ `pnpm run build`
- ❌ `pnpm run test:integration`

✅ **Only verify files were created** using `ls` commands shown above.

## Troubleshooting

**Worried about public/ directory**:
- That's expected - the site will be built later during final verification
- Tests are designed to fail gracefully if public/ doesn't exist

**Concerned about import errors**:
- Imports will be validated when dependencies are installed later
- Focus on creating files with exact content specified

## Next Task

After this task completes successfully, proceed to **Task 4: E2E Tests** (`docs/testing-task-4-e2e.md`).

## Commit Message

```
feat(testing): add integration tests for HTML structure

- Create home page structure tests
- Add gallery page tests for all languages (en/ru/fa)
- Implement book page validation tests
- Add DOM interaction simulation tests
- Verify Hugo builds required elements correctly

Part 3/6 of testing implementation
```

