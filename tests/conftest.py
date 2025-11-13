import os
import pytest
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright
from typing import Dict, Any

# Get base URL from environment variable or use a default
BASE_URL = os.getenv("BASE_URL", "https://beta-stg.markopolo.ai")

@pytest.fixture(scope="session")
def pw():
    with sync_playwright() as p:
        yield p

@pytest.fixture(scope="session")
def browser_context_args() -> Dict[str, Any]:
    return {
        "viewport": {
            "width": 1920,
            "height": 1080,
        },
        "ignore_https_errors": True,
        "record_video_dir": "videos/" if os.getenv("RECORD_VIDEO", "false").lower() == "true" else None,
    }

@pytest.fixture(scope="session")
def base_url(pytestconfig) -> str:
    return os.getenv("BASE_URL", BASE_URL)

@pytest.fixture(scope="session")
def browser(pytestconfig, pw) -> Browser:
    # Read from pytest options if available (e.g., provided by pytest-playwright), else from env, else defaults
    browser_opt = getattr(pytestconfig.option, "browser", None)
    if isinstance(browser_opt, (list, tuple)):
        browser_name = (browser_opt[0] if browser_opt else None)
    else:
        browser_name = browser_opt
    browser_name = browser_name or os.getenv("BROWSER", "chromium")

    headed_raw = getattr(pytestconfig.option, "headed", None)
    if headed_raw is None:
        headed = os.getenv("HEADED", "false").lower() in ("1", "true", "yes", "y")
    else:
        headed = bool(headed_raw)
    slow_mo = int(os.getenv("SLOW_MO", "0"))
    return getattr(pw, browser_name).launch(headless=not headed, slow_mo=slow_mo)

@pytest.fixture(scope="function")
def context(browser: Browser, browser_context_args: Dict[str, Any]) -> BrowserContext:
    ctx = browser.new_context(**{k: v for k, v in browser_context_args.items() if v is not None})
    try:
        yield ctx
    finally:
        ctx.close()

@pytest.fixture(scope="function")
def page(context: BrowserContext, base_url: str) -> Page:
    page = context.new_page()
    page.set_default_timeout(30000)
    page.goto(base_url)
    try:
        yield page
    finally:
        page.close()

# This hook allows adding custom markers
def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "smoke: mark test as a smoke test"
    )
    config.addinivalue_line(
        "markers",
        "login: mark test as related to login functionality"
    )
    config.addinivalue_line(
        "markers",
        "manual: mark test as requiring manual interaction"
    )
    config.addinivalue_line(
        "markers",
        "manual: mark test as requiring manual interaction"
    )
