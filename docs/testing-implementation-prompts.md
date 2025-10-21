# Testing Implementation Prompts

This file contains prompts for each of the 6 testing implementation tasks. Send these prompts to your AI coding agent (ChatGPT Codex, Cursor Agent, etc.) one task at a time.

**Important**: Complete tasks in order (1→2→3→4→5→6). Each task builds on previous tasks.

---

## 📋 TASK 1: Setup & Configuration

**Prompt to send:**

```
Task: Testing Setup & Configuration (Part 1/6)

Read and implement: docs/testing-task-1-setup.md
Context: docs/testing-context.md

Objective: Install all testing dependencies and create configuration files for Vitest, Playwright, Pa11y, and Linkinator.

What to do:
1. Install 12 testing packages using pnpm
2. Add 13 test scripts to package.json (MERGE with existing, don't replace)
3. Create 5 configuration files:
   - vitest.config.unit.ts
   - vitest.config.integration.ts
   - playwright.config.ts
   - .pa11yci.json
   - .linkinator.config.json

Success criteria:
- All dependencies install without errors
- package.json has all new test scripts
- All 5 config files created
- TypeScript compiles without errors (pnpm exec tsc --noEmit)
- No existing package.json scripts were removed

Verification commands:
pnpm list vitest playwright
pnpm exec tsc --noEmit
ls -la vitest.config.unit.ts vitest.config.integration.ts playwright.config.ts

After completion, commit with message from the task document.

Critical: When updating package.json, READ it first and MERGE new scripts. Do NOT replace existing scripts.
```

---

## 📋 TASK 2: Unit Tests

**Prompt to send (after Task 1 completes):**

```
Task: Unit Tests (Part 2/6)

Read and implement: docs/testing-task-2-unit.md
Context: docs/testing-context.md
Prerequisites: Task 1 completed

Objective: Create unit tests for pagination logic, sorting logic, and DOM guard clauses.

What to do:
1. Create directory structure: tests/setup/, tests/helpers/, tests/unit/
2. Create 2 setup files (unit.setup.ts, integration.setup.ts)
3. Create test helpers (test-utils.ts)
4. Create 3 unit test files:
   - pagination.test.ts (15 tests)
   - sorting.test.ts (12 tests)
   - dom-guards.test.ts (8 tests)

Success criteria:
- All 6 files created in correct locations
- Unit tests run successfully: pnpm run test:unit
- All tests pass or show meaningful results
- No TypeScript compilation errors
- Tests are independent (can run in any order)

Verification commands:
pnpm run test:unit
ls -R tests/
pnpm exec tsc --noEmit

Expected: ~35 unit tests pass

After completion, commit with message from the task document.
```

---

## 📋 TASK 3: Integration Tests

**Prompt to send (after Task 2 completes):**

```
Task: Integration Tests (Part 3/6)

Read and implement: docs/testing-task-3-integration.md
Context: docs/testing-context.md
Prerequisites: Tasks 1-2 completed, site must be built

Objective: Create integration tests that validate Hugo-generated HTML structure.

IMPORTANT: Before starting, run: pnpm run build

What to do:
1. Create tests/integration/ directory
2. Create 4 integration test files:
   - home-page.test.ts
   - gallery-page.test.ts (tests en/ru/fa languages)
   - book-page.test.ts
   - dom-interactions.test.ts

Success criteria:
- All 4 integration test files created
- Site builds successfully (public/ directory exists)
- Integration tests run: pnpm run test:integration
- Tests find expected HTML elements
- No TypeScript compilation errors

Verification commands:
pnpm run build
pnpm run test:integration
ls tests/integration/

Expected: ~27 integration tests pass

After completion, commit with message from the task document.

Note: Integration tests require public/ directory. If tests fail with "file not found", run pnpm run build first.
```

---

## 📋 TASK 4: E2E Tests

**Prompt to send (after Task 3 completes):**

```
Task: End-to-End Tests (Part 4/6)

Read and implement: docs/testing-task-4-e2e.md
Context: docs/testing-context.md
Prerequisites: Tasks 1-3 completed

Objective: Create E2E tests that simulate real user interactions in a browser.

IMPORTANT: Before starting, run:
pnpm run playwright:install
pnpm run build

What to do:
1. Create tests/e2e/ directory
2. Create 4 E2E test files:
   - language-navigation.spec.ts (4 tests)
   - gallery-interactions.spec.ts (5 tests)
   - search.spec.ts (3 tests)
   - accessibility.spec.ts (4 tests)

Success criteria:
- All 4 E2E test files created
- Playwright browsers installed successfully
- Site is built (public/ exists)
- E2E tests launch browser and execute: pnpm run test:e2e
- Tests navigate through pages successfully
- No TypeScript compilation errors

Verification commands:
pnpm run playwright:install
pnpm run build
pnpm run test:e2e

Expected: ~15 E2E tests execute (browser opens and tests run)

After completion, commit with message from the task document.

Note: Tests use real Chromium browser. First run may be slower while browsers download.
```

