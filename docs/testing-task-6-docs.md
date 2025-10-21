# Task 6: Documentation & Validation

**Estimated Time**: 15-20 minutes  
**Prerequisites**: Tasks 1-5 completed (all files created)  
**Context**: Read `docs/testing-context.md` first

## Objective

Create testing documentation and a validation script. This is the final task that completes the testing implementation. This task only creates files.

## Important Note

⚠️ **This task runs in an isolated VM environment**. Do NOT run `pnpm install` or `pnpm run validate:tests`. Only create documentation files and the validation script.

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

After completing all steps, verify files were created:

```bash
# Verify files exist
ls docs/testing-guide.md
ls scripts/validate-tests.js
grep -A 5 "## 🧪 Testing" README.md

# Check scripts directory was created
ls scripts/
```

## Success Criteria

✅ `docs/testing-guide.md` created with complete documentation  
✅ `scripts/validate-tests.js` created with validation logic  
✅ `README.md` updated with testing section (around line 104)  
✅ Scripts directory exists  
✅ Documentation is clear and accurate  

## Important Notes

⚠️ **Do NOT run these commands** (they won't work in isolated VM):
- ❌ `pnpm install`
- ❌ `pnpm run validate:tests`
- ❌ `node scripts/validate-tests.js`

✅ **Only verify files were created** using `ls` and `grep` commands shown above.

## Troubleshooting

**Cannot run validation script**:
- That's expected - script will be run after all tasks complete
- Focus on creating the file with correct content

**Worried about README merge**:
- READ existing README.md content first
- Find the "Development & Build" section
- Add testing section AFTER it, around line 104
- Do NOT remove or modify existing content

**Scripts directory doesn't exist**:
- Create it: `mkdir -p scripts`
- Then add the validation script file

## Completion

🎉 **This is the FINAL task!** After completing this, all 22+ test files are created.

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

## Summary of Files Created (All 6 Tasks)

After all 6 tasks complete, you should have created:

**Configuration** (Task 1):
- 5 config files (vitest x2, playwright, pa11y, linkinator)
- Updated package.json (13 scripts, 12 dependencies)

**Test Files** (Tasks 2-4):
- 2 setup files
- 1 helpers file
- 3 unit test files (~35 tests)
- 4 integration test files (~27 tests)
- 4 E2E test files (~15 tests)

**CI/CD** (Task 5):
- 2 GitHub Actions workflow files

**Documentation** (Task 6):
- Testing guide
- Validation script
- Updated README

**Total**: 22+ new files created!

---

## 🚀 NEXT STEPS FOR HUMAN (After All 6 Tasks)

After all tasks are committed to the repository, a human must run these commands to actually install dependencies and run tests:

```bash
# 1. Pull all committed changes
git pull

# 2. Install all testing dependencies
pnpm install

# 3. Validate test setup
pnpm run validate:tests

# 4. Install Playwright browsers
pnpm run playwright:install

# 5. Run unit tests (fast, no build needed)
pnpm run test:unit

# 6. Build the Hugo site
pnpm run build

# 7. Run integration tests (requires build)
pnpm run test:integration

# 8. Run E2E tests (requires build)
pnpm run test:e2e

# 9. Optional: Run all tests together
pnpm run test:all
```

### Expected Results

**Validation** (`pnpm run validate:tests`):
- All 22+ files should show ✓
- All package.json scripts should show ✓
- All devDependencies should show ✓

**Unit Tests** (`pnpm run test:unit`):
- ~35 tests should pass
- Should complete in <5 seconds

**Integration Tests** (`pnpm run test:integration`):
- ~27 tests should pass
- Requires `public/` directory from build

**E2E Tests** (`pnpm run test:e2e`):
- ~15 tests should execute
- Browser should launch and navigate pages
- May take 30-60 seconds

**GitHub Actions**:
- After pushing to GitHub, check Actions tab
- Workflows should run automatically
- All steps should complete successfully

---

## 🐛 If Tests Fail

**Unit test failures**:
- Check TypeScript compilation: `pnpm exec tsc --noEmit`
- Verify all imports resolve correctly
- Review test logic against actual code

**Integration test failures**:
- Ensure site built: `ls public/en/main/index.html`
- Check Hugo build had no errors
- Verify selectors match actual HTML structure

**E2E test failures**:
- Check site structure matches expectations
- Verify selectors in tests match actual elements
- Use `pnpm run test:e2e:ui` to debug visually
- Check browser console for errors

**CI workflow failures**:
- Review GitHub Actions logs
- Check all scripts exist in package.json
- Verify branch names match workflow triggers

---

## 📝 Implementation Complete

All 6 tasks are now done! The testing infrastructure is fully implemented and ready to use once dependencies are installed and tests are run by a human.

