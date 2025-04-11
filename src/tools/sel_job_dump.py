from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import json

def analyze_page_structure():
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        # Get page source
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        print("\n=== Page Analysis ===")
        
        # 1. Basic Page Info
        print(f"\nTitle tag: {soup.title.string if soup.title else 'No title found'}")
        
        # 2. Main content areas
        print("\nMain content sections:")
        for main in soup.find_all('main'):
            print(f"Main section ID: {main.get('id', 'No ID')} | Class: {main.get('class', 'No class')}")
        
        # 3. Look for job-specific elements
        print("\nPotential job elements:")
        elements_to_check = ['h1', 'h2', 'section', 'div']
        job_related_terms = ['job', 'title', 'company', 'description', 'requirements']
        
        for elem in elements_to_check:
            for item in soup.find_all(elem):
                # Check if element or its children contain job-related terms
                text = item.get_text().lower()
                class_name = ' '.join(item.get('class', [])).lower()
                id_name = item.get('id', '').lower()
                
                if any(term in text or term in class_name or term in id_name for term in job_related_terms):
                    print(f"\nFound relevant {elem}:")
                    print(f"  Class: {item.get('class', 'No class')}")
                    print(f"  ID: {item.get('id', 'No ID')}")
                    print(f"  First 100 chars: {text[:100]}...")
        
        # 4. Save full structure for detailed analysis
        with open('page_structure.json', 'w') as f:
            structure = {
                'url': driver.current_url,
                'title': soup.title.string if soup.title else None,
                'headers': [{'tag': h.name, 'class': h.get('class'), 'id': h.get('id'), 'text': h.get_text().strip()} 
                          for h in soup.find_all(['h1', 'h2', 'h3'])],
                'main_sections': [{'tag': s.name, 'class': s.get('class'), 'id': s.get('id')} 
                                for s in soup.find_all('section')]
            }
            json.dump(structure, f, indent=2)
            print("\nDetailed structure saved to 'page_structure.json'")
        
        return True
        
    except Exception as e:
        print(f"Error analyzing page: {str(e)}")
        return False
        
    finally:
        driver.quit()

if __name__ == "__main__":
    print("LinkedIn Page Structure Analyzer")
    print("-" * 50)
    analyze_page_structure()
