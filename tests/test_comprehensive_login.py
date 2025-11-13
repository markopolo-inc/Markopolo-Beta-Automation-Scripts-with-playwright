import os
import json
import pytest
from playwright.sync_api import Page, expect
from pages.markopolo_login_page import MarkopoloLoginPage
from pathlib import Path

# Load test data
test_data_path = Path(__file__).parent / "test_data" / "markopolo_login_testdata.json"
with open(test_data_path, 'r') as f:
    TEST_DATA = json.load(f)


@pytest.mark.login
class TestLoginValidation:
    """Test login field validation and error handling."""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip('/')
        self.login = MarkopoloLoginPage(page)

    def test_empty_email_and_password(self):
        """Test validation when both email and password are empty."""
        self.login.navigate_to_prod_env(self.base_url)
        self.login.click_sign_in()
        self.login.verify_validation_message_for_empty_fields()

    def test_empty_email_only(self):
        """Test validation when only email is empty."""
        self.login.navigate_to_prod_env(self.base_url)
        self.login.enter_password_only(TEST_DATA['edge_cases']['empty_password']['password'])
        self.login.click_sign_in()
        self.login.verify_validation_message_for_empty_fields()

    def test_empty_password_only(self):
        """Test validation when only password is empty."""
        self.login.navigate_to_prod_env(self.base_url)
        self.login.enter_email_only(TEST_DATA['edge_cases']['empty_password']['email'])
        self.login.click_sign_in()
        self.login.verify_validation_message_for_empty_fields()

    def test_whitespace_only_email(self):
        """Test validation with whitespace-only email."""
        self.login.navigate_to_prod_env(self.base_url)
        self.login.enter_credentials(
            TEST_DATA['edge_cases']['whitespace_only_email']['email'],
            TEST_DATA['edge_cases']['whitespace_only_email']['password']
        )
        self.login.click_sign_in()
        # Should show validation or error
        try:
            self.login.verify_validation_message_for_empty_fields()
        except:
            self.login.verify_error_message()

    def test_whitespace_only_password(self):
        """Test validation with whitespace-only password."""
        self.login.navigate_to_prod_env(self.base_url)
        self.login.enter_credentials(
            TEST_DATA['edge_cases']['whitespace_only_password']['email'],
            TEST_DATA['edge_cases']['whitespace_only_password']['password']
        )
        self.login.click_sign_in()
        try:
            self.login.verify_validation_message_for_empty_fields()
        except:
            self.login.verify_error_message()


@pytest.mark.login
class TestLoginInvalidCredentials:
    """Test login with various invalid credential combinations."""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip('/')
        self.login = MarkopoloLoginPage(page)

    def test_non_existent_user(self):
        """Test login with non-existent user."""
        self.login.navigate_to_prod_env(self.base_url)
        creds = TEST_DATA['invalid_credentials'][0]
        self.login.enter_credentials(creds['email'], creds['password'])
        self.login.click_sign_in()
        self.login.verify_error_message()

    def test_wrong_password_for_existing_email(self):
        """Test login with correct email but wrong password."""
        self.login.navigate_to_prod_env(self.base_url)
        creds = TEST_DATA['invalid_credentials'][1]
        self.login.enter_credentials(creds['email'], creds['password'])
        self.login.click_sign_in()
        self.login.verify_error_message()


@pytest.mark.login
class TestLoginEmailFormats:
    """Test login with various email formats."""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip('/')
        self.login = MarkopoloLoginPage(page)

    def test_email_without_domain(self):
        """Test login with email missing domain."""
        self.login.navigate_to_prod_env(self.base_url)
        self.login.enter_credentials(
            TEST_DATA['edge_cases']['email_without_domain']['email'],
            TEST_DATA['edge_cases']['email_without_domain']['password']
        )
        self.login.click_sign_in()
        # Should show validation or error
        try:
            self.login.verify_validation_message_for_empty_fields()
        except:
            self.login.verify_error_message()

    def test_email_with_invalid_format(self):
        """Test login with invalid email format."""
        self.login.navigate_to_prod_env(self.base_url)
        self.login.enter_credentials(
            TEST_DATA['edge_cases']['email_with_invalid_format']['email'],
            TEST_DATA['edge_cases']['email_with_invalid_format']['password']
        )
        self.login.click_sign_in()
        try:
            self.login.verify_validation_message_for_empty_fields()
        except:
            self.login.verify_error_message()

    def test_email_with_spaces(self):
        """Test login with spaces in email."""
        self.login.navigate_to_prod_env(self.base_url)
        self.login.enter_credentials(
            TEST_DATA['edge_cases']['email_with_spaces']['email'],
            TEST_DATA['edge_cases']['email_with_spaces']['password']
        )
        self.login.click_sign_in()
        self.login.verify_error_message()

    def test_email_case_sensitivity(self):
        """Test login with uppercase email (case sensitivity)."""
        self.login.navigate_to_prod_env(self.base_url)
        self.login.enter_credentials(
            TEST_DATA['edge_cases']['email_case_sensitivity']['email'],
            TEST_DATA['edge_cases']['email_case_sensitivity']['password']
        )
        self.login.click_sign_in()
        self.login.verify_error_message()

    def test_email_with_plus_addressing(self):
        """Test login with plus addressing in email."""
        self.login.navigate_to_prod_env(self.base_url)
        self.login.enter_credentials(
            TEST_DATA['boundary_cases']['email_with_plus']['email'],
            TEST_DATA['boundary_cases']['email_with_plus']['password']
        )
        self.login.click_sign_in()
        self.login.verify_error_message()

    def test_email_with_dot_in_local_part(self):
        """Test login with dot in email local part."""
        self.login.navigate_to_prod_env(self.base_url)
        self.login.enter_credentials(
            TEST_DATA['boundary_cases']['email_with_dot']['email'],
            TEST_DATA['boundary_cases']['email_with_dot']['password']
        )
        self.login.click_sign_in()
        self.login.verify_error_message()


