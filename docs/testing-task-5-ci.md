# Task 5: CI/CD Workflows

**Estimated Time**: 10-15 minutes  
**Prerequisites**: Tasks 1-4 completed (all test files created)  
**Context**: Read `docs/testing-context.md` first

## Objective

Create GitHub Actions workflow files to automatically run tests on every push and pull request. This task only creates files - workflows will run automatically when pushed to GitHub.

## Important Note

⚠️ **This task runs in an isolated VM environment**. Only create workflow files. No local testing is possible - workflows activate when code is pushed to GitHub.

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

After creating the workflows, verify files were created:

```bash
# Verify files exist
ls -la .github/workflows/

# Check files exist
ls .github/workflows/test.yml
ls .github/workflows/accessibility.yml

# Verify YAML content is present
cat .github/workflows/test.yml | head -20
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
✅ Files use spaces for indentation (not tabs)  
✅ Workflows reference correct branches  
✅ All workflow steps are properly formatted  

## Important Notes

⚠️ **Do NOT run these commands** (workflows only run in GitHub):
- ❌ Local workflow testing
- ❌ YAML validation with Python/yamllint (may not be installed)

✅ **Only verify files were created** using `ls` and `cat` commands shown above.

✅ **Workflows will be tested** when code is pushed to GitHub and Actions run automatically.

## Understanding How Workflows Activate

**After all 6 tasks complete and code is pushed to GitHub**:
1. Go to your repository on GitHub
2. Click "Actions" tab
3. Workflows will appear and run automatically
4. Click on a workflow run to see details
5. All steps should complete successfully (after `pnpm install` runs in CI)

## Troubleshooting

**YAML indentation concerns**:
- Use 2 spaces for each indentation level
- No tabs allowed in YAML
- Colons must have space after them
- Focus on exact content match from this document

**Worried about workflow failures**:
- Workflows install dependencies themselves in CI
- They have access to `node_modules/` in GitHub Actions
- First run might take longer while caching builds up

**Branch name concerns**:
- Workflow uses `main`, `preview`, `develop` branches
- Adjust branch names if your repo uses different names

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

