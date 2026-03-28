# Test Infrastructure & Coverage Implementation Plan

This plan details the steps to set up the testing infrastructure for both the backend and frontend, activating the local Python environment natively (but skipping in CI), setting coverage thresholds, using Docker for the test database, and testing critical paths.

## Proposed Changes

### Scripts & Environment Checks

#### [MODIFY] [test.sh](file:///home/somesh/Git/stock-analyst/scripts/test.sh)
- Add conditional environment sourcing before running backend tests:
  ```bash
  if [ "$CI" != "true" ]; then
      source ~/PythonEnvs/P3.12_LLM/bin/activate
  fi
  ```
- Make script spin up test PostgreSQL docker container, run tests with `--cov=backend --cov-fail-under=80`, and tear down container safely.

#### [NEW] [test-frontend.sh](file:///home/somesh/Git/stock-analyst/scripts/test-frontend.sh)
- A new script to run frontend tests using Vitest (`npm run test`).
- Will navigate to `frontend/` and invoke the tests enforcing coverage goals. Make it executable.

#### [MODIFY] [check-all.sh](file:///home/somesh/Git/stock-analyst/scripts/check-all.sh)
- Include `./scripts/test-frontend.sh` in the chain of checks to ensure the "Stay Green" rule applies to frontend tests.

---

### Backend Testing

#### [MODIFY] [requirements.txt](file:///home/somesh/Git/stock-analyst/backend/requirements.txt)
- Add `pytest`, `pytest-asyncio`, `httpx`, and `pytest-cov` to support API endpoint testing and coverage reports.

#### [NEW] [conftest.py](file:///home/somesh/Git/stock-analyst/backend/tests/conftest.py)
- Setup Database fixtures for SQLAlchemy communicating with the temporary Docker PostgreSQL database.
- Setup the FastAPI `TestClient` for synchronous integration tests or `AsyncClient` alongside asynchronous tests.
- Override the `get_db` dependency to use the isolated test database session.

#### [NEW] [test_auth.py](file:///home/somesh/Git/stock-analyst/backend/tests/routers/test_auth.py)
- **Unit & Integration tests** covering the critical path in `auth.py`:
  - `test_register_user`: Success case and Duplicate Email case.
  - `test_login_user`: Success case and Invalid Credentials case.
  - `test_refresh_token`: Refresh logic and revoked token behavior.
  - `test_logout_user`: Logout process and cookie clearing.

---

### Frontend Testing

#### [MODIFY] [package.json](file:///home/somesh/Git/stock-analyst/frontend/package.json)
- Add `vitest`, `jsdom`, and `@testing-library/react` as dev dependencies.
- Add `"test": "vitest run"` script logic.

#### [MODIFY] [vite.config.ts](file:///home/somesh/Git/stock-analyst/frontend/vite.config.ts)
- Configure `test` environment to use `jsdom` and appropriate React testing plugins.

#### [NEW] [App.test.tsx](file:///home/somesh/Git/stock-analyst/frontend/src/tests/App.test.tsx)
- Basic functioning tests ensuring the frontend harness operates flawlessly and can interpret rendered components properly.

## Verification Plan

### Automated Tests
- Run `./scripts/test.sh` executing backend tests against temporary Docker database, coverage > 80%.
- Run `./scripts/test-frontend.sh` and ensure frontend tests pass.
- Run `./scripts/check-all.sh` to ensure all checks remain green (Exit 0).
