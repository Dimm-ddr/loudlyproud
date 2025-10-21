# Testing Implementation Prompts

This file contains prompts for each of the 6 testing implementation tasks. Send these prompts to your AI coding agent (ChatGPT Codex, Cursor Agent, etc.) one task at a time.

**Important**: Complete tasks in order (1→2→3→4→5→6). Each task builds on previous tasks.

---

## 📋 TASK 1: Configuration Files

**Prompt to send:**

```
Task: Configuration Files (Part 1/6)

Read and implement: docs/testing-task-1-setup.md
Context: docs/testing-context.md

⚠️ IMPORTANT: This task runs in an isolated VM. Only CREATE FILES. Do NOT run pnpm install, pnpm build, or any test commands.

Objective: Create configuration files and update package.json with test scripts and dependencies.

What to do:
1. Update package.json (MERGE, don't replace):
   - Add 13 test scripts to "scripts" section
   - Add 12 dependencies to "devDependencies" section
2. Create 5 configuration files:
   - vitest.config.unit.ts
   - vitest.config.integration.ts
   - playwright.config.ts
   - .pa11yci.json
   - .linkinator.config.json

Success criteria:
- package.json updated (scripts AND devDependencies added)
- All 5 config files created with exact content from task doc
- No existing package.json content was removed
- Files use correct syntax (TypeScript/JSON)

Verification commands (files only):
ls -la vitest.config.unit.ts vitest.config.integration.ts playwright.config.ts .pa11yci.json .linkinator.config.json
grep "test:" package.json
grep "vitest" package.json

After completion, commit with message from the task document.

Critical: READ existing package.json first, then MERGE new content. Do NOT replace existing content.
```

---

## 📋 TASK 2: Test Setup & Unit Tests

**Prompt to send (after Task 1 completes):**

```
Task: Test Setup & Unit Tests (Part 2/6)

Read and implement: docs/testing-task-2-unit.md
Context: docs/testing-context.md
Prerequisites: Task 1 completed (config files created)

⚠️ IMPORTANT: This task runs in an isolated VM. Only CREATE FILES. Do NOT run pnpm install or pnpm run test:unit.

Objective: Create test setup files, helper utilities, and unit test files.

What to do:
1. Create directory structure: tests/setup/, tests/helpers/, tests/unit/
2. Create 2 setup files (unit.setup.ts, integration.setup.ts)
3. Create test helpers (test-utils.ts)
4. Create 3 unit test files:
   - pagination.test.ts (~15 tests)
   - sorting.test.ts (~12 tests)
   - dom-guards.test.ts (~8 tests)

Success criteria:
- All 6 files created in correct locations
- Directory structure is correct
- Files contain complete test code as specified
- TypeScript syntax is valid (no obvious syntax errors)
- Tests use proper Vitest imports and structure

Verification commands (files only):
ls -R tests/
ls tests/setup/unit.setup.ts tests/setup/integration.setup.ts
ls tests/helpers/test-utils.ts
ls tests/unit/pagination.test.ts tests/unit/sorting.test.ts tests/unit/dom-guards.test.ts

After completion, commit with message from the task document.
```

---

## 📋 TASK 3: Integration Tests

**Prompt to send (after Task 2 completes):**

```
Task: Integration Tests (Part 3/6)

Read and implement: docs/testing-task-3-integration.md
Context: docs/testing-context.md
Prerequisites: Tasks 1-2 completed (config and unit test files created)

⚠️ IMPORTANT: This task runs in an isolated VM. Only CREATE FILES. Do NOT run pnpm build or pnpm run test:integration.

Objective: Create integration test files that validate Hugo-generated HTML structure.

What to do:
1. Create tests/integration/ directory
2. Create 4 integration test files:
   - home-page.test.ts
   - gallery-page.test.ts (tests en/ru/fa languages)
   - book-page.test.ts
   - dom-interactions.test.ts

Success criteria:
- All 4 integration test files created
- Files are in tests/integration/ directory
- Files contain complete test code as specified
- Tests use Cheerio and jsdom correctly
- Tests reference readBuiltPage from setup file

Verification commands (files only):
ls tests/integration/
ls tests/integration/home-page.test.ts tests/integration/gallery-page.test.ts
ls tests/integration/book-page.test.ts tests/integration/dom-interactions.test.ts

After completion, commit with message from the task document.

Note: Tests will be executed later after site is built. Focus on creating files with correct content.
```

