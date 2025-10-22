# Task 1: Configuration Files

**Estimated Time**: 15-20 minutes  
**Prerequisites**: None  
**Context**: Read `docs/testing-context.md` first

## Objective

Create all configuration files and update package.json with test scripts and dependencies. This task only creates/modifies files - no installation or test execution.

## What You'll Create

- Update `package.json` (add scripts and devDependencies)
- Create 5 configuration files
- Total: 6 files created/modified


## Step 1: Update package.json Scripts AND Dependencies

**CRITICAL**: Read existing `package.json` first, then MERGE these additions. Do NOT replace existing content.

**Add to `scripts` section:**

```json
{
  "test": "vitest run",
  "test:watch": "vitest",
  "test:ui": "vitest --ui",
  "test:unit": "vitest run --config vitest.config.unit.ts",
  "test:integration": "vitest run --config vitest.config.integration.ts",
  "test:e2e": "playwright test",
  "test:e2e:ui": "playwright test --ui",
  "test:e2e:debug": "playwright test --debug",
  "test:a11y": "pa11y-ci",
  "test:links": "linkinator public --recurse --skip 'fonts|.css|.js' --verbosity error",
  "test:all": "pnpm run test:unit && pnpm run build && pnpm run test:integration && pnpm run test:e2e && pnpm run test:links",
  "playwright:install": "playwright install --with-deps chromium",
  "validate:tests": "node scripts/validate-tests.js"
}
```

**Add to `devDependencies` section:**

```json
{
  "vitest": "^1.0.0",
  "@vitest/ui": "^1.0.0",
  "jsdom": "^23.0.0",
  "cheerio": "^1.0.0-rc.12",
  "@playwright/test": "^1.40.0",
  "@axe-core/playwright": "^4.8.0",
  "happy-dom": "^12.10.0",
  "@testing-library/dom": "^9.3.3",
  "linkinator": "^6.0.0",
  "pa11y-ci": "^3.0.0",
  "glob": "^10.3.0",
  "@types/glob": "^8.1.0"
}
```

**What each package does**:
- `vitest` + `@vitest/ui`: Test runner with UI
- `jsdom`: DOM simulation for Node
- `cheerio`: HTML parsing
- `@playwright/test`: E2E browser testing
- `@axe-core/playwright`: Accessibility testing
- `linkinator`, `pa11y-ci`: Site quality checks
- `glob`: File pattern matching

## Step 2: Create Vitest Unit Config

**File**: `vitest.config.unit.ts`

**Important**: Check `tsconfig.json` for existing path aliases and use them.

```typescript
import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  test: {
    name: 'unit',
    environment: 'jsdom',
    include: ['tests/unit/**/*.test.ts'],
    exclude: ['**/node_modules/**', '**/dist/**', '**/public/**'],
    globals: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      include: ['assets/js/**/*.ts', 'src/**/*.ts'],
      exclude: ['**/*.test.ts', '**/vendor/**', '**/*.d.ts'],
    },
    setupFiles: ['./tests/setup/unit.setup.ts'],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './assets'),
      '@src': path.resolve(__dirname, './src'),
    },
  },
});
```

## Step 3: Create Vitest Integration Config

**File**: `vitest.config.integration.ts`

```typescript
import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  test: {
    name: 'integration',
    environment: 'jsdom',
    include: ['tests/integration/**/*.test.ts'],
    exclude: ['**/node_modules/**', '**/dist/**'],
    globals: true,
    testTimeout: 10000,
    setupFiles: ['./tests/setup/integration.setup.ts'],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './assets'),
      '@src': path.resolve(__dirname, './src'),
    },
  },
});
```

## Step 4: Create Playwright Config

**File**: `playwright.config.ts`

```typescript
import { defineConfig, devices } from '@playwright/test';

const PORT = process.env.PORT || 4173;
const BASE_URL = process.env.BASE_URL || `http://localhost:${PORT}`;

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: process.env.CI ? 'github' : 'html',

  use: {
    baseURL: BASE_URL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  webServer: {
    command: 'npx http-server public -p 4173 --silent',
    port: 4173,
    timeout: 120000,
    reuseExistingServer: !process.env.CI,
  },
});
```

## Step 5: Create Pa11y Config

**File**: `.pa11yci.json`

```json
{
  "defaults": {
    "standard": "WCAG2AA",
    "timeout": 10000,
    "wait": 1000,
    "chromeLaunchConfig": {
      "args": ["--no-sandbox", "--disable-setuid-sandbox"]
    }
  },
  "urls": [
    "public/index.html",
    "public/en/index.html",
    "public/ru/index.html",
    "public/fa/index.html",
    "public/en/main/index.html"
  ]
}
```

## Step 6: Create Linkinator Config

**File**: `.linkinator.config.json`

```json
{
  "path": "public",
  "recurse": true,
  "skip": [
    "fonts",
    ".css$",
    ".js$",
    ".woff2$",
    "admin/*"
  ],
  "silent": false,
  "verbosity": "error"
}
```

## Verification

After completing all steps, run:

```bash
# Check all files exist
ls -la vitest.config.unit.ts vitest.config.integration.ts playwright.config.ts .pa11yci.json .linkinator.config.json

# Verify package.json was updated
grep "test:" package.json
grep "vitest" package.json

# Optional: Install dependencies and verify TypeScript
pnpm install
pnpm exec tsc --noEmit
```

## Success Criteria

✅ package.json has all new test scripts in `scripts` section  
✅ package.json has all new dependencies in `devDependencies` section  
✅ All 5 config files created with correct content  
✅ No existing scripts or dependencies in package.json were removed  
✅ TypeScript compilation succeeds (no errors)  

## Troubleshooting

**pnpm install fails**:
- Check Node.js version: `node --version` (need ≥18)
- Try: `pnpm install --shamefully-hoist`

**TypeScript errors in configs**:
- Verify vitest is installed: `pnpm list vitest`
- Check path aliases match tsconfig.json
- Ensure @playwright/test is installed

**Path alias errors**:
- Read tsconfig.json to see existing aliases
- Update vitest configs to match

## Next Task

After this task completes successfully, proceed to **Task 2: Unit Tests** (`docs/testing-task-2-unit.md`).

## Commit Message

```
feat(testing): add testing configuration files

- Add testing dependencies to package.json devDependencies
- Add test scripts to package.json (unit, integration, e2e, a11y, links)
- Create Vitest configs for unit and integration tests
- Create Playwright config for E2E tests
- Add Pa11y and Linkinator configs
- Configure test environments and path aliases

Part 1/6 of testing implementation
```

