import argparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from src.extractors.browser import BrowserExtractor
import json
import pyperclip
import os
from src.config import get_chrome_options
from datetime import datetime

def format_output(job_data):
    """Format job data for clipboard in CSV format"""
    today = datetime.now().strftime("%m/%d/%Y")
    
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
    Find and switch to the window with a LinkedIn job posting, prioritizing:
    1. Single-tab windows with LinkedIn job postings
    2. Currently active window if it has a job posting
    3. Any other window with a job posting
    """
    base_url = "https://www.linkedin.com/jobs"
    current_handle = driver.current_window_handle
    
    def is_valid_job_url(url):
        return (url.startswith(base_url) and 
                '/collections/' not in url and 
                '/search/' not in url)
    
    def switch_and_validate(handle):
        driver.switch_to.window(handle)
        driver.refresh()
        try:
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.t-24")))
            print("Page refreshed and loaded successfully")
            return True
        except Exception as e:
            print(f"Warning: Page refresh wait timed out: {e}")
            return False

    # Get window information
    windows = {}
    window_urls = {}  # Track URLs per window title to identify single-tab windows
    
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        url = driver.current_url
        title = driver.title
        
        windows[handle] = {
            'url': url,
            'title': title,
            'is_valid': is_valid_job_url(url),
            'is_current': handle == current_handle,
            'window_count': len([h for h in driver.window_handles 
                               if driver.switch_to.window(h) or True and driver.title == title])
        }
        
        # Group by window title to identify single-tab windows
        if title not in window_urls:
            window_urls[title] = []
        window_urls[title].append(handle)
    
    # Switch back to original window after counting
    driver.switch_to.window(current_handle)
    
    # Priority 1: Single-tab windows with valid job posting
    single_tab_windows = [(handle, info) for handle, info in windows.items() 
                         if info['window_count'] == 1 and info['is_valid']]
    if single_tab_windows:
        handle, info = single_tab_windows[0]
        print(f"Found single-tab window with job posting: {info['url']}")
        return switch_and_validate(handle)
    
    # Priority 2: Current window if valid
    if windows[current_handle]['is_valid']:
        print(f"Current window has valid job posting: {windows[current_handle]['url']}")
        return switch_and_validate(current_handle)
    
    # Priority 3: Any other valid window
    for handle, info in windows.items():
        if info['is_valid']:
            print(f"Found alternative window with job posting: {info['url']}")
            return switch_and_validate(handle)
    
    print("Could not find window with job posting")
    return False

def test_basic_extraction(debug=False):
    print("Testing Browser Extraction")
    print("-" * 50)
    
    try:
        # Initialize Chrome options for debugging
        chrome_options = Options()
        chrome_config = get_chrome_options()
        chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{chrome_config['debug_port']}")
        
        # Use configured Chrome profile
        chrome_options.add_argument(f"user-data-dir={chrome_config['user_data_dir']}")
        chrome_options.add_argument(f"profile-directory={chrome_config['profile']}")
        
        # Debug Chrome connection
        if debug:
            print("\nChrome Connection Details:")
            print(f"Connecting to debugging port: {chrome_config['debug_port']}")
            print(f"Using profile: {chrome_config['profile']}")
        
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