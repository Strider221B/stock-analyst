## 1. Critical Principles

These principles are **non-negotiable** and must be followed without exception:

### Follow SOLID Design principles

**IMPORTANT** Ensure code follows SOLID design principles through out.

### Use Project Scripts, Not Direct Tools

Always invoke tools through `./scripts/*` instead of directly.

**Why**: Scripts ensure consistent configuration across local development and CI.

| Task | ❌ NEVER | ✅ ALWAYS |
|------|----------|-----------|
| Format code | `black .` | `./scripts/format.sh` |
| Run tests | `pytest` | `./scripts/test.sh` |
| Type check | `mypy .` | `./scripts/lint.sh` (includes mypy) |
| Lint code | `ruff check .` | `./scripts/lint.sh` |
| All checks | *(run each tool)* | `./scripts/check-all.sh` |

---
### No Shortcuts - Fix Root Causes

Never bypass quality checks or suppress errors without justification.

**Forbidden Shortcuts**:
- ❌ Commenting out failing tests
- ❌ Adding `# noqa` without issue reference
- ❌ Lowering quality thresholds to pass builds
- ❌ Using `git commit --no-verify` to skip pre-commit
- ❌ Deleting code to reduce complexity metrics

**Required Approach**:
- ✅ Fix the failing test or mark with `@pytest.mark.skip(reason="Issue #N")`
- ✅ Refactor code to pass linting (or justify with issue: `# noqa  # Issue #N: reason`)
- ✅ Write tests to reach 90% coverage
- ✅ Always run pre-commit checks
- ✅ Refactor complex functions into smaller ones

### Stay Green - Never Request Review with Failing Checks

Follow the 4-gate workflow rigorously.

**The Rule**:
- 🚫 **NEVER** create PR while CI is red
- 🚫 **NEVER** request review with failing checks
- 🚫 **NEVER** merge without LGTM

**The Process**:
1. Gate 1: Local checks pass (`./scripts/check-all.sh` → exit 0)
2. Gate 2: CI pipeline green (all jobs ✅)
3. Gate 3: Mutation score ≥80%
4. Gate 4: Code review LGTM

### Operate from Project Root

Use relative paths from project root. Never `cd` into subdirectories.

**Why**: Ensures commands work in any environment (local, CI, scripts).

**Examples**:
- ✅ `./scripts/test.sh tests/unit/ai/test_orchestrator.py`
- ❌ `cd tests/unit/ai && pytest test_orchestrator.py`

**CI Note**: CI always runs from project root. Commands that use `cd` will break in CI.

---
### Verify Before Commit

Run `./scripts/check-all.sh` before every commit. Only commit if exit code is 0.

**Pre-Commit Checklist**:
- [ ] `./scripts/check-all.sh` passes (exit 0)
- [ ] All new functions have tests
- [ ] Coverage ≥90% maintained
- [ ] No failing tests
- [ ] Conventional commit message ready

## 2. Project Overview

I want to build an app in python backend and react front end for stock analysis and buy/sell suggestions based on latest news and technical analysis. For stock related information I want to start of by using yahoo finance first. The UI will allow user to log in, register stocks, provide in-depth analysis by using information from yahoo stocks and news and processed by Gemini. So Gemini will have access to free tools that it may need to perform its analysis, like data from yahoo finance, playwright etc. Use framework like langgraph but you may choose any other framework that may be better suited for this. The app will also search for stocks which have a large potential gains in the short and long term. The app will ask the user to  select companies and or domains in which they want to perform the search. It will also have a sidebar chat which will be connected to Gemini for discussing more on the recommendations. The app will be finally hosted on Azure and the deployment will happen via terraform.

the entire app should run locally and will be tested locally before finally being pushed to Azure. Also, on Azure we want to have 2 separate environment - test and prod.


---
