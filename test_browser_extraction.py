import argparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from src.extractors.browser import BrowserExtractor
import datetime
import pyperclip

def format_output(job_data):
    """Format job data for clipboard in CSV format"""
    today = datetime.datetime.now().strftime("%m/%d/%Y")
    
    fields = [
        job_data.company,
        job_data.title,
        job_data.location + (' (Remote)' if job_data.is_remote else ''),
        job_data.url,  # Include URL from extraction
        today,  # Date
        'LinkedIn',  # Source
        today,  # DateApplied
        '',  # InitialResponse
        '',  # Reject
        '',  # Screen
        '',  # FirstRound
        '',  # SecondRound
        '',  # Notes
        job_data.salary,
        job_data.posted,
        job_data.applicants
    ]
    
    return '"' + '","'.join(str(field) if field is not None else '' for field in fields) + '"'

def ensure_correct_window(driver):
    """
    Find and switch to the window with a LinkedIn job posting
    
    Args:
        driver: Selenium WebDriver instance
    
    Returns:
        bool: True if correct window found and switched, False otherwise
    """
    base_url = "https://www.linkedin.com/jobs"
    
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        current_url = driver.current_url
        
        # Check if URL starts with the LinkedIn jobs base URL and is not a collections page
        if (current_url.startswith(base_url) and 
            '/collections/' not in current_url and 
            '/search/' not in current_url):
            print(f"Found correct window: {current_url}")
            # Refresh the page to ensure all content is loaded
            driver.refresh()
            # Wait for page to load after refresh
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.common.by import By
            try:
                # Wait for job title to be present (indicating page is loaded)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h1.t-24"))
                )
                print("Page refreshed and loaded successfully")
            except Exception as e:
                print(f"Warning: Page refresh wait timed out: {e}")
            return True
    
    print("Could not find window with job posting")
    return False

def test_basic_extraction(debug=False):
    print("Testing Browser Extraction")
    print("-" * 50)
    
    try:
        # Initialize Chrome options for debugging
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        
        # Specify the user data directory and profile for macOS
        user_data_dir = "/Users/lalbers/Library/Application Support/Google/Chrome"
        chrome_options.add_argument(f"user-data-dir={user_data_dir}")
        chrome_options.add_argument("profile-directory=Profile 1")  # Specifically use Profile 1
        
        # Debug Chrome connection
        print("\nChrome Connection Details:")
        print(f"Connecting to debugging port: 9222")
        print(f"Using profile: Profile 1 (Lucas - lucas.b.albers@gmail.com)")
        
        # Initialize driver
        driver = webdriver.Chrome(options=chrome_options)
        
        # Verify we're connected to the correct profile
        if debug:
            try:
                print(f"\nConnected Profile Info:")
                print(f"Current URL: {driver.current_url}")
                print(f"Page Title: {driver.title}")
            except Exception as e:
                print(f"Error getting profile info: {e}")
        
        # Print window information before extraction
        print("\nWindow Information:")
        print(f"Total windows: {len(driver.window_handles)}")
        print(f"Current window handle: {driver.current_window_handle}")
        print("\nAll window handles:")
        for handle in driver.window_handles:
            driver.switch_to.window(handle)
            print(f"Handle: {handle}")
            print(f"Title: {driver.title}")
            print(f"URL: {driver.current_url}")
            print("-" * 30)
        
        # Ensure correct window is selected
        if not ensure_correct_window(driver):
            print("Failed to find correct job window")
            return
            
        # Initialize extractor with driver
        extractor = BrowserExtractor(driver)
        
        # Extract data with debug flag
        print("Attempting extraction...")
        job_data = extractor.extract(debug=debug)
        
        # Format and copy to clipboard
        clipboard_text = format_output(job_data)
        try:
            pyperclip.copy(clipboard_text)
            print("\nCopied to clipboard:")
            print(clipboard_text)
        except Exception as e:
            print(f"Error copying to clipboard: {e}")
        
        # Print results
        print("\nExtracted Data:")
        print(f"Title: {job_data.title}")
        print(f"Company: {job_data.company}")
        print(f"Location: {job_data.location}")
        print(f"Remote: {job_data.is_remote}")
        print(f"Salary: {job_data.salary}")
        print(f"Posted: {job_data.posted}")
        print(f"Applicants: {job_data.applicants}")
        print(f"URL: {job_data.url}")
        
    except Exception as e:
        print(f"\nError during extraction: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Test browser extraction')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    args = parser.parse_args()
    
    # Run test with debug flag
    test_basic_extraction(debug=args.debug) 