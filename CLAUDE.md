# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Context

30-day self-training program for a software testing internship (Python + pytest). The learner has Python basics, no prior testing experience. All code under `test_intern/`.

## Commands

```bash
# Unit tests (test_register.py, test_api.py)
pytest test_register.py -v
pytest test_api.py -v

# API tests (requires Flask running in another terminal)
python api_server.py                    # terminal 1
pytest test_api_register.py -v          # terminal 2

# Coverage
pytest test_register.py --cov=register --cov-report=term

# All tests at once
pytest -v
```

## Architecture

### Two-layer testing setup

**Layer 1 — Unit tests** (`register.py` + `test_register.py`):
Pure Python functions, import directly, no external dependency. Validates phone/password/nickname/confirm-password logic. Two error styles coexist: `return str | None` and `raise ValueError/PhoneAlreadyRegisteredError`.

**Layer 2 — API tests** (`api_server.py` + `test_api_register.py`):
A Flask server with in-memory `registered_phones` set. Tests hit `http://127.0.0.1:5000/api/register` and `/api/test/clear` via `requests`. Server must be running separately.

### Fixture architecture

`conftest.py` provides session-scoped fixtures (`base_url`, `api_client`) shared across all API test files. `api_client` is a `requests.Session` instance — returns TCP connections and manages cookies. `yield`/`close()` pattern for cleanup.

### Test data design

- Phone `13800001111` is the permanent "already registered" seed — never use it for success tests
- `/api/test/clear` resets data between tests (invoked via `autouse=True` fixture)
- Random phone generation (`fresh_phone` fixture) prevents cross-test pollution

## Key Files

| File | Role |
|------|------|
| `register.py` | Business logic: validation functions |
| `test_register.py` | Unit tests: parametrized, includes exception tests |
| `api_server.py` | Flask REST API; run before API tests |
| `test_api_register.py` | Integration tests against the Flask server |
| `test_api.py` | HTTP client practice (hits external httpbin.org) |
| `conftest.py` | Shared fixtures for all test files |
| `test_ui.py` | Selenium WebDriver tests (Day 12+) |

## Notes

- WSL environment — Selenium requires `--headless --no-sandbox --disable-dev-shm-usage`
- The learner discovered a test data bug on Day 6: `139abc9000` (10 chars) hit length check before digit check, so `match` must account for priority order
- `scope="function"` is pytest default (fresh per test); `scope="session"` runs once for the entire run
