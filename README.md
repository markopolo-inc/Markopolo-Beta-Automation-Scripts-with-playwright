# Markopolo Playwright Automation

Playwright-based UI automation for Markopolo (Staging/Production) with a simple interactive runner.

## Prerequisites

- Python 3.13 (recommended to match installed packages)
- Windows PowerShell or Command Prompt

## Quick Start (Recommended)

Set environment variables first, then run the interactive test runner:

**Windows:**
```
set MANUAL_EMAIL=your@email.com
set MANUAL_PASSWORD=yourpassword
./r.bat                # defaults: Staging, Chromium, headless
./r.bat stg chromium headed
./r.bat prod firefox   # Production, Firefox, headless
```

**macOS/Linux:**
```
export MANUAL_EMAIL=your@email.com
export MANUAL_PASSWORD=yourpassword
chmod +x r.sh          # first time only
./r.sh                 # defaults: Staging, Chromium, headless
./r.sh stg chromium headed
./r.sh prod firefox    # Production, Firefox, headless
```

The runner will:
- Install/verify Python dependencies
- Install Playwright browsers
- Ask which server to test (Staging/Production)
- Use `MANUAL_EMAIL` and `MANUAL_PASSWORD` env vars for valid login tests
- Set `BASE_URL` based on your choice

## Advanced: Run Directly with Pytest

Set environment and run with Python 3.13 to match your installed packages:

```
$env:BASE_URL="https://beta-stg.markopolo.ai"
$env:MANUAL_EMAIL="you@example.com"      # optional
$env:MANUAL_PASSWORD="your_password"     # optional
py -3.13 -m pytest -v --browser=chromium --headed
```

Other browsers: `--browser=firefox` or `--browser=webkit`

## Project Structure

- `tests/` – Test suites
  - `test_markopolo_login.py` – Login flow tests
- `tests/pages/` – Page Objects
  - `markopolo_login_page.py` – Login page POM
- `tests/test_data/` – Test data JSON
- `tests/conftest.py` – Playwright fixtures (browser/context/page)
- `pytest.ini` – Pytest config (markers, logging)
- `requirements.txt` – Dependencies
- `r.bat` – One-command interactive runner

## Credentials

- Preferred: set env vars before running, or provide at the prompt in `r.bat`.
  - `MANUAL_EMAIL` and `MANUAL_PASSWORD`
- The valid login test will also use provided defaults if env vars are not set.

## Troubleshooting

- "fixture 'context' not found" or CLI option conflicts:
  - The project uses its own Playwright fixtures in `tests/conftest.py`. We removed custom CLI option registration to avoid conflicts with plugins.

- Running with the wrong Python version:
  - If dependencies were installed under Python 3.13, run tests as `py -3.13 -m pytest ...`.

- Navigation timeouts:
  - Network may be slow. We increased timeouts and made navigation more tolerant; re-run in `--headed` for debugging.

## Markers

- `@pytest.mark.login` – Login tests
- `@pytest.mark.smoke` – Smoke subset
- `@pytest.mark.manual` – Requires manual input/credentials

## Notes

- Environments:
  - Staging: `https://beta-stg.markopolo.ai`
  - Production: `https://beta.markopolo.ai`

If you need CI instructions or a PowerShell version of the runner, let me know.
