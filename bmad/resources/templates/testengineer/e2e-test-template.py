
"""
End-to-End Test Template voor BMAD TestEngineer Agent

Dit template bevat een uitgebreide E2E test structuur voor het testen van volledige
gebruikersflows van begin tot eind.

Best Practices:
- Test complete user journeys
- Simuleer realistische user interactions
- Test cross-browser en cross-device scenarios
- Implementeer visual regression testing
- Test accessibility en usability
- Verifieer business requirements end-to-end
"""

import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from typing import Dict, Any, Optional
import json
import logging
from selenium.webdriver.common.keys import Keys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class E2ETestBase:
    """Base class voor E2E tests met common functionality."""
    
    def __init__(self, headless: bool = True):
        self.driver = None
        self.wait = None
        self.headless = headless
        self.test_data = {}
        self.screenshots = []
    
    def setup_driver(self):
        """Setup WebDriver met configuratie."""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        self.driver.implicitly_wait(5)
        
        logger.info("WebDriver setup completed")
    
    def teardown_driver(self):
        """Cleanup WebDriver resources."""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver teardown completed")
    
    def take_screenshot(self, name: str):
        """Take screenshot voor debugging."""
        if self.driver:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{name}_{timestamp}.png"
            self.driver.save_screenshot(filename)
            self.screenshots.append(filename)
            logger.info(f"Screenshot saved: {filename}")
    
    def wait_for_element(self, by: By, value: str, timeout: int = 10):
        """Wait voor element om zichtbaar te zijn."""
        return self.wait.until(EC.visibility_of_element_located((by, value)))
    
    def wait_for_clickable(self, by: By, value: str, timeout: int = 10):
        """Wait voor element om clickable te zijn."""
        return self.wait.until(EC.element_to_be_clickable((by, value)))
    
    def scroll_to_element(self, element):
        """Scroll naar element."""
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.5)

class UserRegistrationFlow(E2ETestBase):
    """E2E test voor user registration flow."""
    
    def test_complete_registration_flow(self):
        """Test complete user registration flow van begin tot eind."""
        try:
            # Setup
            self.setup_driver()
            
            # Step 1: Navigate to registration page
            logger.info("Step 1: Navigating to registration page")
            self.driver.get("https://example.com/register")
            
            # Verify page loaded
            title = self.driver.title
            assert "Register" in title, f"Expected 'Register' in title, got: {title}"
            
            # Step 2: Fill registration form
            logger.info("Step 2: Filling registration form")
            
            # Fill name fields
            first_name_input = self.wait_for_element(By.ID, "first-name")
            first_name_input.clear()
            first_name_input.send_keys("John")
            
            last_name_input = self.wait_for_element(By.ID, "last-name")
            last_name_input.clear()
            last_name_input.send_keys("Doe")
            
            # Fill email field
            email_input = self.wait_for_element(By.ID, "email")
            email_input.clear()
            email_input.send_keys("john.doe@example.com")
            
            # Fill password fields
            password_input = self.wait_for_element(By.ID, "password")
            password_input.clear()
            password_input.send_keys("SecurePassword123!")
            
            confirm_password_input = self.wait_for_element(By.ID, "confirm-password")
            confirm_password_input.clear()
            confirm_password_input.send_keys("SecurePassword123!")
            
            # Step 3: Accept terms and conditions
            logger.info("Step 3: Accepting terms and conditions")
            terms_checkbox = self.wait_for_element(By.ID, "terms-checkbox")
            if not terms_checkbox.is_selected():
                terms_checkbox.click()
            
            # Step 4: Submit registration
            logger.info("Step 4: Submitting registration")
            submit_button = self.wait_for_clickable(By.ID, "register-button")
            submit_button.click()
            
            # Step 5: Verify email verification page
            logger.info("Step 5: Verifying email verification page")
            self.wait_for_element(By.ID, "verification-message")
            
            verification_text = self.driver.find_element(By.ID, "verification-message").text
            assert "verification email" in verification_text.lower(), "Email verification message not found"
            
            # Step 6: Verify user data in database (simulated)
            logger.info("Step 6: Verifying user data")
            # In real scenario, this would check database
            self.test_data["user_registered"] = True
            self.test_data["email"] = "john.doe@example.com"
            
            logger.info("Registration flow completed successfully")
            
        except Exception as e:
            self.take_screenshot("registration_error")
            logger.error(f"Registration flow failed: {e}")
            raise
        finally:
            self.teardown_driver()

