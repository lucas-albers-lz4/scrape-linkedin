import argparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.extractors.browser import BrowserExtractor
import json
import os
from src.config import get_chrome_options
import time

def test_basic_extraction(debug=False):
    """Test basic extraction from LinkedIn"""
    try:
        # Set up Chrome driver with options
        options = Options()
        options.debugger_address = "127.0.0.1:9222"
        driver = webdriver.Chrome(options=options)
        browser = BrowserExtractor(driver)

        # Find LinkedIn window
        linkedin_window = None
        for handle in driver.window_handles:
            driver.switch_to.window(handle)
            if "linkedin.com/jobs/search" in driver.current_url:
                linkedin_window = handle
                break

        if not linkedin_window:
            print("No LinkedIn jobs window found")
            return
            
        driver.switch_to.window(linkedin_window)
        
        # Wait for job cards to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "jobs-search-results__list"))
        )
        
        # Find all job cards
        job_cards = driver.find_elements(By.CLASS_NAME, "job-card-container")
        
        print(f"\nFound {len(job_cards)} jobs")
        
        # List and dismiss jobs
        for i, card in enumerate(job_cards, 1):
            try:
                title = card.find_element(By.CLASS_NAME, "job-card-list__title").text
                company = card.find_element(By.CLASS_NAME, "job-card-container__company-name").text
                print(f"{i}. {title} at {company}")
                
                # Find and click the dismiss button (SVG icon)
                dismiss_button = card.find_element(By.CSS_SELECTOR, "[aria-label^='Dismiss']")
                dismiss_button.click()
                
                print(f"Dismissed job {i}/{len(job_cards)}")
                
                # Small delay to prevent rate limiting
                time.sleep(1)
                
            except Exception as e:
                if debug:
                    print(f"Error dismissing job {i}: {str(e)}")
                continue
                
    except Exception as e:
        print(f"\nError during job dismissal: {str(e)}")
        if debug:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Test browser extraction')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    args = parser.parse_args()
    
    # Run test with debug flag
    test_basic_extraction(debug=args.debug) 