---

## 📋 TASK 4: E2E Tests

**Prompt to send (after Task 3 completes):**

```
Task: End-to-End Tests (Part 4/6)

Read and implement: docs/testing-task-4-e2e.md
Context: docs/testing-context.md
Prerequisites: Tasks 1-3 completed (config and test files created)

⚠️ IMPORTANT: This task runs in an isolated VM. Only CREATE FILES. Do NOT run pnpm run playwright:install or pnpm run test:e2e.

Objective: Create E2E test files that will simulate real user interactions in a browser.

What to do:
1. Create tests/e2e/ directory
2. Create 4 E2E test files:
   - language-navigation.spec.ts (~4 tests)
   - gallery-interactions.spec.ts (~5 tests)
   - search.spec.ts (~3 tests)
   - accessibility.spec.ts (~4 tests)

Success criteria:
- All 4 E2E test files created
- Files are in tests/e2e/ directory
- Files use .spec.ts extension (E2E convention)
- Tests use Playwright test API correctly
- Accessibility tests import AxeBuilder correctly

Verification commands (files only):
ls tests/e2e/
ls tests/e2e/language-navigation.spec.ts tests/e2e/gallery-interactions.spec.ts
ls tests/e2e/search.spec.ts tests/e2e/accessibility.spec.ts

After completion, commit with message from the task document.

Note: Browser installation and test execution happen later. Focus on creating files with correct content.
```

---

## 📋 TASK 5: CI/CD Workflows

**Prompt to send (after Task 4 completes):**

```
Task: CI/CD Workflows (Part 5/6)

Read and implement: docs/testing-task-5-ci.md
Context: docs/testing-context.md
Prerequisites: Tasks 1-4 completed (all test files created)

⚠️ IMPORTANT: This task runs in an isolated VM. Only CREATE FILES. Workflows will run automatically when pushed to GitHub.

Objective: Create GitHub Actions workflow files to automate testing.

What to do:
1. Create .github/workflows/ directory
2. Create 2 workflow files:
   - test.yml (main testing workflow)
   - accessibility.yml (accessibility audit workflow)

Success criteria:
- Both workflow files created in .github/workflows/
- YAML syntax is valid (no tabs, 2 spaces for indentation)
- Files use spaces for indentation (not tabs)
- Workflows reference correct branches
- All workflow steps are properly formatted

Verification commands (files only):
ls -la .github/workflows/
ls .github/workflows/test.yml .github/workflows/accessibility.yml
cat .github/workflows/test.yml | head -20

After completion, commit with message from the task document.

Note: Workflows will be tested when code is pushed to GitHub. Use spaces for YAML indentation (2 spaces per level), never tabs.
```

---

## 📋 TASK 6: Documentation & Validation

**Prompt to send (after Task 5 completes - FINAL TASK):**

```
Task: Documentation & Validation (Part 6/6 - FINAL)

Read and implement: docs/testing-task-6-docs.md
Context: docs/testing-context.md
Prerequisites: Tasks 1-5 completed (all files created)

⚠️ IMPORTANT: This task runs in an isolated VM. Only CREATE FILES. Do NOT run pnpm install or pnpm run validate:tests.

Objective: Create testing documentation and validation script. This completes file creation for testing implementation.

What to do:
1. Create docs/testing-guide.md (comprehensive testing documentation)
2. Create scripts/ directory (if needed)
3. Create scripts/validate-tests.js (validation script)
4. Update README.md with testing section (MERGE, don't replace existing content)

Success criteria:
- docs/testing-guide.md created with complete documentation
- scripts/validate-tests.js created with validation logic
- README.md updated with testing section (around line 104)
- scripts/ directory exists
- Documentation is clear and accurate

Verification commands (files only):
ls docs/testing-guide.md
ls scripts/validate-tests.js
grep -A 5 "## 🧪 Testing" README.md
ls scripts/

After completion, commit with message from the task document.

🎉 This is the FINAL task! After this, all 22+ files are created.

IMPORTANT: After all 6 tasks complete and are committed, a HUMAN must run:
1. pnpm install
2. pnpm run validate:tests
3. pnpm run playwright:install
4. pnpm run test:unit
5. pnpm run build
6. pnpm run test:integration
7. pnpm run test:e2e

See Task 6 document for complete post-implementation instructions.
```

