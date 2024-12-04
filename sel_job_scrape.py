from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import json
import datetime
import pyperclip
import os

def format_for_clipboard(job_data):
    """Format job data for clipboard in CSV format"""
    today = datetime.datetime.now().strftime("%m/%d/%Y")
    
    # Format matches the test case format
    fields = [
        job_data.get('company', ''),
        job_data.get('title', ''),
        job_data.get('location', '') + (' (Remote)' if job_data.get('is_remote', False) else ''),
        '',  # URL (empty)
        today,  # Date
        'LinkedIn',  # Source
        today,  # DateApplied
        '',  # InitialResponse
        '',  # Reject
        '',  # Screen
        '',  # FirstRound
        '',  # SecondRound
        '',  # Notes
        job_data.get('salary', ''),
        job_data.get('posted', ''),
        job_data.get('applicants', '')
    ]
    
    return '"' + '","'.join(str(field) if field is not None else '' for field in fields) + '"'

def parse_tab_title(title):
    """Parse tab title to extract job title and company name"""
    if not title or '|' not in title:
        return None, None
    
    parts = [part.strip() for part in title.split('|')]
    if len(parts) >= 2:
        job_title = parts[0]
        company_name = parts[1]
        # Remove "LinkedIn" if it's in the company name
        company_name = company_name.replace('LinkedIn', '').strip()
        return job_title, company_name
    return None, None