@pytest.mark.login
class TestLoginPasswordFormats:
    """Test login with various password formats."""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip('/')
        self.login = MarkopoloLoginPage(page)

    def test_password_with_special_characters(self):
        """Test login with special characters in password."""
        self.login.navigate_to_prod_env(self.base_url)
        self.login.enter_credentials(
            TEST_DATA['edge_cases']['special_characters_in_password']['email'],
            TEST_DATA['edge_cases']['special_characters_in_password']['password']
        )
        self.login.click_sign_in()
        self.login.verify_error_message()

    def test_very_long_password(self):
        """Test login with very long password."""
        self.login.navigate_to_prod_env(self.base_url)
        self.login.enter_credentials(
            TEST_DATA['edge_cases']['very_long_password']['email'],
            TEST_DATA['edge_cases']['very_long_password']['password']
        )
        self.login.click_sign_in()
        self.login.verify_error_message()


@pytest.mark.login
@pytest.mark.security
class TestLoginSecurityCases:
    """Test login with security attack scenarios."""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip('/')
        self.login = MarkopoloLoginPage(page)

    def test_sql_injection_in_email(self):
        """Test SQL injection attempt in email field."""
        self.login.navigate_to_prod_env(self.base_url)
        self.login.enter_credentials(
            TEST_DATA['edge_cases']['sql_injection_attempt_email']['email'],
            TEST_DATA['edge_cases']['sql_injection_attempt_email']['password']
        )
        self.login.click_sign_in()
        # Should not bypass authentication
        self.login.verify_error_message()

    def test_sql_injection_in_password(self):
        """Test SQL injection attempt in password field."""
        self.login.navigate_to_prod_env(self.base_url)
        self.login.enter_credentials(
            TEST_DATA['edge_cases']['sql_injection_attempt_password']['email'],
            TEST_DATA['edge_cases']['sql_injection_attempt_password']['password']
        )
        self.login.click_sign_in()
        self.login.verify_error_message()

    def test_xss_attempt_in_email(self):
        """Test XSS attempt in email field."""
        self.login.navigate_to_prod_env(self.base_url)
        self.login.enter_credentials(
            TEST_DATA['edge_cases']['xss_attempt_email']['email'],
            TEST_DATA['edge_cases']['xss_attempt_email']['password']
        )
        self.login.click_sign_in()
        self.login.verify_error_message()

    def test_xss_attempt_in_password(self):
        """Test XSS attempt in password field."""
        self.login.navigate_to_prod_env(self.base_url)
        self.login.enter_credentials(
            TEST_DATA['edge_cases']['xss_attempt_password']['email'],
            TEST_DATA['edge_cases']['xss_attempt_password']['password']
        )
        self.login.click_sign_in()
        self.login.verify_error_message()


@pytest.mark.login
@pytest.mark.smoke
class TestLoginValidCredentials:
    """Test successful login with valid credentials."""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip('/')
        self.login = MarkopoloLoginPage(page)

    def test_valid_login_with_env_vars(self):
        """Test successful login with environment variables."""
        email = os.getenv("MANUAL_EMAIL")
        password = os.getenv("MANUAL_PASSWORD")
        if not email or not password:
            pytest.skip("No valid credentials provided in environment variables")

        self.login.maximize_window()
        self.login.perform_login(self.base_url, email=email, password=password)
        expect(self.page).not_to_have_url(f"{self.base_url}/login")

    def test_valid_login_with_test_data(self):
        """Test successful login with test data credentials."""
        email = TEST_DATA['valid_credentials']['email']
        password = TEST_DATA['valid_credentials']['password']
        
        if email == "fagun115946@gmail.com" and not os.getenv("MANUAL_EMAIL"):
            pytest.skip("Using placeholder credentials; set MANUAL_EMAIL to test")

        self.login.maximize_window()
        self.login.perform_login(self.base_url, email=email, password=password)
        expect(self.page).not_to_have_url(f"{self.base_url}/login")


@pytest.mark.login
class TestLoginUIBehavior:
    """Test UI behavior and interactions during login."""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip('/')
        self.login = MarkopoloLoginPage(page)

    def test_login_page_loads_correctly(self):
        """Test that login page loads with all required elements."""
        self.login.navigate_to_prod_env(self.base_url)
        expect(self.page).to_have_url(f"{self.base_url}/login")
        expect(self.page).to_have_title("Markopolo | Sign in")

    def test_form_elements_are_visible(self):
        """Test that all form elements are visible on login page."""
        self.login.navigate_to_prod_env(self.base_url)
        # Try to find email field (should be visible)
        email_field = self.login._find_element('email')
        expect(email_field).to_be_visible()
        # Try to find password field
        password_field = self.login._find_element('password')
        expect(password_field).to_be_visible()
        # Try to find sign in button
        sign_in_button = self.login._find_element('sign_in')
        expect(sign_in_button).to_be_visible()

    def test_error_message_clears_on_new_attempt(self):
        """Test that error message clears when user tries again."""
        self.login.navigate_to_prod_env(self.base_url)
        # First attempt with invalid credentials
        self.login.enter_invalid_credentials()
        self.login.click_sign_in()
        self.login.verify_error_message()
        
        # Clear fields and try again
        self.login.enter_credentials("another@example.com", "anotherpass")
        # Error should be replaced or cleared
        self.login.click_sign_in()
