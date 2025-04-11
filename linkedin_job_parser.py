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
import sys
from src.config import get_chrome_options
from datetime import datetime
from src.diagnostics.chrome import ChromeDiagnostics

def format_output(job_data):
    """Return CSV-formatted string for clipboard from job_data."""
    today = datetime.now().strftime("%m/%d/%Y")
    fields = [
        job_data.company,
        job_data.title,
        job_data.location + (' (Remote)' if job_data.is_remote else ''),
        job_data.url,
        today,
        'LinkedIn',
        today,
        '', '', '', '', '', '',
        job_data.salary,
        job_data.posted,
        job_data.applicants
    ]
    return '"' + '","'.join(str(field) if field is not None else '' for field in fields) + '"'

def is_valid_job_url(url: str, base_url: str = "https://www.linkedin.com/jobs") -> bool:
    """Return True if the URL is a LinkedIn job posting."""
    return (url.startswith(base_url) and '/collections/' not in url and '/search/' not in url)

def switch_and_validate_window(driver, handle: str, css_selector: str = "h1.t-24", timeout: int = 10) -> bool:
    """Switch to the window, refresh, and wait for css_selector to load."""
    driver.switch_to.window(handle)
    driver.refresh()
    try:
        wait = WebDriverWait(driver, timeout)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
        print("Page loaded in window:", handle)
        return True
    except Exception as e:
        print(f"Warning: Timeout in window {handle}: {e}")
        return False

def get_window_metadata(driver, current_handle: str) -> dict:
    """Collect metadata (URL, title, validity, etc.) for all browser windows."""
    metadata = {}
    title_counts = {}
    handles = driver.window_handles

    for handle in handles:
        driver.switch_to.window(handle)
        title = driver.title
        title_counts[title] = title_counts.get(title, 0) + 1

    for handle in handles:
        driver.switch_to.window(handle)
        url = driver.current_url
        title = driver.title
        metadata[handle] = {
            "url": url,
            "title": title,
            "is_valid": is_valid_job_url(url),
            "is_current": handle == current_handle,
            "window_count": title_counts[title]
        }

    driver.switch_to.window(current_handle)
    return metadata

def ensure_correct_window(driver) -> bool:
    """Select the job posting window based on priority and validate it."""
    current_handle = driver.current_window_handle
    windows = get_window_metadata(driver, current_handle)

    # Priority 1: Single-tab valid window
    single_tab_windows = [(handle, info) for handle, info in windows.items() if info['window_count'] == 1 and info['is_valid']]
    if single_tab_windows:
        selected_handle, info = single_tab_windows[0]
        print(f"Found single-tab job window: {info['url']}")
        return switch_and_validate_window(driver, selected_handle)

    # Priority 2: Current window if valid
    if windows[current_handle]['is_valid']:
        print(f"Current window valid: {windows[current_handle]['url']}")
        return switch_and_validate_window(driver, current_handle)

    # Priority 3: Any other valid window
    for handle, info in windows.items():
        if info['is_valid']:
            print(f"Found alternative job window: {info['url']}")
            return switch_and_validate_window(driver, handle)

    print("No valid job window found")
    return False

def test_basic_extraction(debug=False):
    """Test extraction: connect to a Chrome debugging instance and run extraction."""
    print("Testing Browser Extraction")
    print("-" * 50)
    try:
        chrome_options = Options()
        chrome_config = get_chrome_options()
        chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{chrome_config['debug_port']}")
        chrome_options.add_argument(f"user-data-dir={chrome_config['user_data_dir']}")
        chrome_options.add_argument(f"profile-directory={chrome_config['profile']}")

        if debug:
            print(f"\nChrome Debug - Port: {chrome_config['debug_port']}, Profile: {chrome_config['profile']}")

        try:
            driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            if "DevToolsActivePort" in str(e):
                print("\nERROR: Could not connect to Chrome debugging port.")
                print("Make sure Chrome is running with --remote-debugging-port=9222")
                print("Try running: ./chrome.debug.sh")
                sys.exit(1)
            elif "session not created" in str(e):
                print("\nERROR: Chrome version mismatch.")
                print("Make sure your ChromeDriver version matches your Chrome version.")
                sys.exit(1)
            else:
                print(f"\nERROR: {str(e)}")
                sys.exit(1)

        if debug:
            print(f"\nProfile Info: URL: {driver.current_url}, Title: {driver.title}")

        print("\nWindow Info:")
        print(f"Total windows: {len(driver.window_handles)}")
        print(f"Current handle: {driver.current_window_handle}")
        print("\nAll handles:")
        for handle in driver.window_handles:
            driver.switch_to.window(handle)
            print(f"Handle: {handle}")
            print(f"Title: {driver.title}")
            print(f"URL: {driver.current_url}")
            print("-" * 30)

        if not ensure_correct_window(driver):
            print("Failed to select valid job window")
            print("TIP: Make sure you have a LinkedIn job posting page open in one of your Chrome tabs")
            return

        extractor = BrowserExtractor(driver)
        print("Extracting data...")
        job_data = extractor.extract(debug=debug)
        clipboard_text = format_output(job_data)

        try:
            pyperclip.copy(clipboard_text)
            print("\nCopied to clipboard:")
            print(clipboard_text)
        except Exception as e:
            print(f"Clipboard error: {e}")

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
        print(f"Extraction error: {e}")
        import traceback
        traceback.print_exc()
        print("\nTIP: If Chrome is not running in debug mode, try running: ./chrome.debug.sh")
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='LinkedIn Job Parser - Extract job details from LinkedIn')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    parser.add_argument('--diagnose', action='store_true', help='Run Chrome connection diagnostics')
    args = parser.parse_args()
    
    if args.diagnose:
        print("Running Chrome connection diagnostics...")
        diagnostics = ChromeDiagnostics()
        diagnostics.run_all_diagnostics()
        sys.exit(0)
    
    test_basic_extraction(debug=args.debug) 