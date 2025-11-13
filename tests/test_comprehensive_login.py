import pytest
from playwright.sync_api import Page, expect
from pages.markopolo_login_page import MarkopoloLoginPage


@pytest.mark.login
class TestLoginCoreFlows:
    """Focused login coverage exercising the main UI paths."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")
        self.login = MarkopoloLoginPage(page)

    def test_login_page_loads(self):
        """Login page should render with the expected URL and title."""
        self.login.navigate_to_prod_env(self.base_url)
        expect(self.page).to_have_url(f"{self.base_url}/login")
        expect(self.page).to_have_title("Markopolo | Sign in")

    def test_empty_credentials_validation(self):
        """Submitting empty form should display validation messaging."""
        self.login.navigate_to_prod_env(self.base_url)
        self.login.click_sign_in()
        self.login.verify_validation_message_for_empty_fields()

    def test_invalid_credentials_shows_error(self):
        """Invalid credentials path stays on login and shows error."""
        self.login.navigate_to_prod_env(self.base_url)
        self.login.enter_invalid_credentials()
        self.login.click_sign_in()
        self.login.verify_error_message()
        expect(self.page).to_have_url(f"{self.base_url}/login")