---

## 📋 TASK 5: CI/CD Workflows

**Prompt to send (after Task 4 completes):**

```
Task: CI/CD Workflows (Part 5/6)

Read and implement: docs/testing-task-5-ci.md
Context: docs/testing-context.md
Prerequisites: Tasks 1-4 completed (all tests working locally)

Objective: Create GitHub Actions workflows to automatically run tests on every push and PR.

What to do:
1. Create .github/workflows/ directory
2. Create 2 workflow files:
   - test.yml (main testing workflow)
   - accessibility.yml (accessibility audit workflow)

Success criteria:
- Both workflow files created in .github/workflows/
- YAML syntax is valid (no tabs, correct indentation)
- All referenced scripts exist in package.json
- Workflows will trigger on correct branches
- Proper caching configured

Verification commands:
cat .github/workflows/test.yml
cat .github/workflows/accessibility.yml
ls -la .github/workflows/
grep -E "(test:unit|test:integration|test:e2e)" package.json

After completion, commit with message from the task document.

Note: Workflows will run automatically when pushed to GitHub. Use spaces for YAML indentation, not tabs.
```

---

## 📋 TASK 6: Documentation & Validation

**Prompt to send (after Task 5 completes - FINAL TASK):**

```
Task: Documentation & Validation (Part 6/6 - FINAL)

Read and implement: docs/testing-task-6-docs.md
Context: docs/testing-context.md
Prerequisites: Tasks 1-5 completed

Objective: Create comprehensive documentation and validation script. This completes the testing implementation.

What to do:
1. Create docs/testing-guide.md (comprehensive testing documentation)
2. Create scripts/validate-tests.js (validation script)
3. Update README.md with testing section (MERGE, don't replace existing content)

Success criteria:
- docs/testing-guide.md created with complete documentation
- scripts/validate-tests.js created
- README.md updated with testing section (around line 104)
- Validation script runs: pnpm run validate:tests
- All validation checks pass
- Documentation is clear and accurate

Verification commands:
pnpm run validate:tests
cat docs/testing-guide.md
grep -A 5 "Testing" README.md

Expected validation output: All checks show ✓ (green checkmarks)

After completion, commit with message from the task document.

This is the FINAL task. After completion, the entire testing implementation is done!

Final verification:
pnpm run validate:tests
pnpm run test:unit
pnpm run build
pnpm run test:integration
pnpm run test:e2e

All commands should work successfully.
```

---

## 📊 Task Summary

| Task | Focus | Files Created | Est. Time |
|------|-------|---------------|-----------|
| 1 | Setup & Config | 5 configs | 20-30 min |
| 2 | Unit Tests | 6 test files | 30-40 min |
| 3 | Integration Tests | 4 test files | 30-40 min |
| 4 | E2E Tests | 4 test files | 30-40 min |
| 5 | CI/CD | 2 workflows | 15-20 min |
| 6 | Documentation | 3 docs | 20-25 min |
| **Total** | **Complete Suite** | **22+ files** | **~2.5 hours** |

---

## 🎯 Quick Reference

### Order of Execution
1. Task 1 → Install deps & configs
2. Task 2 → Unit tests
3. Task 3 → Integration tests (requires build)
4. Task 4 → E2E tests (requires Playwright)
5. Task 5 → CI/CD workflows
6. Task 6 → Documentation (final)

### Key Points for AI Agent

- **Task 1**: MERGE package.json scripts, don't replace existing ones
- **Task 2**: Tests must be independent, no shared state
- **Task 3**: Must run `pnpm run build` before tests
- **Task 4**: Must run `pnpm run playwright:install` first
- **Task 5**: Use spaces in YAML, not tabs
- **Task 6**: MERGE README.md, don't replace content

### Between Tasks

After each task:
1. Verify success criteria met
2. Commit with provided message
3. Run verification commands
4. Proceed to next task if all checks pass

### Final Success

After Task 6, you should have:
- ✅ All dependencies installed
- ✅ 22+ files created
- ✅ 3 test tiers (unit, integration, E2E)
- ✅ CI/CD workflows
- ✅ Complete documentation
- ✅ Validation passing

---

## 🚨 Important Reminders

1. **Read context first**: Always start by reading `docs/testing-context.md`
2. **Follow task order**: Tasks build on each other - do them sequentially
3. **Read task files**: Each task has detailed instructions in its file
4. **Merge, don't replace**: When editing package.json or README.md
5. **Build before integration/E2E**: These tests need `public/` directory
6. **Independent tests**: Each test must run in isolation
7. **Commit after each task**: Use provided commit messages

---

## 📝 Usage Example

```bash
# Send Task 1 prompt to AI agent
# Wait for completion
# Verify with: pnpm run test:unit --help

# Send Task 2 prompt to AI agent
# Wait for completion
# Verify with: pnpm run test:unit

# Send Task 3 prompt to AI agent
# (and so on...)
```

Good luck! 🚀

