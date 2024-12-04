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

def test_basic_extraction(debug=False):
    print("Testing Browser Extraction")
    print("-" * 50)
    
    try:
        # Initialize Chrome options for debugging
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        
        # Initialize driver
        driver = webdriver.Chrome(options=chrome_options)
        
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