def extract_linkedin_job():
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 10)
        
        # Get and print current tab title and URL
        current_title = driver.title
        current_url = driver.current_url
        print("\nCurrent Tab:")
        print(f"Title: {current_title}")
        print(f"URL: {current_url}")
        print("-" * 50)
        
        job_data = {
            'company': '',
            'title': '',
            'location': '',
            'salary': '',
            'description': '',
            'is_remote': False,
            'posted': '',
            'applicants': '',
            'source_tab': current_title,
            'source_url': current_url
        }
        
        # Try to extract from tab title first
        tab_title, tab_company = parse_tab_title(current_title)
        if tab_company:
            job_data['company'] = tab_company
        if tab_title:
            job_data['title'] = tab_title
        
        # Continue with existing extraction methods as fallback
        if not job_data['company'] or not job_data['title']:
            # Job Title
            try:
                title = driver.find_element(By.CSS_SELECTOR, "h1.t-24.t-bold.inline").text
                job_data['title'] = title
            except Exception as e:
                print(f"Error getting title: {e}")
            
            # About the job section
            try:
                job_description = driver.find_element(
                    By.XPATH, 
                    "//h2[contains(@class, 'text-heading-large') and text()='About the job']/following-sibling::div"
                ).text
                job_data['description'] = job_description
            except Exception as e:
                print(f"Error getting description: {e}")
            
            # Company info
            try:
                company = None
                
                # Strategy 1: Try company link with specific text content
                company_selectors = [
                    "//a[contains(@href, '/company/') and not(contains(text(), 'Premium'))]",
                    "//a[@data-tracking-control-name='public_jobs_company_name']",
                    "//div[contains(@class, 'job-details-jobs-unified-top-card__company-name')]//a",
                    "//span[contains(@class, 'jobs-unified-top-card__company-name')]//a",
                    "//div[contains(@class, 'jobs-company__box')]//a[contains(@href, '/company/')]"
                ]
                
                for selector in company_selectors:
                    try:
                        element = driver.find_element(By.XPATH, selector)
                        if element and element.text:
                            company_text = element.text.strip()
                            if (company_text and 
                                'premium' not in company_text.lower() and 
                                'show more' not in company_text.lower() and
                                'insights' not in company_text.lower()):
                                company = company_text
                                break
                    except:
                        continue
                
                # Strategy 2: Try finding company name in the top card section
                if not company:
                    top_card_selectors = [
                        ".job-details-jobs-unified-top-card__company-name",
                        ".jobs-unified-top-card__company-name",
                        ".jobs-company__name",
                        "div[data-test-id='job-company-name']"
                    ]
                    for selector in top_card_selectors:
                        try:
                            element = driver.find_element(By.CSS_SELECTOR, selector)
                            if element and element.text:
                                company_text = element.text.strip()
                                if ('premium' not in company_text.lower() and 
                                    'show more' not in company_text.lower()):
                                    company = company_text
                                    break
                        except:
                            continue
                
                # Strategy 3: Try finding within the company info section
                if not company:
                    try:
                        company_section = driver.find_element(
                            By.XPATH, 
                            "//section[contains(@class, 'jobs-company')]//div[contains(@class, 'company-name')]"
                        )
                        if company_section and company_section.text:
                            company_text = company_section.text.strip()
                            if ('premium' not in company_text.lower() and 
                                'show more' not in company_text.lower()):
                                company = company_text
                    except:
                        pass
                
                if company:
                    job_data['company'] = company
                else:
                    print("Could not determine company name")
                    
            except Exception as e:
                print(f"Error in company extraction: {e}")
            
            # Salary info - try multiple approaches but don't error if not found
            try:
                salary_selectors = [
                    "//h3[contains(@class, 'jobs-details-premium-insight__title') and text()='Applicants for this job']/following-sibling::div",
                    "//span[contains(text(), 'Salary') or contains(text(), 'Pay')]/following-sibling::*",
                    "//div[contains(@class, 'salary-range')]"
                ]
                
                for selector in salary_selectors:
                    try:
                        salary_element = driver.find_element(By.XPATH, selector)
                        if salary_element and salary_element.text:
                            job_data['salary'] = salary_element.text.strip()
                            break
                    except:
                        continue
                
                if not job_data['salary']:
                    print("Note: No salary information found in posting")
            
            except Exception as e:
                print(f"Note: Could not extract salary: {e}")
            
            # Location and remote status (trying multiple selectors)
            try:
                location_selectors = [
                    ".job-details-jobs-unified-top-card__primary-description",
                    ".jobs-unified-top-card__bullet",
                    ".job-details-jobs-unified-top-card__workplace-type"
                ]
                
                for selector in location_selectors:
                    try:
                        location_text = driver.find_element(By.CSS_SELECTOR, selector).text.lower()
                        job_data['is_remote'] = 'remote' in location_text
                        job_data['location'] = location_text.replace('remote', '').strip()
                        if job_data['location']:
                            break
                    except:
                        continue
            except Exception as e:
                print(f"Error getting location: {e}")
            
            # Posted date and applicants
            try:
                metadata_selectors = [
                    ".jobs-unified-top-card__subtitle-secondary-grouping",
                    ".jobs-unified-top-card__posted-date"
                ]
                
                for selector in metadata_selectors:
                    try:
                        metadata = driver.find_element(By.CSS_SELECTOR, selector).text
                        if 'ago' in metadata:
                            job_data['posted'] = metadata.split('·')[0].strip()
                        if 'applicants' in metadata.lower():
                            job_data['applicants'] = ''.join(filter(str.isdigit, metadata))
                        break
                    except:
                        continue
            except Exception as e:
                print(f"Error getting metadata: {e}")
            
            # Format and copy to clipboard
            clipboard_text = format_for_clipboard(job_data)
            try:
                pyperclip.copy(clipboard_text)
                print("\nCopied to clipboard:")
                print(clipboard_text)
            except Exception as e:
                print(f"Error copying to clipboard: {e}")
            
            # Print human-readable output
            print("\nJob Details:")
            for key, value in job_data.items():
                if value and key not in ['description']:  # Skip long description
                    print(f"{key.replace('_', ' ').title()}: {value}")
            
            # Save snapshot
            os.makedirs('snapshots', exist_ok=True)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            snapshot_file = f'snapshots/linkedin_snapshot_{timestamp}.json'
            with open(snapshot_file, 'w') as f:
                json.dump(job_data, f, indent=2)
            print(f"\nSnapshot saved: {snapshot_file}")
            
            return job_data
        
        # Format and copy to clipboard
        clipboard_text = format_for_clipboard(job_data)
        try:
            pyperclip.copy(clipboard_text)
            print("\nCopied to clipboard:")
            print(clipboard_text)
        except Exception as e:
            print(f"Error copying to clipboard: {e}")
        
        # Print human-readable output
        print("\nJob Details:")
        for key, value in job_data.items():
            if value and key not in ['description']:  # Skip long description
                print(f"{key.replace('_', ' ').title()}: {value}")
        
        # Save snapshot
        os.makedirs('snapshots', exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_file = f'snapshots/linkedin_snapshot_{timestamp}.json'
        with open(snapshot_file, 'w') as f:
            json.dump(job_data, f, indent=2)
        print(f"\nSnapshot saved: {snapshot_file}")
        
        return job_data
        
    except Exception as e:
        print(f"Major error: {e}")
        return None
    finally:
        driver.quit()

if __name__ == "__main__":
    print("LinkedIn Job Extractor")
    print("-" * 50)
    extract_linkedin_job()