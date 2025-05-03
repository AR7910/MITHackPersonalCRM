import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LinkedInConnector:
    def __init__(self):
        """
        Initialize the LinkedIn connector with credentials from .env file
        """
        self.email = os.getenv("LINKEDIN_EMAIL")
        self.password = os.getenv("LINKEDIN_PASSWORD")
        self.browser = None
        
        if not self.email or not self.password:
            logger.warning("LinkedIn credentials not found in .env file")
    
    def setup_browser(self):
        """
        Set up the Chrome browser with options
        """
        try:
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")
            # Uncomment the line below to run in headless mode
            # chrome_options.add_argument("--headless")
            
            service = Service(ChromeDriverManager().install())
            self.browser = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("Browser setup successful")
            return True
        except Exception as e:
            logger.error(f"Error setting up browser: {str(e)}")
            return False
    
    def login(self):
        """
        Login to LinkedIn
        
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            if not self.browser:
                if not self.setup_browser():
                    return False
            
            logger.info("Logging in to LinkedIn...")
            self.browser.get("https://www.linkedin.com/login")
            
            # Wait for login fields to appear
            WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            
            # Enter credentials
            self.browser.find_element(By.ID, "username").send_keys(self.email)
            self.browser.find_element(By.ID, "password").send_keys(self.password)
            self.browser.find_element(By.ID, "password").send_keys(Keys.RETURN)
            
            # Wait for login to complete
            try:
                WebDriverWait(self.browser, 15).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'feed-identity-module')]"))
                )
                logger.info("Successfully logged in to LinkedIn")
                return True
            except:
                logger.error("Login failed or timeout occurred")
                return False
        except Exception as e:
            logger.error(f"Error during login: {str(e)}")
            return False
    
    def search_person(self, name, company=None):
        """
        Search for a person on LinkedIn
        
        Args:
            name: Person's name
            company: Company name (optional)
            
        Returns:
            str: URL of the first search result, or None if not found
        """
        try:
            if not self.browser:
                if not self.login():
                    return None
            
            # Construct search query
            search_query = name
            if company:
                search_query += f" {company}"
            
            logger.info(f"Searching for: {search_query}")
            
            # Navigate to search page
            search_url = f"https://www.linkedin.com/search/results/people/?keywords={search_query.replace(' ', '%20')}"
            self.browser.get(search_url)
            
            # Wait for results
            try:
                WebDriverWait(self.browser, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".search-results-container"))
                )
                
                # Get first result
                person_elements = self.browser.find_elements(By.CSS_SELECTOR, ".entity-result__title a")
                
                if person_elements:
                    profile_url = person_elements[0].get_attribute("href")
                    
                    # Clean up the URL to remove tracking parameters
                    if "?" in profile_url:
                        profile_url = profile_url.split("?")[0]
                    
                    logger.info(f"Found profile: {profile_url}")
                    return profile_url
                else:
                    logger.warning(f"No results found for {search_query}")
                    return None
            except Exception as e:
                logger.error(f"Error waiting for search results: {str(e)}")
                return None
        except Exception as e:
            logger.error(f"Error during person search: {str(e)}")
            return None
    
    def send_connection_request(self, profile_url, message=None):
        """
        Send a connection request to a LinkedIn profile
        
        Args:
            profile_url: LinkedIn profile URL
            message: Optional connection message
            
        Returns:
            bool: True if request sent successfully, False otherwise
        """
        try:
            if not self.browser:
                if not self.login():
                    return False
            
            logger.info(f"Navigating to profile: {profile_url}")
            self.browser.get(profile_url)
            
            # Wait for profile to load
            WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".pv-top-card"))
            )
            
            # Find the Connect button
            connect_buttons = self.browser.find_elements(By.XPATH, "//button[contains(.,'Connect')]")
            
            if not connect_buttons:
                more_buttons = self.browser.find_elements(By.XPATH, "//button[contains(.,'More')]")
                if more_buttons:
                    more_buttons[0].click()
                    time.sleep(1)
                    connect_buttons = self.browser.find_elements(By.XPATH, "//button[contains(.,'Connect')]")
            
            if connect_buttons:
                connect_buttons[0].click()
                
                # Check if there's an option to add a note
                if message:
                    try:
                        # Wait for the "Add a note" button
                        WebDriverWait(self.browser, 5).until(
                            EC.presence_of_element_located((By.XPATH, "//button[contains(.,'Add a note')]"))
                        )
                        
                        # Click "Add a note"
                        add_note_button = self.browser.find_element(By.XPATH, "//button[contains(.,'Add a note')]")
                        add_note_button.click()
                        
                        # Wait for the message field
                        WebDriverWait(self.browser, 5).until(
                            EC.presence_of_element_located((By.ID, "custom-message"))
                        )
                        
                        # Enter message (limit to 300 characters)
                        message_field = self.browser.find_element(By.ID, "custom-message")
                        message_field.send_keys(message[:300])
                        
                        # Send the request
                        send_button = self.browser.find_element(By.XPATH, "//button[contains(.,'Send')]")
                        send_button.click()
                        
                        logger.info(f"Connection request sent with message to {profile_url}")
                        return True
                    except Exception as e:
                        logger.warning(f"Could not add message, sending without message: {str(e)}")
                        # Just send without a message
                        send_button = self.browser.find_element(By.XPATH, "//button[contains(.,'Send')]")
                        send_button.click()
                        
                        logger.info(f"Connection request sent without message to {profile_url}")
                        return True
                else:
                    # Send without message
                    send_button = self.browser.find_element(By.XPATH, "//button[contains(.,'Send')]")
                    send_button.click()
                    
                    logger.info(f"Connection request sent without message to {profile_url}")
                    return True
            else:
                logger.warning(f"Connect button not found for {profile_url}")
                return False
        except Exception as e:
            logger.error(f"Error sending connection request: {str(e)}")
            return False
    
    def check_connection_status(self, profile_url):
        """
        Check the connection status of a LinkedIn profile
        
        Args:
            profile_url: LinkedIn profile URL
            
        Returns:
            str: Connection status ("Connected", "Pending", "Not Connected", or "Unknown")
        """
        try:
            if not self.browser:
                if not self.login():
                    return "Unknown"
                    
            logger.info(f"Checking connection status for: {profile_url}")
            self.browser.get(profile_url)
            
            # Wait for profile to load
            WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".pv-top-card"))
            )
            
            # Check if there's a "Message" button (indicating connected)
            message_buttons = self.browser.find_elements(By.XPATH, "//button[contains(.,'Message')]")
            if message_buttons:
                return "Connected"
                
            # Check if there's a "Pending" button
            pending_buttons = self.browser.find_elements(By.XPATH, "//button[contains(.,'Pending')]")
            if pending_buttons:
                return "Pending"
                
            # If neither, assume not connected
            return "Not Connected"
                
        except Exception as e:
            logger.error(f"Error checking connection status: {str(e)}")
            return "Unknown"
    
    def close(self):
        """
        Close the browser
        """
        if self.browser:
            self.browser.quit()
            self.browser = None
            logger.info("Browser closed")
