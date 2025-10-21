# Testing Implementation Context

This document provides general context for implementing automated testing in the Loudly Proud project. This context applies to all testing implementation tasks.

## Project Overview

**Loudly Proud** is a multilingual LGBTQ+ literature catalog built with Hugo, serving content in English, Russian, Farsi, and Kurdish with RTL support.

### Architecture

**Static Site Generator**: Hugo (extended version)
- Content: `content/{lang}/books/*.md`
- Templates: `layouts/`
- Output: `public/` directory
- Multilingual routing: `/en/`, `/ru/`, `/fa/`, `/ku/`

**Client-Side Scripts**: TypeScript compiled via Hugo Pipes
- `assets/js/pagination.ts` - Pagination logic
- `assets/js/sorting.ts` - Sorting comparators
- `assets/js/accessibility-enhancements.ts` - A11y features

**Styling**: TailwindCSS with component system

**Search**: Pagefind (static, client-side)

**Build Tools**: pnpm, Node.js ≥18

**Deployment**: Netlify

### What We're Testing

1. **Pagination Logic**: Page calculations, button states, no-results display
2. **Sorting Logic**: Title/author/year sorting with Unicode support (Cyrillic, Arabic)
3. **HTML Structure**: Gallery pages, book pages, i18n links, RTL/LTR directionality
4. **User Workflows**: Language switching, navigation, search
5. **Accessibility**: WCAG 2.1 AA compliance
6. **Site Quality**: No broken links, valid HTML

### Testing Strategy

We're implementing a **three-tier testing pyramid**:

```
        /\
       /E2E\       ← Few tests, critical paths (Playwright)
      /------\
     /  Integ \    ← Medium, structure validation (Cheerio + jsdom)
    /----------\
   /    Unit    \  ← Many tests, fast logic (Vitest + jsdom)
  /--------------\
```

**Tool Choices**:
- **Vitest** (not Jest): Faster, better ESM support, built-in TypeScript
- **jsdom**: DOM simulation for Node environment
- **Playwright** (not Cypress): Better multi-browser support, faster
- **Cheerio**: Fast HTML parsing without browser
- **Pa11y**: Accessibility testing
- **Linkinator**: Link validation

### Project Conventions

**Modern TypeScript**:
- Use strict mode, explicit types
- No `any` types
- Type annotations on all functions
- Use modern features (f-strings style templates, optional chaining)

**Test Independence**:
- Each test runs independently
- No shared state between tests
- Use `beforeEach` for setup, not shared variables
- Tests can run in any order

**Error Handling**:
- Clear, actionable error messages
- Guard clauses with descriptive throws
- Graceful degradation for optional elements

### File Structure

**Current**:
```
loudlyproud/
├── assets/js/              ← TypeScript client scripts
├── src/js/                 ← Additional utilities
├── content/{lang}/books/   ← Markdown content
├── layouts/                ← Hugo templates
├── public/                 ← Built site (generated)
├── package.json
├── tsconfig.json
└── docs/
```

**Testing Structure** (to be built):
```
tests/
├── setup/           ← Setup files for test environments
├── helpers/         ← Shared test utilities
├── unit/            ← Fast, isolated logic tests
├── integration/     ← HTML structure validation
└── e2e/             ← Browser-based workflow tests
```

### Important Integration Points

**package.json**:
- ALWAYS merge new scripts with existing
- NEVER replace existing scripts
- Add to "scripts" and "devDependencies"

**tsconfig.json**:
- Check existing path aliases before creating test configs
- Common aliases: `@` → `./assets`, `@src` → `./src`
- Match these in Vitest configs

**Build Requirement**:
- Integration and E2E tests require `public/` directory
- Must run `pnpm run build` before these tests
- Unit tests can run without building

### Task Breakdown Philosophy

The testing implementation is split into **6 independent file-creation tasks**:

1. **Configuration Files** - Config files and package.json scripts
2. **Test Setup & Unit Tests** - Setup files and unit test files
3. **Integration Tests** - HTML structure validation test files
4. **E2E Tests** - User workflow test files
5. **CI/CD Workflows** - GitHub Actions workflow files
6. **Documentation & Validation** - Testing guide and validation script

**Important**: Each task runs in a fresh VM environment:
- ✅ Repository files from previous tasks persist (committed)
- ❌ `node_modules/` does NOT persist
- ❌ Installed packages do NOT persist
- ❌ Built site (`public/`) does NOT persist

Therefore, each task:
- **Only creates/modifies files** (no npm install, no running tests, no building)
- Can be completed independently in a fresh environment
- Commits files at the end
- Takes ~15-30 minutes to complete

**Verification**: After all 6 tasks complete, a human runs:
```bash
pnpm install
pnpm run validate:tests
pnpm run test:unit
pnpm run build
pnpm run test:integration
pnpm run test:e2e
```

### Common Verification Commands

After any task:
```bash
# Check TypeScript compilation
pnpm exec tsc --noEmit

# Check file structure
ls -R tests/

# Install dependencies if needed
pnpm install
```

### Troubleshooting

**Dependencies won't install**:
- Ensure Node.js ≥18
- Try: `pnpm install --shamefully-hoist`

**TypeScript errors**:
- Verify `tsconfig.json` exists
- Check path aliases match
- Run: `pnpm exec tsc --noEmit`

**Tests can't find files**:
- Integration/E2E: Run `pnpm run build` first
- Check paths are case-sensitive
- Verify `public/` directory exists

**Import errors**:
- Check package is in devDependencies
- Run: `pnpm install`
- Verify import paths match installed packages

---

## Reference Documents

Each task has its own specification file:
- `docs/testing-task-1-setup.md`
- `docs/testing-task-2-unit.md`
- `docs/testing-task-3-integration.md`
- `docs/testing-task-4-e2e.md`
- `docs/testing-task-5-ci.md`
- `docs/testing-task-6-docs.md`

All task prompts are in: `docs/testing-implementation-prompts.md`

---

This context document should be referenced by all testing tasks but does not contain implementation details - those are in the individual task files.

