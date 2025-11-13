import pytest
from playwright.sync_api import Page, expect
from pages.markopolo_login_page import MarkopoloLoginPage


@pytest.mark.smoke
class TestSmoke:
    """Minimal smoke coverage to ensure at least one browser test runs."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")
        self.login_page = MarkopoloLoginPage(page)

    def test_can_open_login_page(self):
        """Verify the login page loads and responds."""
        self.login_page.navigate_to_prod_env(self.base_url)
        expect(self.page).to_have_url(f"{self.base_url}/login")
        expect(self.page).to_have_title("Markopolo | Sign in")

