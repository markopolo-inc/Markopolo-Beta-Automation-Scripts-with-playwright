from playwright.sync_api import Page, expect
import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from playwright.sync_api import Page, expect, TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger(__name__)

class MarkopoloLoginPage:
    """Page Object Model for the Markopolo login page."""
    
    # Timeout settings (in milliseconds)
    TIMEOUT = 30000  # 30 seconds
    
    def __init__(self, page: Page):
        """Initialize the login page object.
        
        Args:
            page: Playwright Page instance
        """
        self.page = page
        
        # Primary selectors with fallbacks
        self._selectors = {
            'email': [
                "//input[contains(@class, 'mantine-TextInput-input')]",
                "input[type='email']",
                "input[name='email']",
                "input[id*='email']",
                "input[placeholder*='Email' i]",
                "//label[contains(normalize-space(.), 'Email')]/following::input[1]"
            ],
            'password': [
                "//input[contains(@class, 'mantine-PasswordInput-innerInput')]",
                "input[type='password']",
                "input[name='password']",
                "input[id*='password']",
                "input[placeholder*='Password' i]",
                "//label[contains(normalize-space(.), 'Password')]/following::input[1]"
            ],
            'sign_in': [
                "//button[@type='submit']",
                "button[type='submit']",
                "button:has-text('Sign in')",
                "//button[contains(translate(., 'IN', 'in'), 'sign in')]"
            ],
            'validation_message': [
                "//*[contains(text(), 'required')]",
                ".error-message:has-text('required')"
            ],
            'error_message': [
                "//div[contains(@class, 'go') or contains(text(), 'Invalid') or contains(text(), 'credentials')]",
                ".error-message:visible"
            ]
        }
        
        # Load test data
        self.test_data_path = os.path.join(Path(__file__).parent.parent, 'test_data', 'markopolo_login_testdata.json')
        self.test_data = self._load_test_data()
        
        # Set default timeout
        self.page.set_default_timeout(self.TIMEOUT)
    
    def _load_test_data(self) -> Dict[str, str]:
        """Load test data from JSON file or return defaults."""
        default_data = {
            'prod_invalid_email': 'invalid@example.com',
            'prod_invalid_pass': 'invalidpass123',
            'prod_email': 'test@example.com',
            'prod_pass': 'testpass123'
        }
        
        try:
            with open(self.test_data_path, 'r', encoding='utf-8') as file:
                return {**default_data, **json.load(file)}
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Could not load test data from {self.test_data_path}: {e}")
            return default_data
    
    def _find_element(self, element_type: str, timeout: Optional[float] = None) -> Any:
        """Find an element using the first matching selector.
        
        Args:
            element_type: The type of element to find (e.g., 'email', 'password')
            timeout: Optional timeout in milliseconds
            
        Returns:
            The first matching element locator
            
        Raises:
            TimeoutError: If no matching element is found within the timeout
        """
        selectors = self._selectors.get(element_type, [])
        if not selectors:
            raise ValueError(f"No selectors defined for element type: {element_type}")
        
        for selector in selectors:
            try:
                locator = self.page.locator(selector).first
                # Wait explicitly for the element to be attached and visible
                self.page.wait_for_selector(selector, state="visible", timeout=timeout or self.TIMEOUT)
                return locator
            except PlaywrightTimeoutError:
                logger.debug(f"Selector not found or not visible: {selector}")
                continue
                
        raise TimeoutError(f"Could not find visible element for {element_type} using any selector")
    
    def navigate_to_prod_env(self, base_url: str) -> None:
        """Navigate to the login page.
        
        Args:
            base_url: Base URL of the application
        """
        url = f"{base_url.rstrip('/')}/login"
        logger.info(f"Navigating to {url}")
        # More tolerant navigation: wait for 'load' and then for URL to contain /login
        self.page.goto(url, wait_until="load", timeout=self.TIMEOUT)
        self.page.wait_for_url("**/login*", timeout=self.TIMEOUT)
    
    def maximize_window(self) -> None:
        """Maximize the browser window."""
        self.page.set_viewport_size({"width": 1920, "height": 1080})
    
    def enter_invalid_credentials(self) -> None:
        """Enter invalid login credentials."""
        self.enter_credentials(
            email=self.test_data['prod_invalid_email'],
            password=self.test_data['prod_invalid_pass']
        )
    
    def enter_credentials(self, email: str, password: str) -> None:
        """Enter email and password into the login form.
        
        Args:
            email: Email to enter
            password: Password to enter
        """
        # Fill email field
        email_field = self._find_element('email')
        email_field.clear()
        email_field.fill(email)
        
        # Fill password field
        password_field = self._find_element('password')
        password_field.clear()
        password_field.fill(password)

    def enter_email_only(self, email: str) -> None:
        """Enter only the email field, leave password empty."""
        email_field = self._find_element('email')
        email_field.clear()
        email_field.fill(email)

    def enter_password_only(self, password: str) -> None:
        """Enter only the password field, leave email empty."""
        password_field = self._find_element('password')
        password_field.clear()
        password_field.fill(password)
    
    def enter_valid_credentials(self, email: Optional[str] = None, password: Optional[str] = None) -> None:
        """Enter valid login credentials.
        
        Args:
            email: Email to use for login. If None, uses from environment or test data.
            password: Password to use for login. If None, uses from environment or test data.
        """
        # Get credentials from parameters, environment variables, or test data
        email = email or os.getenv('MANUAL_EMAIL') or self.test_data.get('prod_email')
        password = password or os.getenv('MANUAL_PASSWORD') or self.test_data.get('prod_pass')
        
        if not email or not password:
            raise ValueError("Email and password must be provided or set in environment variables")
            
        self.enter_credentials(email, password)
    
    def click_sign_in(self) -> None:
        """Click the sign in button."""
        sign_in_button = self._find_element('sign_in')
        # Do not assume navigation will occur (validation may keep us on the same page)
        sign_in_button.click()
    
    def verify_error_message(self, expected_text: str = "Invalid credentials") -> None:
        """Verify that the error message is displayed.
        
        Args:
            expected_text: Expected text in the error message
        """
        error_message = self._find_element('error_message')
        expect(error_message).to_be_visible()
        if expected_text:
            expect(error_message).to_contain_text(expected_text)
    
    def verify_validation_message_for_empty_fields(self) -> None:
        """Verify that validation messages for empty fields are displayed."""
        validation_message = self._find_element('validation_message')
        expect(validation_message).to_be_visible()
        expect(validation_message).to_contain_text("required")
    
    def perform_login(self, base_url: str, email: Optional[str] = None, 
                     password: Optional[str] = None) -> None:
        """Perform a complete login with the given credentials.
        
        Args:
            base_url: Base URL of the application
            email: Email to use for login. If None, uses from environment or test data.
            password: Password to use for login. If None, uses from environment or test data.
        """
        logger.info("Performing login")
        self.navigate_to_prod_env(base_url)
        self.maximize_window()
        self.enter_valid_credentials(email, password)
        self.click_sign_in()
        
        # Wait for navigation to complete
        self.page.wait_for_url("**/dashboard", timeout=10000)
        
        # Verify successful login by checking for a logged-in element
        try:
            # Try to find a logged-in indicator (adjust selector as needed)
            self.page.wait_for_selector("button:has-text('Logout')", timeout=5000)
            logger.info("Login successful")
        except PlaywrightTimeoutError:
            # If logout button not found, check for error messages
            try:
                error = self._find_element('error_message', timeout=2000)
                error_text = error.text_content()
                raise AssertionError(f"Login failed: {error_text}")
            except (TimeoutError, PlaywrightTimeoutError):
                # No error message found, but login might still have failed
                logger.warning("Login status unclear - no error message found"
                             "but logout button not visible")
    
    def is_logged_in(self) -> bool:
        """Check if the user is logged in.
        
        Returns:
            bool: True if logged in, False otherwise
        """
        try:
            # Check for a logged-in indicator (adjust selector as needed)
            return self.page.locator("button:has-text('Logout')").is_visible(timeout=3000)
        except PlaywrightTimeoutError:
            return False
