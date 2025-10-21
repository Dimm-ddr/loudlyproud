# Task 6: Documentation & Validation

**Estimated Time**: 20-25 minutes  
**Prerequisites**: Tasks 1-5 completed (all tests and CI working)  
**Context**: Read `docs/testing-context.md` first

## Objective

Create comprehensive documentation for the testing system and a validation script to verify all components are in place. This is the final task that completes the testing implementation.

## What You'll Create

- Testing guide documentation
- Validation script
- Updates to main README
- Total: 3 files created/modified

## Step 1: Create Testing Guide

**File**: `docs/testing-guide.md`

```markdown
# Testing Guide

This document describes how to run tests for the Loudly Proud project.

## Test Structure

We use a three-tier testing approach:

1. **Unit Tests** (`tests/unit/`): Fast, isolated tests for business logic
2. **Integration Tests** (`tests/integration/`): Tests verifying Hugo build output and DOM structure
3. **E2E Tests** (`tests/e2e/`): Full browser tests for user workflows

## Prerequisites

```bash
pnpm install
pnpm run playwright:install
```

## Running Tests

### All Tests
```bash
pnpm run test:all
```

### Unit Tests Only
```bash
pnpm run test:unit
```

### Integration Tests Only
```bash
# Requires building first
pnpm run build
pnpm run test:integration
```

### E2E Tests Only
```bash
# Requires building first
pnpm run build
pnpm run test:e2e
```

### Watch Mode (for development)
```bash
pnpm run test:watch
```

### With UI
```bash
pnpm run test:ui
```

## Accessibility Testing

```bash
pnpm run build
pnpm run test:a11y
```

## Link Checking

```bash
pnpm run build
pnpm run test:links
```

## CI/CD

Tests run automatically on:
- Push to main, preview, develop branches
- Pull requests to main, preview branches

See `.github/workflows/test.yml` for CI configuration.

## Writing New Tests

### Unit Tests
- Place in `tests/unit/`
- Use Vitest + jsdom
- Test pure functions and isolated logic
- Name files: `*.test.ts`

### Integration Tests
- Place in `tests/integration/`
- Use Cheerio for HTML parsing
- Test built HTML structure
- Name files: `*.test.ts`

### E2E Tests
- Place in `tests/e2e/`
- Use Playwright
- Test critical user workflows
- Keep minimal and focused
- Name files: `*.spec.ts`

## Test Guidelines

### Test Independence
- Each test must run independently
- No shared state between tests
- Use `beforeEach` for setup
- Tests should pass in any order

### Error Messages
- Use clear, descriptive assertions
- Provide actionable error messages
- Include context in failure messages

### Performance
- Unit tests should be fast (<5s total)
- Integration tests under 30s
- E2E tests under 2 minutes

## Debugging

### Debug Unit/Integration Tests
```bash
pnpm run test:watch
```

### Debug E2E Tests
```bash
pnpm run test:e2e:debug
```

### View E2E Test UI
```bash
pnpm run test:e2e:ui
```

### View Coverage
```bash
pnpm run test:unit -- --coverage
```

Coverage reports are generated in `coverage/` directory.

## Troubleshooting

### Tests fail with "module not found"
- Run: `pnpm install`
- Check import paths are correct
- Verify package is in devDependencies

### Integration tests fail with "file not found"
- Run: `pnpm run build`
- Check `public/` directory exists
- Verify paths are case-sensitive

### E2E tests timeout
- Increase timeout in playwright.config.ts
- Check site builds correctly
- Verify browser can access localhost:4173

### Playwright browser errors
- Run: `pnpm run playwright:install`
- Check system has required dependencies
- Try: `npx playwright install --with-deps chromium`

## Test File Structure

```
tests/
├── setup/              # Test environment setup
│   ├── unit.setup.ts
│   └── integration.setup.ts
├── helpers/            # Shared test utilities
│   └── test-utils.ts
├── unit/               # Unit tests
│   ├── pagination.test.ts
│   ├── sorting.test.ts
│   └── dom-guards.test.ts
├── integration/        # Integration tests
│   ├── home-page.test.ts
│   ├── gallery-page.test.ts
│   ├── book-page.test.ts
│   └── dom-interactions.test.ts
└── e2e/                # E2E tests
    ├── language-navigation.spec.ts
    ├── gallery-interactions.spec.ts
    ├── search.spec.ts
    └── accessibility.spec.ts
