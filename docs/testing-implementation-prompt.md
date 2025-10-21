# AI Agent Implementation Prompt

Copy and send this prompt to your AI coding agent (Claude Codex, Cursor Agent, etc.):

---

## Task: Implement Testing Infrastructure

You are tasked with implementing a comprehensive automated testing suite for the Loudly Proud project - a Hugo-based multilingual LGBTQ+ literature catalog.

### Your Mission

Read and follow the complete implementation specification in `docs/testing-implementation-task.md`. This document contains:
- Full project context and architecture
- Detailed implementation phases with complete code
- Success criteria and verification steps
- Troubleshooting guidance

### What You Must Do

1. **Read the specification**: Start by reading `docs/testing-implementation-task.md` thoroughly
2. **Execute all 8 phases** in order:
   - Phase 1: Dependencies & Configuration
   - Phase 2: Test Setup Files
   - Phase 3: Unit Tests
   - Phase 4: Integration Tests
   - Phase 5: E2E Tests
   - Phase 6: CI/CD Configuration
   - Phase 7: Documentation
   - Phase 8: Validation
3. **Verify your work**: Run all verification commands listed in the document
4. **Create a PR**: Commit to a new branch named `feature/testing-implementation`

### Key Requirements

- **Complete implementation**: All files from the specification must be created
- **Merge, don't replace**: When modifying `package.json`, merge new scripts with existing ones
- **TypeScript compliance**: All code must compile without errors
- **Test independence**: Every test must be isolated and runnable independently
- **Follow conventions**: Use modern TypeScript syntax per project standards

### Deliverables

After implementation, these commands MUST work:

```bash
pnpm install                  # Install dependencies
pnpm run validate:tests       # Validation passes
pnpm run test:unit            # Unit tests run
pnpm run build                # Site builds successfully
pnpm run test:integration     # Integration tests run
pnpm run test:e2e            # E2E tests execute
```

### Branch & Commit

- **Branch name**: `feature/testing-implementation`
- **Commit message**: Use the template provided in the specification document

### Success Criteria

✅ All 22+ files created (configs, tests, workflows, docs)  
✅ All dependencies installed successfully  
✅ TypeScript compiles without errors  
✅ Validation script passes  
✅ Unit tests run and pass (or show meaningful results)  
✅ Integration tests run after build  
✅ E2E tests execute (browser launches)  
✅ CI workflows are valid YAML  
✅ Documentation is complete  

### If You Encounter Issues

Consult the "Troubleshooting" section in `docs/testing-implementation-task.md`. Common issues and solutions are documented there.

### Final Step

After successful implementation:
1. Run all verification commands
2. Ensure validation passes
3. Commit all changes with the provided commit message
4. Report completion with summary of what was created

---

## Begin Implementation

Start by reading `docs/testing-implementation-task.md` and proceed through each phase systematically. Good luck! 🚀

