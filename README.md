# Markopolo-Beta-Automation-Scripts-with-playwright

This is a Playwright-based test automation framework for Markopolo Beta.

## Setup

1. Install Python 3.8 or higher
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Install Playwright browsers:
   ```
   playwright install
   ```

## Running Tests

Run all tests:
```
pytest
```

Run a specific test file:
```
pytest tests/test_example.py
```

Run tests in headed mode:
```
pytest --headed
```

## Project Structure

- `tests/` - Test files (to be created)
- `pages/` - Page object models (to be created)
- `utils/` - Utility functions and helpers (to be created)
- `conftest.py` - Pytest fixtures (to be created)
- `pytest.ini` - Pytest configuration
- `requirements.txt` - Python dependencies

## Best Practices

1. Use page object model pattern
2. Keep tests independent and isolated
3. Use fixtures for setup/teardown
4. Add proper error handling and assertions
5. Use environment variables for sensitive data