class LoginFlow(E2ETestBase):
    """E2E test voor login flow."""
    
    def test_complete_login_flow(self):
        """Test complete login flow."""
        try:
            self.setup_driver()
            
            # Step 1: Navigate to login page
            logger.info("Step 1: Navigating to login page")
            self.driver.get("https://example.com/login")
            
            # Step 2: Fill login form
            logger.info("Step 2: Filling login form")
            email_input = self.wait_for_element(By.ID, "email")
            email_input.clear()
            email_input.send_keys("john.doe@example.com")
            
            password_input = self.wait_for_element(By.ID, "password")
            password_input.clear()
            password_input.send_keys("SecurePassword123!")
            
            # Step 3: Submit login
            logger.info("Step 3: Submitting login")
            login_button = self.wait_for_clickable(By.ID, "login-button")
            login_button.click()
            
            # Step 4: Verify successful login
            logger.info("Step 4: Verifying successful login")
            self.wait_for_element(By.ID, "dashboard")
            
            # Verify user is logged in
            user_menu = self.wait_for_element(By.ID, "user-menu")
            assert user_menu.is_displayed(), "User menu not displayed after login"
            
            # Step 5: Verify user data
            logger.info("Step 5: Verifying user data")
            user_name = self.driver.find_element(By.ID, "user-name").text
            assert "John Doe" in user_name, f"Expected 'John Doe' in user name, got: {user_name}"
            
            logger.info("Login flow completed successfully")
            
        except Exception as e:
            self.take_screenshot("login_error")
            logger.error(f"Login flow failed: {e}")
            raise
        finally:
            self.teardown_driver()

class ShoppingCartFlow(E2ETestBase):
    """E2E test voor shopping cart flow."""
    
    def test_complete_shopping_cart_flow(self):
        """Test complete shopping cart flow."""
        try:
            self.setup_driver()
            
            # Step 1: Login first
            logger.info("Step 1: Logging in")
            self.driver.get("https://example.com/login")
            
            email_input = self.wait_for_element(By.ID, "email")
            email_input.send_keys("john.doe@example.com")
            
            password_input = self.wait_for_element(By.ID, "password")
            password_input.send_keys("SecurePassword123!")
            
            login_button = self.wait_for_clickable(By.ID, "login-button")
            login_button.click()
            
            # Step 2: Browse products
            logger.info("Step 2: Browsing products")
            self.driver.get("https://example.com/products")
            
            # Wait for products to load
            self.wait_for_element(By.CLASS_NAME, "product-card")
            
            # Step 3: Add product to cart
            logger.info("Step 3: Adding product to cart")
            first_product = self.driver.find_element(By.CLASS_NAME, "product-card")
            add_to_cart_button = first_product.find_element(By.CLASS_NAME, "add-to-cart")
            
            # Scroll to product
            self.scroll_to_element(first_product)
            add_to_cart_button.click()
            
            # Step 4: Verify product added to cart
            logger.info("Step 4: Verifying product added to cart")
            cart_notification = self.wait_for_element(By.ID, "cart-notification")
            assert "added to cart" in cart_notification.text.lower(), "Product not added to cart"
            
            # Step 5: View cart
            logger.info("Step 5: Viewing cart")
            cart_icon = self.wait_for_clickable(By.ID, "cart-icon")
            cart_icon.click()
            
            # Step 6: Verify cart contents
            logger.info("Step 6: Verifying cart contents")
            cart_items = self.driver.find_elements(By.CLASS_NAME, "cart-item")
            assert len(cart_items) > 0, "No items in cart"
            
            # Step 7: Proceed to checkout
            logger.info("Step 7: Proceeding to checkout")
            checkout_button = self.wait_for_clickable(By.ID, "checkout-button")
            checkout_button.click()
            
            # Step 8: Verify checkout page
            logger.info("Step 8: Verifying checkout page")
            self.wait_for_element(By.ID, "checkout-form")
            
            logger.info("Shopping cart flow completed successfully")
            
        except Exception as e:
            self.take_screenshot("shopping_cart_error")
            logger.error(f"Shopping cart flow failed: {e}")
            raise
        finally:
            self.teardown_driver()

