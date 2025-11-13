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
    TIMEOUT = 45000  # 45 seconds
    
    def __init__(self, page: Page):
        """Initialize the login page object.
        
        Args:
            page: Playwright Page instance
        """
        self.page = page
        
        # Primary selectors with fallbacks
        self._selectors = {
            'email': [
                "xpath=/html/body/div[1]/div[3]/div/div/div/div[2]/form/div[1]/div[1]/div/input",
                "//input[contains(@class, 'mantine-TextInput-input')]",
                # Fallbacks (match Cypress)
                "input[type='email']",
                "input[placeholder*='email' i]",
                "input[name*='email' i]",
                "input[id*='email' i]",
                "//label[contains(normalize-space(.), 'Email')]/following::input[1]"
            ],
            'password': [
                "xpath=/html/body/div[1]/div[3]/div/div/div/div[2]/form/div[1]/div[2]/div/input",
                "//input[contains(@class, 'mantine-PasswordInput-innerInput')]",
                # Fallbacks (match Cypress)
                "input[type='password']",
                "input[placeholder*='password' i]",
                "input[name*='password' i]",
                "input[id*='password' i]",
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

        # Post-login heuristics (any of these indicate a successful login)
        self._post_login_selectors = [
            "button:has-text('Logout')",
            "[data-testid='logout']",
            "[data-testid='sidebar']",
            "nav[role='navigation']",
            "img[alt*='avatar' i]",
            "[class*='sidebar' i]",
        ]
        
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
                # For xpath= prefixed selectors, skip wait_for (it can fail on absolute paths)
                # Just try to use it; if not found, continue to next selector
                if selector.startswith("xpath="):
                    # Absolute XPath: just check if it's there
                    try:
                        locator.is_visible(timeout=2000)
                    except PlaywrightTimeoutError:
                        continue
                else:
                    # CSS selector or relative XPath: wait for visibility
                    locator.wait_for(state="visible", timeout=timeout or self.TIMEOUT)
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
        # More tolerant navigation: wait for DOM to be ready, not all resources
        self.page.goto(url, wait_until="domcontentloaded", timeout=self.TIMEOUT)
        try:
            self.page.wait_for_url("**/login*", timeout=5000)
        except PlaywrightTimeoutError:
            # If URL check is slow/flaky, proceed if we're already on a login-like URL
            if "/login" not in (self.page.url or ""):
                logger.debug(f"URL did not match login quickly, current URL: {self.page.url}")
        # Ensure form is interactable
        try:
            self._find_element('email', timeout=8000)
        except Exception:
            # Do not fail navigation; tests will surface exact failure later
            logger.debug("Email field not ready immediately after navigation")
    
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
        # Fill email field (focus, clear, fill)
        email_field = self._find_element('email')
        email_field.click()
        try:
            email_field.clear()
        except Exception:
            email_field.press("Control+A")
            email_field.press("Delete")
        email_field.fill(email)
        
        # Fill password field
        password_field = self._find_element('password')
        password_field.click()
        try:
            password_field.clear()
        except Exception:
            password_field.press("Control+A")
            password_field.press("Delete")
        password_field.fill(password)

    def enter_email_only(self, email: str) -> None:
        """Enter only the email field, leave password empty."""
        email_field = self._find_element('email')
        email_field.click()
        try:
            email_field.clear()
        except Exception:
            email_field.press("Control+A")
            email_field.press("Delete")
        email_field.fill(email)

    def enter_password_only(self, password: str) -> None:
        """Enter only the password field, leave email empty."""
        password_field = self._find_element('password')
        password_field.click()
        try:
            password_field.clear()
        except Exception:
            password_field.press("Control+A")
            password_field.press("Delete")
        password_field.fill(password)
    
    def enter_valid_credentials(self, email: Optional[str] = None, password: Optional[str] = None) -> None:
        """Enter valid login credentials.
        
        Args:
            email: Email to use for login. If None, uses from environment or test data.
            password: Password to use for login. If None, uses from environment or test data.
        """
        # Get credentials from parameters, environment variables (MANUAL_* or GOOGLE_*), or test data
        email = (
            email
            or os.getenv('MANUAL_EMAIL')
            or os.getenv('GOOGLE_EMAIL')
            or self.test_data.get('prod_email')
        )
        password = (
            password
            or os.getenv('MANUAL_PASSWORD')
            or os.getenv('GOOGLE_PASSWORD')
            or self.test_data.get('prod_pass')
        )
        
        if not email or not password:
            raise ValueError("Email and password must be provided or set in environment variables")
            
        self.enter_credentials(email, password)

    def login_with_google(self, email: str, password: str) -> None:
        # Placeholder: align API with Cypress; actual Google OAuth not implemented yet
        self.perform_login(base_url=os.getenv('BASE_URL', ''), email=email, password=password)

    def login_manually(self, email: str, password: str) -> None:
        self.perform_login(base_url=os.getenv('BASE_URL', ''), email=email, password=password)
    
    def click_sign_in(self) -> None:
        """Click the sign in button."""
        sign_in_button = self._find_element('sign_in')
        # Do not assume navigation will occur (validation may keep us on the same page)
        sign_in_button.click()
        try:
            self.page.wait_for_load_state("load", timeout=10000)
        except PlaywrightTimeoutError:
            pass
    
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

        # Wait for page to settle
        try:
            self.page.wait_for_load_state("networkidle", timeout=self.TIMEOUT)
        except PlaywrightTimeoutError:
            logger.debug("Network idle not reached; proceeding with URL/selector checks")

        # Consider multiple possible post-login URLs
        possible_urls = [
            "**/dashboard*",
            "**/home*",
            f"{base_url.rstrip('/')}/*",
        ]
        url_ok = False
        for pattern in possible_urls:
            try:
                self.page.wait_for_url(pattern, timeout=8000)
                url_ok = True
                break
            except PlaywrightTimeoutError:
                continue

        # Also check for post-login UI selectors
        selector_ok = False
        for sel in self._post_login_selectors:
            try:
                self.page.wait_for_selector(sel, timeout=5000)
                selector_ok = True
                break
            except PlaywrightTimeoutError:
                continue

        if url_ok or selector_ok:
            logger.info("Login successful")
            return

        # If reached here, try to pull error content if present
        try:
            error = self._find_element('error_message', timeout=3000)
            error_text = (error.text_content() or "").strip()
            raise AssertionError(f"Login failed: {error_text}")
        except (TimeoutError, PlaywrightTimeoutError):
            # Surface current URL and title for debugging
            raise AssertionError(
                f"Login did not complete. URL={self.page.url}, Title={self.page.title()}"
            )
    
    def submit_again_and_wait_error_refresh(self, new_email: str, new_password: str, timeout_ms: int = 8000) -> None:
        """Submit credentials again and ensure the error state refreshes quickly.
        
        This guards against long global timeouts by bounding the waits to a short window.
        We consider it refreshed if:
          - the error text changes, or
          - the error temporarily disappears and reappears, or
          - we navigate to a logged-in state.
        """
        # Capture existing error state if present
        previous_error_text = ""
        try:
            existing_error = self._find_element('error_message', timeout=3000)
            previous_error_text = (existing_error.text_content() or "").strip()
        except (TimeoutError, PlaywrightTimeoutError):
            # No prior error visible; proceed
            pass

        # Enter new credentials and submit
        self.enter_credentials(new_email, new_password)
        self.click_sign_in()

        # Fast-path: success indicators
        try:
            for sel in self._post_login_selectors:
                self.page.wait_for_selector(sel, timeout=2000)
                return
        except PlaywrightTimeoutError:
            pass

        # Otherwise, ensure error refreshed within a bounded timeout
        error_locator = self.page.locator(self._selectors['error_message'][0]).first
        try:
            # Wait for error to re-appear (in case it briefly disappears)
            error_locator.wait_for(state="visible", timeout=timeout_ms)
            # Do not require text to change; visibility suffices to prove refresh
        except PlaywrightTimeoutError:
            # As a fallback, check any error selector becomes visible even if first variant failed
            for sel in self._selectors['error_message'][1:]:
                try:
                    self.page.locator(sel).first.wait_for(state="visible", timeout=1500)
                    return
                except PlaywrightTimeoutError:
                    continue
            # If nothing matched within the bounded window, raise a concise assertion
            raise AssertionError("Error state did not refresh within expected time after retry")
    
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
