# Task 5: CI/CD Workflows

**Estimated Time**: 15-20 minutes  
**Prerequisites**: Tasks 1-4 completed (all tests working locally)  
**Context**: Read `docs/testing-context.md` first

## Objective

Create GitHub Actions workflows to automatically run tests on every push and pull request. This ensures tests run in CI and catch regressions before they reach production.

## What You'll Create

- Main testing workflow (runs all tests)
- Accessibility audit workflow (separate, can fail without blocking)
- Total: 2 workflow files in `.github/workflows/`

## Step 1: Create Workflows Directory

```bash
mkdir -p .github/workflows
```

## Step 2: Create Main Test Workflow

**File**: `.github/workflows/test.yml`

```yaml
name: Testing Suite

on:
  push:
    branches: [main, preview, develop]
  pull_request:
    branches: [main, preview]

jobs:
  test:
    name: Run Tests
    runs-on: ubuntu-latest
    timeout-minutes: 20

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Setup pnpm
        uses: pnpm/action-setup@v2
        with:
          version: 8

      - name: Get pnpm store directory
        id: pnpm-cache
        shell: bash
        run: |
          echo "STORE_PATH=$(pnpm store path)" >> $GITHUB_OUTPUT

      - name: Setup pnpm cache
        uses: actions/cache@v3
        with:
          path: ${{ steps.pnpm-cache.outputs.STORE_PATH }}
          key: ${{ runner.os }}-pnpm-store-${{ hashFiles('**/pnpm-lock.yaml') }}
          restore-keys: |
            ${{ runner.os }}-pnpm-store-

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Setup Hugo
        uses: peaceiris/actions-hugo@v2
        with:
          hugo-version: 'latest'
          extended: true

      - name: Cache Hugo resources
        uses: actions/cache@v3
        with:
          path: resources
          key: ${{ runner.os }}-hugo-resources-${{ hashFiles('content/**') }}
          restore-keys: |
            ${{ runner.os }}-hugo-resources-

      - name: Run unit tests
        run: pnpm run test:unit

      - name: Build site for integration tests
        run: pnpm run build
        env:
          NODE_ENV: test

      - name: Run integration tests
        run: pnpm run test:integration

      - name: Install Playwright browsers
        run: pnpm exec playwright install --with-deps chromium

      - name: Run E2E tests
        run: pnpm run test:e2e

      - name: Run link checker
        run: pnpm run test:links
        continue-on-error: true

      - name: Upload Playwright report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 7

      - name: Upload test coverage
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: coverage
          path: coverage/
          retention-days: 7
```

## Step 3: Create Accessibility Workflow

**File**: `.github/workflows/accessibility.yml`

```yaml
name: Accessibility Check

on:
  push:
    branches: [main, preview]
  pull_request:
    branches: [main]

jobs:
  a11y:
    name: Accessibility Audit
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '18'

      - uses: pnpm/action-setup@v2
        with:
          version: 8

      - run: pnpm install --frozen-lockfile

      - name: Setup Hugo
        uses: peaceiris/actions-hugo@v2
        with:
          hugo-version: 'latest'
          extended: true

      - name: Build site
        run: pnpm run build

      - name: Run Pa11y CI
        run: pnpm run test:a11y
        continue-on-error: true
```

## Verification

After creating the workflows, verify:

```bash
# Check YAML syntax is valid
cat .github/workflows/test.yml
cat .github/workflows/accessibility.yml

# Verify files exist
ls -la .github/workflows/

# Optional: Use yamllint if available
# yamllint .github/workflows/test.yml
```

## Understanding the Workflows

### Main Test Workflow (`test.yml`)

**Triggers**:
- Pushes to `main`, `preview`, `develop` branches
- Pull requests to `main`, `preview` branches

**Steps**:
1. Checkout code
2. Setup Node.js 18 and pnpm 8
3. Cache pnpm store for faster installs
4. Install dependencies
5. Setup Hugo (extended version)
6. Cache Hugo resources
7. **Run unit tests** (fast, no build needed)
8. **Build site** (required for integration/E2E)
9. **Run integration tests**
10. Install Playwright browsers
11. **Run E2E tests**
12. Run link checker (won't fail build)
13. Upload test reports as artifacts

**Key Features**:
- Caching for faster runs (pnpm store, Hugo resources)
- Artifacts uploaded for debugging
- Link checker doesn't fail build (`continue-on-error: true`)
- 20-minute timeout to prevent hanging

### Accessibility Workflow (`accessibility.yml`)

**Triggers**:
- Pushes to `main`, `preview` branches
- Pull requests to `main` branch

**Steps**:
1. Checkout code
2. Setup environment
3. Build site
4. Run Pa11y accessibility audit

**Key Features**:
- Separate from main tests (can fail independently)
- Uses `continue-on-error` so it reports but doesn't block
- Shorter timeout (10 minutes)

## Success Criteria

✅ Both workflow files created in `.github/workflows/`  
✅ YAML syntax is valid (no tabs, correct indentation)  
✅ All referenced scripts exist in package.json  
✅ Workflows will trigger on correct branches  
✅ Proper caching configured  

## Testing CI Workflows

**Local validation**:
```bash
# Check YAML is valid
python -c "import yaml; yaml.safe_load(open('.github/workflows/test.yml'))"

# Verify referenced scripts exist
grep -E "(test:unit|test:integration|test:e2e|test:links|test:a11y)" package.json
```

**After pushing to GitHub**:
1. Go to your repository on GitHub
2. Click "Actions" tab
3. You should see workflows running
4. Click on a workflow run to see details
5. Verify all steps complete successfully

## Troubleshooting

**YAML syntax errors**:
- Use spaces, not tabs for indentation
- Check all colons have space after them
- Verify nested structure is correct
- Use online YAML validator if needed

**Workflow doesn't trigger**:
- Check branch names match your repository
- Verify `.github/workflows/` path is correct
- Ensure files are committed and pushed

**Steps fail in CI but work locally**:
- Check Node.js version matches (18)
- Verify all dependencies are in package.json
- Check environment differences (CI uses Ubuntu)
- Look at failed step logs in Actions tab

**Playwright fails in CI**:
- Workflow includes `--with-deps` flag (installs system dependencies)
- Uses `chromium` only (faster than all browsers)
- Runs on Ubuntu (has required libraries)

## Next Task

After this task completes successfully, proceed to **Task 6: Documentation & Validation** (`docs/testing-task-6-docs.md`).

## Commit Message

```
feat(testing): add CI/CD workflows for automated testing

- Create main testing workflow for GitHub Actions
- Add accessibility audit workflow
- Configure caching for pnpm and Hugo
- Upload test artifacts for debugging
- Run tests on push and pull requests

Part 5/6 of testing implementation
```

