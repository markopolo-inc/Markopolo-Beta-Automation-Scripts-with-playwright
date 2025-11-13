import pytest
from playwright.sync_api import Page, expect
from pages.markopolo_login_page import MarkopoloLoginPage

@pytest.mark.smoke
class TestSmoke:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip('/')
        self.login_page = MarkopoloLoginPage(page)

    def test_can_open_login_page(self):
        self.login_page.navigate_to_prod_env(self.base_url)
        expect(self.page).to_have_url(f"{self.base_url}/login")
        expect(self.page).to_have_title("Markopolo | Sign in")

    def test_signin_shows_validation_when_empty(self):
        self.login_page.navigate_to_prod_env(self.base_url)
        self.login_page.click_sign_in()
        self.login_page.verify_validation_message_for_empty_fields()
