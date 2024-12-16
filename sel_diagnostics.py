from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import sys
import traceback
import subprocess
import platform
import json
import datetime

class ChromeDiagnostics:
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        self.chrome_options.add_argument("--verbose")
        self.chrome_options.add_argument("--log-level=3")
        self.driver = None

    def run_all_diagnostics(self):
        """Run all diagnostic checks"""
        print("=== Chrome Diagnostics Suite ===")
        print("-" * 50)
        
        # System Information
        print("System Information:")
        print(f"Python: {sys.version.split()[0]}")
        print(f"Selenium: {webdriver.__version__}")
        
        # Connection Diagnostics
        print("\nConnection Diagnostics:")
        port_active = self.verify_chrome_debug_port()
        if not port_active:
            print("ERROR: Debug port check failed")
            return
        
        connection_success = self.test_chrome_connection()
        if not connection_success:
            print("ERROR: Chrome connection failed")
            return
        
        # Page Analysis
        self.analyze_page_structure()
        self.cleanup()

    def verify_chrome_debug_port(self):
        """Check if debug port is active"""
        system = platform.system()
        try:
            if system == "Darwin":
                result = subprocess.run(['lsof', '-i', ':9222'], capture_output=True, text=True)
            elif system == "Windows":
                result = subprocess.run(['netstat', '-ano', '|', 'findstr', '9222'], 
                                     capture_output=True, text=True, shell=True)
            else:  # Linux
                result = subprocess.run(['ss', '-tuln', '| grep 9222'], 
                                     capture_output=True, text=True, shell=True)
            
            if result.stdout:
                print("Debug port 9222: ACTIVE")
                return True
            print("Debug port 9222: NOT FOUND")
            print(f"System: {system}")
            return False
            
        except Exception as e:
            print(f"Port check failed: {str(e)}")
            print(f"System: {system}")
            return False

    def test_chrome_connection(self):
        """Test basic Chrome connection"""
        try:
            # Add page load timeout
            service = Service()
            self.driver = webdriver.Chrome(service=service, options=self.chrome_options)
            self.driver.set_page_load_timeout(10)  # 10 second timeout
            
            # Test connection with timeout
            current_url = self.driver.current_url if self.driver.current_url else "No URL available"
            print("Chrome connection: SUCCESS")
            print(f"Current URL: {current_url}")
            return True
            
        except webdriver.TimeoutException:
            print("Chrome connection timed out after 10 seconds")
            return False
        except Exception as e:
            print(f"Chrome connection failed: {str(e)}")
            print("Detailed error:", traceback.format_exc())
            return False

    def analyze_page_structure(self):
        """Analyze current page structure"""
        print("\nPage Analysis:")
        try:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            print(f"Title: {soup.title.string if soup.title else 'None'}")
            
            # Count key elements
            elements = {
                'main': len(soup.find_all('main')),
                'job_related': len(self._find_job_elements(soup)),
                'forms': len(soup.find_all('form')),
                'links': len(soup.find_all('a'))
            }
            
            print("\nElement Counts:")
            for elem, count in elements.items():
                print(f"{elem}: {count}")
            
            # Save structure for detailed analysis
            structure_file = self._save_page_structure(soup)
            print(f"\nDetailed structure saved: {structure_file}")
            
        except Exception as e:
            print(f"Page analysis failed: {str(e)}")

    def _find_job_elements(self, soup):
        """Find job-related elements"""
        job_terms = ['job', 'title', 'company', 'description', 'requirements']
        return [item for item in soup.find_all(['h1', 'h2', 'section', 'div'])
                if any(term in item.get_text().lower() for term in job_terms)]

    def _save_page_structure(self, soup):
        """Save page structure to JSON"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'page_structure_{timestamp}.json'
            
            structure = {
                'url': self.driver.current_url,
                'title': soup.title.string if soup.title else None,
                'headers': [{'tag': h.name, 'class': h.get('class'), 
                            'id': h.get('id')} 
                           for h in soup.find_all(['h1', 'h2', 'h3'])],
                'main_sections': [{'tag': s.name, 'class': s.get('class'), 
                                 'id': s.get('id')} 
                                for s in soup.find_all('section')]
            }
            
            with open(filename, 'w') as f:
                json.dump(structure, f, indent=2)
            return filename
            
        except Exception as e:
            print(f"Failed to save structure: {str(e)}")
            return None

    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            try:
                self.driver.quit()
                print("\nDriver: Closed")
            except Exception as e:
                print(f"\nDriver cleanup failed: {str(e)}")

if __name__ == "__main__":
    try:
        diagnostics = ChromeDiagnostics()
        diagnostics.run_all_diagnostics()
    except KeyboardInterrupt:
        print("\nDiagnostics interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        traceback.print_exc()