class PaymentFlow(E2ETestBase):
    """E2E test voor payment flow."""
    
    def test_complete_payment_flow(self):
        """Test complete payment flow."""
        try:
            self.setup_driver()
            
            # Step 1: Navigate to checkout
            logger.info("Step 1: Navigating to checkout")
            self.driver.get("https://example.com/checkout")
            
            # Step 2: Fill shipping information
            logger.info("Step 2: Filling shipping information")
            shipping_form = self.wait_for_element(By.ID, "shipping-form")
            
            # Fill address fields
            address_input = shipping_form.find_element(By.ID, "address")
            address_input.send_keys("123 Main Street")
            
            city_input = shipping_form.find_element(By.ID, "city")
            city_input.send_keys("Amsterdam")
            
            postal_code_input = shipping_form.find_element(By.ID, "postal-code")
            postal_code_input.send_keys("1000 AA")
            
            # Step 3: Fill payment information
            logger.info("Step 3: Filling payment information")
            payment_form = self.wait_for_element(By.ID, "payment-form")
            
            # Fill card details
            card_number_input = payment_form.find_element(By.ID, "card-number")
            card_number_input.send_keys("4111111111111111")  # Test card number
            
            expiry_input = payment_form.find_element(By.ID, "expiry")
            expiry_input.send_keys("12/25")
            
            cvv_input = payment_form.find_element(By.ID, "cvv")
            cvv_input.send_keys("123")
            
            # Step 4: Submit payment
            logger.info("Step 4: Submitting payment")
            pay_button = self.wait_for_clickable(By.ID, "pay-button")
            pay_button.click()
            
            # Step 5: Verify payment success
            logger.info("Step 5: Verifying payment success")
            success_message = self.wait_for_element(By.ID, "payment-success")
            assert "payment successful" in success_message.text.lower(), "Payment not successful"
            
            # Step 6: Verify order confirmation
            logger.info("Step 6: Verifying order confirmation")
            order_number = self.driver.find_element(By.ID, "order-number").text
            assert order_number.startswith("ORD"), f"Invalid order number: {order_number}"
            
            logger.info("Payment flow completed successfully")
            
        except Exception as e:
            self.take_screenshot("payment_error")
            logger.error(f"Payment flow failed: {e}")
            raise
        finally:
            self.teardown_driver()

class AccessibilityFlow(E2ETestBase):
    """E2E test voor accessibility compliance."""
    
    def test_accessibility_compliance(self):
        """Test accessibility compliance."""
        try:
            self.setup_driver()
            
            # Step 1: Navigate to main page
            logger.info("Step 1: Testing accessibility on main page")
            self.driver.get("https://example.com")
            
            # Step 2: Check for alt text on images
            logger.info("Step 2: Checking alt text on images")
            images = self.driver.find_elements(By.TAG_NAME, "img")
            for img in images:
                alt_text = img.get_attribute("alt")
                assert alt_text is not None, f"Image missing alt text: {img.get_attribute('src')}"
            
            # Step 3: Check for proper heading structure
            logger.info("Step 3: Checking heading structure")
            headings = self.driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3, h4, h5, h6")
            heading_levels = [int(h.tag_name[1]) for h in headings]
            
            # Verify no skipped heading levels
            for i in range(len(heading_levels) - 1):
                assert heading_levels[i+1] - heading_levels[i] <= 1, "Skipped heading level detected"
            
            # Step 4: Check for keyboard navigation
            logger.info("Step 4: Testing keyboard navigation")
            focusable_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                "a, button, input, select, textarea, [tabindex]")
            
            for element in focusable_elements:
                # Test tab navigation
                element.send_keys(Keys.TAB)
                assert element == self.driver.switch_to.active_element, "Tab navigation not working"
            
            # Step 5: Check for ARIA labels
            logger.info("Step 5: Checking ARIA labels")
            elements_with_aria = self.driver.find_elements(By.CSS_SELECTOR, "[aria-label], [aria-labelledby]")
            assert len(elements_with_aria) > 0, "No ARIA labels found"
            
            logger.info("Accessibility compliance test completed successfully")
            
        except Exception as e:
            self.take_screenshot("accessibility_error")
            logger.error(f"Accessibility test failed: {e}")
            raise
        finally:
            self.teardown_driver()