```

## Configuration Files

- `vitest.config.unit.ts` - Unit test configuration
- `vitest.config.integration.ts` - Integration test configuration
- `playwright.config.ts` - E2E test configuration
- `.pa11yci.json` - Accessibility test configuration
- `.linkinator.config.json` - Link checker configuration

## Further Reading

- [Vitest Documentation](https://vitest.dev/)
- [Playwright Documentation](https://playwright.dev/)
- [Testing Best Practices](https://testingjavascript.com/)
```

## Step 2: Create Validation Script

**File**: `scripts/validate-tests.js`

```javascript
#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const requiredFiles = [
  'vitest.config.unit.ts',
  'vitest.config.integration.ts',
  'playwright.config.ts',
  '.pa11yci.json',
  '.linkinator.config.json',
  'tests/setup/unit.setup.ts',
  'tests/setup/integration.setup.ts',
  'tests/helpers/test-utils.ts',
  'tests/unit/pagination.test.ts',
  'tests/unit/sorting.test.ts',
  'tests/unit/dom-guards.test.ts',
  'tests/integration/home-page.test.ts',
  'tests/integration/gallery-page.test.ts',
  'tests/integration/book-page.test.ts',
  'tests/integration/dom-interactions.test.ts',
  'tests/e2e/language-navigation.spec.ts',
  'tests/e2e/gallery-interactions.spec.ts',
  'tests/e2e/search.spec.ts',
  'tests/e2e/accessibility.spec.ts',
  '.github/workflows/test.yml',
  '.github/workflows/accessibility.yml',
  'docs/testing-guide.md',
];

console.log('Validating test setup...\n');

let allValid = true;

for (const file of requiredFiles) {
  const filePath = path.join(process.cwd(), file);
  const exists = fs.existsSync(filePath);

  console.log(`${exists ? '✓' : '✗'} ${file}`);

  if (!exists) {
    allValid = false;
  }
}

console.log(
  '\n' +
    (allValid ? '✓ All test files present' : '✗ Some test files missing')
);

// Check package.json scripts
const packageJsonPath = path.join(process.cwd(), 'package.json');
if (!fs.existsSync(packageJsonPath)) {
  console.error('\n✗ package.json not found');
  process.exit(1);
}

const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf-8'));
const requiredScripts = [
  'test',
  'test:unit',
  'test:integration',
  'test:e2e',
  'test:a11y',
  'test:links',
  'validate:tests',
];

console.log('\nChecking package.json scripts:');
for (const script of requiredScripts) {
  const exists = packageJson.scripts && packageJson.scripts[script];
  console.log(`${exists ? '✓' : '✗'} ${script}`);
  if (!exists) allValid = false;
}

// Check dependencies
const requiredDeps = [
  'vitest',
  '@playwright/test',
  'jsdom',
  'cheerio',
  '@axe-core/playwright',
  'linkinator',
  'pa11y-ci',
];

console.log('\nChecking devDependencies:');
for (const dep of requiredDeps) {
  const exists = packageJson.devDependencies && packageJson.devDependencies[dep];
  console.log(`${exists ? '✓' : '✗'} ${dep}`);
  if (!exists) allValid = false;
}

console.log(
  '\n' +
    (allValid
      ? '✅ All validation checks passed'
      : '❌ Some validation checks failed')
);

process.exit(allValid ? 0 : 1);
```

## Step 3: Update Main README

**Add this section to `README.md`** after the "Development & Build" section (around line 104):

```markdown
---

## 🧪 Testing

The project includes a comprehensive testing suite:

```bash
# Run all tests
pnpm run test:all

# Run specific test suites
pnpm run test:unit          # Fast unit tests
pnpm run test:integration   # Integration tests (requires build)
pnpm run test:e2e          # End-to-end tests (requires build)

# Additional checks
pnpm run test:a11y         # Accessibility audit
pnpm run test:links        # Check for broken links
```

See [docs/testing-guide.md](docs/testing-guide.md) for detailed testing documentation.

---
```

