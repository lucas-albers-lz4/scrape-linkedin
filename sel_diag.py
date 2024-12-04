from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import sys
import traceback

def diagnose_chrome_connection():
    print("Chrome Connection Diagnostic Script")
    print("-" * 50)
    
    try:
        # Detailed Chrome options
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        
        # Print system and environment details
        print(f"Python Version: {sys.version}")
        print(f"Selenium Version: {webdriver.__version__}")
        
        # Attempt to connect
        print("\nAttempting to connect to Chrome...")
        
        # Use Service with default ChromeDriver
        service = Service()
        
        # Verbose logging
        chrome_options.add_argument("--verbose")
        chrome_options.add_argument("--log-level=3")  # Minimal logging
        
        # Attempt connection
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Basic connection test
        print("\nConnection Successful!")
        print(f"Current URL: {driver.current_url}")
        print(f"Page Title: {driver.title}")
        
        return driver
    
    except Exception as e:
        print("\n=== ERROR DETAILS ===")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        print("\nFull Traceback:")
        traceback.print_exc()
        return None

def verify_chrome_debug_port():
    import subprocess
    import platform
    
    print("\nVerifying Chrome Debug Port:")
    
    # Platform-specific command to check port
    system = platform.system()
    
    if system == "Darwin":  # macOS
        try:
            result = subprocess.run(['lsof', '-i', ':9222'], capture_output=True, text=True)
            print(result.stdout)
        except Exception as e:
            print(f"Error checking port: {e}")
    
    elif system == "Windows":
        try:
            result = subprocess.run(['netstat', '-ano', '|', 'findstr', '9222'], capture_output=True, text=True, shell=True)
            print(result.stdout)
        except Exception as e:
            print(f"Error checking port: {e}")
    
    else:  # Linux
        try:
            result = subprocess.run(['ss', '-tuln', '| grep 9222'], capture_output=True, text=True, shell=True)
            print(result.stdout)
        except Exception as e:
            print(f"Error checking port: {e}")

if __name__ == "__main__":
    # First, verify the debug port
    verify_chrome_debug_port()
    
    # Then attempt to connect
    driver = diagnose_chrome_connection()
    
    if driver:
        try:
            driver.quit()
        except:
            pass
