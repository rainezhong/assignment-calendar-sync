"""Simple Gradescope scraper using Selenium"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, WebDriverException,
    ElementNotInteractableException, StaleElementReferenceException
)
from datetime import datetime
import time
import re
import config
from date_parser import parse_gradescope_date
from utils import (
    logger, retry_on_failure, handle_common_errors, 
    handle_selenium_errors, safe_cleanup, ScrapingError
)


class GradescopeScraper:
    """Simple scraper to get assignments from Gradescope"""
    
    def __init__(self):
        self.driver = None
        self.logged_in = False
    
    @handle_common_errors
    def _setup_driver(self):
        """Initialize Chrome driver with basic options"""
        logger.debug("Setting up Chrome driver...")
        
        options = Options()
        if config.HEADLESS_BROWSER:
            options.add_argument('--headless')
            logger.debug("Running in headless mode")
        
        # Chrome options for stability
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-logging')
        options.add_argument('--log-level=3')
        
        try:
            if config.CHROMEDRIVER_PATH:
                logger.debug(f"Using ChromeDriver at: {config.CHROMEDRIVER_PATH}")
                self.driver = webdriver.Chrome(executable_path=config.CHROMEDRIVER_PATH, options=options)
            else:
                logger.debug("Using ChromeDriver from PATH")
                self.driver = webdriver.Chrome(options=options)
            
            logger.success("Chrome driver initialized successfully")
            
        except WebDriverException as e:
            error_msg = handle_selenium_errors(e)
            logger.error(f"Chrome driver setup failed: {error_msg}")
            raise ScrapingError(f"Chrome driver setup failed: {error_msg}")
        
        except Exception as e:
            logger.error(f"Unexpected error setting up Chrome driver: {e}")
            raise ScrapingError(f"Failed to start browser: {e}")
    
    @retry_on_failure(max_attempts=2, delay=3, exceptions=(TimeoutException, WebDriverException))
    @handle_common_errors
    def login(self):
        """Login to Gradescope with error handling"""
        if not self.driver:
            self._setup_driver()
        
        try:
            logger.info("Navigating to Gradescope login page...")
            self.driver.get('https://www.gradescope.com/login')
            
            # Wait for page to load
            wait = WebDriverWait(self.driver, 15)
            
            # Find and fill email field
            logger.debug("Looking for email field...")
            try:
                email_field = wait.until(EC.presence_of_element_located((By.ID, 'session_email')))
                email_field.clear()
                email_field.send_keys(config.GRADESCOPE_EMAIL)
                logger.debug("Email field filled")
            except TimeoutException:
                logger.error("Could not find email field - Gradescope login page may have changed")
                raise ScrapingError("Login page layout has changed - could not find email field")
            
            # Find and fill password field
            try:
                password_field = self.driver.find_element(By.ID, 'session_password')
                password_field.clear() 
                password_field.send_keys(config.GRADESCOPE_PASSWORD)
                logger.debug("Password field filled")
            except NoSuchElementException:
                logger.error("Could not find password field")
                raise ScrapingError("Login page layout has changed - could not find password field")
            
            # Submit form
            try:
                submit_button = self.driver.find_element(By.NAME, 'commit')
                submit_button.click()
                logger.debug("Login form submitted")
            except NoSuchElementException:
                logger.error("Could not find login submit button")
                raise ScrapingError("Login page layout has changed - could not find submit button")
            
            # Wait for redirect - more flexible check
            logger.debug("Waiting for login redirect...")
            try:
                # Wait for either account page or dashboard
                wait.until(lambda driver: 'login' not in driver.current_url.lower())
                time.sleep(2)  # Give page time to fully load
            except TimeoutException:
                logger.error("Login redirect timed out")
                # Check if we're still on login page
                if 'login' in self.driver.current_url.lower():
                    # Look for error messages
                    try:
                        error_elements = self.driver.find_elements(By.CSS_SELECTOR, '.alert-danger, .error, .flash-error')
                        if error_elements:
                            error_text = error_elements[0].text
                            logger.error(f"Gradescope login error: {error_text}")
                            raise ScrapingError(f"Login failed: {error_text}")
                    except:
                        pass
                    
                    raise ScrapingError("Login failed - check your email and password in .env file")
            
            # Final check that login was successful
            current_url = self.driver.current_url
            if 'login' in current_url.lower():
                logger.error(f"Still on login page after submission: {current_url}")
                raise ScrapingError("Login failed - please verify your Gradescope credentials")
            
            self.logged_in = True
            logger.success("Successfully logged into Gradescope")
            
        except ScrapingError:
            raise
        except (TimeoutException, WebDriverException) as e:
            error_msg = handle_selenium_errors(e)
            logger.error(f"Browser error during login: {error_msg}")
            raise ScrapingError(f"Login failed due to browser issue: {error_msg}")
        except Exception as e:
            logger.error(f"Unexpected error during login: {e}")
            raise ScrapingError(f"Login failed: {e}")
    
    def navigate_to_assignments(self):
        """Navigate to assignments page and get course list"""
        if not self.logged_in:
            raise Exception("Must login first")
        
        try:
            # Go to account page to see courses
            self.driver.get('https://www.gradescope.com/account')
            time.sleep(2)
            
            # Find all course links
            course_links = []
            course_elements = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/courses/"]')
            
            for element in course_elements:
                href = element.get_attribute('href')
                if '/courses/' in href and href not in course_links:
                    course_links.append(href)
            
            print(f"Found {len(course_links)} courses")
            return course_links
            
        except Exception as e:
            raise Exception(f"Failed to get course list: {e}")
    
    def extract_assignments(self):
        """Extract assignment names and due dates from all courses"""
        if not self.logged_in:
            raise Exception("Must login first")
        
        assignments = []
        course_urls = self.navigate_to_assignments()
        
        for course_url in course_urls:
            try:
                print(f"Scraping course: {course_url}")
                self.driver.get(course_url)
                time.sleep(2)
                
                # Get course name
                try:
                    course_name_element = self.driver.find_element(By.CSS_SELECTOR, 'h1.courseHeader--title, .courseHeader h1')
                    course_name = course_name_element.text.strip()
                except:
                    course_name = f"Course {course_url.split('/')[-1]}"
                
                # Find assignment table rows
                assignment_rows = self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr, .table tbody tr')
                
                for row in assignment_rows:
                    try:
                        # Look for assignment link
                        assignment_link = row.find_element(By.CSS_SELECTOR, 'a[href*="/assignments/"]')
                        assignment_name = assignment_link.text.strip()
                        
                        if not assignment_name:
                            continue
                        
                        # Try to extract due date from the row
                        due_date = None
                        due_date_text = None
                        
                        # Look for due date in various possible locations
                        date_selectors = [
                            'td:contains("Due")',
                            'td.submissionTimeChart--dueDate',
                            '[class*="due"]',
                            'td:nth-child(3)',  # Often in 3rd column
                            'td:nth-child(4)'   # Sometimes in 4th column
                        ]
                        
                        for selector in date_selectors:
                            try:
                                if ':contains' in selector:
                                    # Use XPath for text-based search
                                    elements = self.driver.find_elements(By.XPATH, f"//td[contains(text(), 'Due')]")
                                else:
                                    elements = row.find_elements(By.CSS_SELECTOR, selector)
                                
                                for element in elements:
                                    text = element.text.strip()
                                    if text and text != '--':
                                        due_date_text = text
                                        due_date = parse_gradescope_date(text)
                                        if due_date:
                                            break
                                
                                if due_date:
                                    break
                            except:
                                continue
                        
                        assignment = {
                            'name': assignment_name,
                            'course': course_name,
                            'due_date': due_date,
                            'due_date_text': due_date_text,
                            'url': assignment_link.get_attribute('href')
                        }
                        
                        assignments.append(assignment)
                        
                        if due_date:
                            print(f"  Found: {assignment_name} (Due: {due_date.strftime('%Y-%m-%d %H:%M')})")
                        else:
                            print(f"  Found: {assignment_name} (No due date)")
                        
                    except Exception as e:
                        # Skip this row if we can't parse it
                        continue
                
            except Exception as e:
                print(f"  Error scraping course {course_url}: {e}")
                continue
        
        print(f"\nTotal assignments extracted: {len(assignments)}")
        return assignments
    
    
    def cleanup(self):
        """Close browser and cleanup"""
        logger.debug("Cleaning up scraper resources...")
        safe_cleanup(lambda: self.driver.quit() if self.driver else None, "Chrome driver")
        self.driver = None
        self.logged_in = False
        logger.debug("Scraper cleanup completed")
    
    def get_assignments(self):
        """Main method to login and get all assignments"""
        try:
            self.login()
            return self.extract_assignments()
        except Exception as e:
            print(f"Error getting assignments: {e}")
            raise


def test_scraper():
    """Test function that runs scraper without making changes"""
    print("=" * 50)
    print("Testing Gradescope Scraper (Read-Only)")
    print("=" * 50)
    
    scraper = GradescopeScraper()
    
    try:
        # Test the scraping functionality
        assignments = scraper.get_assignments()
        
        print("\n" + "=" * 50)
        print("SCRAPING RESULTS")
        print("=" * 50)
        
        if assignments:
            # Group by course
            by_course = {}
            for assignment in assignments:
                course = assignment['course']
                if course not in by_course:
                    by_course[course] = []
                by_course[course].append(assignment)
            
            print(f"\nFound {len(assignments)} assignments across {len(by_course)} courses:")
            
            for course, course_assignments in by_course.items():
                print(f"\n📚 {course}:")
                for assignment in course_assignments:
                    if assignment['due_date']:
                        print(f"  ✓ {assignment['name']} - Due: {assignment['due_date'].strftime('%Y-%m-%d %H:%M')}")
                    else:
                        print(f"  • {assignment['name']} - No due date")
        else:
            print("No assignments found. This could mean:")
            print("  - No courses enrolled")
            print("  - No assignments posted")
            print("  - Page structure has changed")
        
        print("\n" + "=" * 50)
        print("Test completed successfully!")
        print("=" * 50)
        
        return assignments
        
    except Exception as e:
        print(f"\nScraper test failed: {e}")
        return None
    
    finally:
        scraper.cleanup()


if __name__ == '__main__':
    test_scraper()