## Step 4: Create scripts directory if needed

```bash
mkdir -p scripts
```

## Verification

Run these commands to verify everything:

```bash
# 1. Run validation script
pnpm run validate:tests

# 2. Check all test commands exist
pnpm run test:unit --help
pnpm run test:integration --help
pnpm run test:e2e --help

# 3. Verify documentation exists
cat docs/testing-guide.md

# 4. Check README was updated
grep -A 5 "## 🧪 Testing" README.md
```

## Success Criteria

✅ `docs/testing-guide.md` created with complete documentation  
✅ `scripts/validate-tests.js` created and executable  
✅ `README.md` updated with testing section  
✅ Validation script runs successfully  
✅ All validation checks pass  
✅ Documentation is clear and accurate  

## Expected Output

When you run `pnpm run validate:tests`, you should see:

```
Validating test setup...

✓ vitest.config.unit.ts
✓ vitest.config.integration.ts
✓ playwright.config.ts
✓ .pa11yci.json
✓ .linkinator.config.json
✓ tests/setup/unit.setup.ts
✓ tests/setup/integration.setup.ts
✓ tests/helpers/test-utils.ts
✓ tests/unit/pagination.test.ts
✓ tests/unit/sorting.test.ts
✓ tests/unit/dom-guards.test.ts
✓ tests/integration/home-page.test.ts
✓ tests/integration/gallery-page.test.ts
✓ tests/integration/book-page.test.ts
✓ tests/integration/dom-interactions.test.ts
✓ tests/e2e/language-navigation.spec.ts
✓ tests/e2e/gallery-interactions.spec.ts
✓ tests/e2e/search.spec.ts
✓ tests/e2e/accessibility.spec.ts
✓ .github/workflows/test.yml
✓ .github/workflows/accessibility.yml
✓ docs/testing-guide.md

✓ All test files present

Checking package.json scripts:
✓ test
✓ test:unit
✓ test:integration
✓ test:e2e
✓ test:a11y
✓ test:links
✓ validate:tests

Checking devDependencies:
✓ vitest
✓ @playwright/test
✓ jsdom
✓ cheerio
✓ @axe-core/playwright
✓ linkinator
✓ pa11y-ci

✅ All validation checks passed
```

## Troubleshooting

**Validation script fails to run**:
- Ensure Node.js is installed
- Check file permissions: `chmod +x scripts/validate-tests.js`
- Run directly: `node scripts/validate-tests.js`

**Missing files reported**:
- Review previous tasks
- Check file paths are correct
- Verify all files were created

**README merge conflicts**:
- Read existing README first
- Find appropriate location for testing section
- Don't remove existing content
- Add testing section after "Development & Build"

## Final Verification

After completing this task, run the full verification:

```bash
# 1. Validate test setup
pnpm run validate:tests

# 2. Run all tests
pnpm run test:unit
pnpm run build
pnpm run test:integration
pnpm run test:e2e

# 3. Check documentation
cat docs/testing-guide.md
grep "Testing" README.md
```

## Completion

This is the final task! After completing this:

1. All test infrastructure is in place
2. All tests are documented
3. CI/CD is configured
4. Validation script confirms everything

You can now commit all changes with the final commit message below.

## Commit Message

```
feat(testing): add documentation and validation

- Create comprehensive testing guide
- Add validation script to verify test setup
- Update README with testing section
- Document all test commands and workflows
- Provide troubleshooting guidance

Part 6/6 of testing implementation - COMPLETE
```

## Summary of Complete Implementation

After all 6 tasks, you should have:

**Configuration** (Task 1):
- 5 config files
- 13 new npm scripts
- 10+ dependencies installed

**Unit Tests** (Task 2):
- 3 unit test files
- 2 setup files
- 1 helpers file
- ~35 unit tests

**Integration Tests** (Task 3):
- 4 integration test files
- ~27 integration tests

**E2E Tests** (Task 4):
- 4 E2E test files
- ~15 end-to-end tests

**CI/CD** (Task 5):
- 2 GitHub Actions workflows
- Automated testing on push/PR

**Documentation** (Task 6):
- Testing guide
- Validation script
- Updated README

**Total**: 22+ new files, comprehensive test coverage, full CI/CD integration!

