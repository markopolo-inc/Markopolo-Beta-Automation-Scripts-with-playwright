import os
import pytest
from playwright.sync_api import Page, expect
from pages.markopolo_login_page import MarkopoloLoginPage

# Mark all tests in this class with the "login" marker
@pytest.mark.login
class TestMarkopoloLogin:
    """Test suite for Markopolo login functionality."""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page, base_url: str):
        """Setup test fixtures."""
        self.page = page
        self.base_url = base_url.rstrip('/')  # Remove trailing slash if present
        self.login_page = MarkopoloLoginPage(page)

    def test_navigate_to_login_page(self):
        """Verify user is navigated to Markopolo Login Page."""
        # Navigate to login page
        self.login_page.navigate_to_prod_env(self.base_url)
        self.login_page.maximize_window()
        
        # Verify URL and page title
        expect(self.page).to_have_url(f"{self.base_url}/login")
        # Actual title includes subtitle
        expect(self.page).to_have_title("Markopolo | Sign in")

    @pytest.mark.smoke
    def test_login_without_credentials(self):
        """Verify users cannot log in without entering credentials."""
        # Navigate to login page
        self.login_page.navigate_to_prod_env(self.base_url)
        self.login_page.maximize_window()
        
        # Attempt to login without credentials
        self.login_page.click_sign_in()
        
        # Verify validation messages are shown
        self.login_page.verify_validation_message_for_empty_fields()

    def test_login_with_invalid_credentials(self):
        """Verify users cannot log in with invalid credentials."""
        # Navigate to login page
        self.login_page.navigate_to_prod_env(self.base_url)
        self.login_page.maximize_window()
        
        # Enter invalid credentials and attempt to login
        self.login_page.enter_invalid_credentials()
        self.login_page.click_sign_in()
        
        # Verify error message is shown
        self.login_page.verify_error_message()

    def test_login_with_only_email(self):
        """Verify validation when only email is provided."""
        self.login_page.navigate_to_prod_env(self.base_url)
        self.login_page.maximize_window()
        self.login_page.enter_email_only("someone@example.com")
        self.login_page.click_sign_in()
        self.login_page.verify_validation_message_for_empty_fields()

    def test_login_with_only_password(self):
        """Verify validation when only password is provided."""
        self.login_page.navigate_to_prod_env(self.base_url)
        self.login_page.maximize_window()
        self.login_page.enter_password_only("somepassword")
        self.login_page.click_sign_in()
        self.login_page.verify_validation_message_for_empty_fields()

    @pytest.mark.smoke
    def test_login_with_valid_credentials(self):
        """Verify users can log in with valid credentials."""
        # Use env vars; skip if not provided to avoid hardcoding secrets in repo
        email = os.getenv("MANUAL_EMAIL")
        password = os.getenv("MANUAL_PASSWORD")
        if not email or not password:
            pytest.skip("No valid credentials provided in environment variables")
        
        # Perform login with valid credentials
        self.login_page.maximize_window()
        self.login_page.perform_login(self.base_url, email=email, password=password)
        
        # After successful login, verify we're on the home page
        expect(self.page).to_have_url(f"{self.base_url}/")
        
        # Verify user is logged in by checking for a logged-in element
        # Adjust the selector based on your application
        expect(self.page.locator("button:has-text('Logout')")).to_be_visible()

    @pytest.mark.skip(reason="Google OAuth login not implemented yet")
    def test_login_with_google(self):
        """Verify users can log in using Google OAuth."""
        # This is a placeholder - implement Google OAuth login test
        self.login_page.navigate_to_prod_env(self.base_url)
        # Add Google OAuth login steps here
        pass
    
    @pytest.mark.manual
    def test_login_with_manual_credentials(self):
        """Test login with manually provided credentials."""
        email = os.getenv("MANUAL_EMAIL")
        password = os.getenv("MANUAL_PASSWORD")
        
        if not email or not password:
            pytest.skip("No manual credentials provided in environment variables")
        
        # Perform login with manual credentials
        self.login_page.maximize_window()
        self.login_page.perform_login(
            base_url=self.base_url,
            email=email,
            password=password
        )
        
        # Verify successful login
        expect(self.page).to_have_url(f"{self.base_url}/")
        expect(self.page.locator("button:has-text('Logout')")).to_be_visible()