---

## 📊 Task Summary

| Task | Focus | Files Created | Est. Time |
|------|-------|---------------|-----------|
| 1 | Config Files | 5 configs + package.json | 15-20 min |
| 2 | Test Setup & Unit | 6 test files | 20-30 min |
| 3 | Integration Tests | 4 test files | 20-25 min |
| 4 | E2E Tests | 4 test files | 20-25 min |
| 5 | CI/CD Workflows | 2 workflow files | 10-15 min |
| 6 | Documentation | 3 docs + validation | 15-20 min |
| **Total** | **Complete Suite** | **22+ files** | **~2 hours** |

---

## 🎯 Quick Reference

### Order of Execution
1. Task 1 → Config files & package.json updates
2. Task 2 → Test setup & unit test files
3. Task 3 → Integration test files
4. Task 4 → E2E test files
5. Task 5 → CI/CD workflow files
6. Task 6 → Documentation files (final)

### Critical Points for AI Agent

⚠️ **EACH TASK RUNS IN ISOLATED VM** - Only create files, no installations or test runs!

- **Task 1**: MERGE package.json (add scripts AND devDependencies), don't replace
- **Task 2**: Create test files with proper structure and imports
- **Task 3**: Create integration test files (site will be built later)
- **Task 4**: Create E2E test files (browsers installed later)
- **Task 5**: Use 2 spaces for YAML indentation, never tabs
- **Task 6**: MERGE README.md, don't replace content

### After All Tasks Complete

A **human** must run (in this order):
```bash
pnpm install                    # Install all dependencies
pnpm run validate:tests         # Verify all files created
pnpm run playwright:install     # Install browsers
pnpm run test:unit             # Run unit tests
pnpm run build                  # Build Hugo site
pnpm run test:integration      # Run integration tests
pnpm run test:e2e              # Run E2E tests
```

### Between Tasks

After each task:
1. Verify files were created (using ls/grep commands)
2. Commit with provided message
3. Proceed to next task

### Final Success (After Task 6)

You should have created:
- ✅ 5 configuration files
- ✅ package.json updated (scripts + devDependencies)
- ✅ 11 test files (setup, helpers, unit, integration, E2E)
- ✅ 2 CI/CD workflow files
- ✅ 3 documentation files
- ✅ **Total: 22+ files ready for testing**

Tests will be validated and run by a human after all files are committed.

---

## 🚨 Important Reminders for AI Agents

1. **Isolated VM environment**: Each task runs in fresh VM - only CREATE FILES
2. **No installations**: Do NOT run pnpm install, pnpm build, or any test commands
3. **Read context first**: Always start by reading `docs/testing-context.md`
4. **Follow task order**: Tasks build on each other - do them sequentially
5. **Read task files**: Each task has complete code and detailed instructions
6. **Merge, don't replace**: When editing package.json or README.md, READ FIRST then MERGE
7. **File creation only**: Verify files were created using ls/grep, not by running them
8. **Commit after each task**: Use exact commit messages from task documents

---

## 📝 Usage Example

```
Step 1: Send Task 1 prompt to AI agent (Codex)
Step 2: Agent creates 5 config files + updates package.json
Step 3: Agent commits changes
Step 4: Verify files exist: ls vitest.config.unit.ts (etc.)

Step 5: Send Task 2 prompt to AI agent
Step 6: Agent creates 6 test files
Step 7: Agent commits changes
Step 8: Verify files exist: ls tests/unit/pagination.test.ts (etc.)

... Continue through Task 6 ...

Step Final: After all 6 tasks committed:
- Human runs: pnpm install
- Human runs: pnpm run validate:tests
- Human runs: pnpm run test:unit
- Human runs: pnpm run build
- Human runs: pnpm run test:integration
- Human runs: pnpm run test:e2e

All tests should now work! ✅
```

---

## 🎉 Ready to Start!

Copy the prompts above (Tasks 1-6) and send them to your AI agent one at a time. After all tasks complete, follow the human verification steps in Task 6 documentation.

Good luck! 🚀

