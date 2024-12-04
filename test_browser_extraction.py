import argparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from src.extractors.browser import BrowserExtractor

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