class PerformanceFlow(E2ETestBase):
    """E2E test voor performance metrics."""
    
    def test_page_performance(self):
        """Test page performance metrics."""
        try:
            self.setup_driver()
            
            # Step 1: Navigate to page and measure load time
            logger.info("Step 1: Measuring page load time")
            start_time = time.time()
            
            self.driver.get("https://example.com")
            
            # Wait for page to fully load
            self.wait_for_element(By.TAG_NAME, "body")
            
            end_time = time.time()
            load_time = end_time - start_time
            
            # Verify load time is acceptable (< 3 seconds)
            assert load_time < 3.0, f"Page load time too slow: {load_time:.2f}s"
            
            # Step 2: Measure resource loading
            logger.info("Step 2: Measuring resource loading")
            performance_entries = self.driver.execute_script(
                "return window.performance.getEntriesByType('resource');"
            )
            
            total_resources = len(performance_entries)
            total_size = sum(entry.get('transferSize', 0) for entry in performance_entries)
            
            # Verify reasonable resource count and size
            assert total_resources < 50, f"Too many resources: {total_resources}"
            assert total_size < 5 * 1024 * 1024, f"Total size too large: {total_size} bytes"
            
            # Step 3: Test user interaction responsiveness
            logger.info("Step 3: Testing interaction responsiveness")
            
            # Test button click responsiveness
            button = self.wait_for_clickable(By.TAG_NAME, "button")
            
            start_time = time.time()
            button.click()
            end_time = time.time()
            
            response_time = end_time - start_time
            assert response_time < 0.5, f"Button response too slow: {response_time:.3f}s"
            
            logger.info("Performance test completed successfully")
            
        except Exception as e:
            self.take_screenshot("performance_error")
            logger.error(f"Performance test failed: {e}")
            raise
        finally:
            self.teardown_driver()

# Test execution helpers
def run_e2e_test_suite():
    """Run complete E2E test suite."""
    test_classes = [
        UserRegistrationFlow,
        LoginFlow,
        ShoppingCartFlow,
        PaymentFlow,
        AccessibilityFlow,
        PerformanceFlow
    ]
    
    results = {}
    
    for test_class in test_classes:
        logger.info(f"Running {test_class.__name__}")
        try:
            test_instance = test_class()
            test_method = getattr(test_instance, f"test_complete_{test_class.__name__.lower()}")
            test_method()
            results[test_class.__name__] = "PASSED"
        except Exception as e:
            results[test_class.__name__] = f"FAILED: {e}"
            logger.error(f"{test_class.__name__} failed: {e}")
    
    return results

# Pytest fixtures
@pytest.fixture(scope="class")
def e2e_driver():
    """Fixture voor E2E test driver."""
    driver = None
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(options=chrome_options)
        yield driver
    finally:
        if driver:
            driver.quit()

@pytest.fixture
def test_data():
    """Fixture voor test data."""
    return {
        "valid_user": {
            "email": "test@example.com",
            "password": "TestPassword123!",
            "name": "Test User"
        },
        "invalid_user": {
            "email": "invalid@example.com",
            "password": "wrongpassword",
            "name": "Invalid User"
        }
    }

if __name__ == "__main__":
    # Run E2E test suite
    results = run_e2e_test_suite()
    
    print("\nE2E Test Results:")
    print("=" * 50)
    for test_name, result in results.items():
        print(f"{test_name}: {result}")
    
    # Calculate success rate
    passed = sum(1 for result in results.values() if result == "PASSED")
    total = len(results)
    success_rate = (passed / total) * 100
    
    print(f"\nSuccess Rate: {success_rate:.1f}% ({passed}/{total})")
