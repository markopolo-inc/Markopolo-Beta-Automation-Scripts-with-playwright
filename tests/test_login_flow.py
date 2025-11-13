import os
import pytest
from playwright.sync_api import Page, expect
from pages.markopolo_login_page import MarkopoloLoginPage

@pytest.mark.login
class TestLoginFlow:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip('/')
        self.login = MarkopoloLoginPage(page)

    def test_invalid_credentials(self):
        self.login.navigate_to_prod_env(self.base_url)
        self.login.maximize_window()
        self.login.enter_invalid_credentials()
        self.login.click_sign_in()
        self.login.verify_error_message()

    @pytest.mark.smoke
    def test_valid_credentials(self):
        email = os.getenv("MANUAL_EMAIL")
        password = os.getenv("MANUAL_PASSWORD")
        if not email or not password:
            pytest.skip("No valid credentials provided in environment variables")

        self.login.maximize_window()
        self.login.perform_login(self.base_url, email=email, password=password)

        # Accept any post-login landing; verify we are not on /login anymore
        expect(self.page).not_to_have_url(f"{self.base_url}/login")
