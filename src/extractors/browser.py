from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from .base import JobExtractor
from ..models.job import JobData
from ..utils.selectors import (
    LINKEDIN_SELECTORS,
    LINKEDIN_VERSION_INDICATORS,
    LINKEDIN_LOGIN_INDICATORS,
    LINKEDIN_PATTERNS,
    LINKEDIN_VERSION_SELECTORS
)
import re
from datetime import datetime, timedelta
import json

class BrowserExtractor(JobExtractor):
    def __init__(self, driver):
        self.driver = driver
        self.debug = False
        self.logged_in = False

    def _initialize_driver(self):
        # Mock for testing
        return None

    def connect(self):
        """Ensure connection is active"""
        try:
            self.driver.current_url
        except:
            raise ConnectionError("Browser connection lost")

    def _detect_page_version(self):
        """Detect which version of LinkedIn page we're dealing with"""
        for version, indicator in LINKEDIN_VERSION_INDICATORS.items():
            try:
                if self.driver.find_element(By.CLASS_NAME, indicator):
                    print(f"Detected LinkedIn version: {version}")
                    return version
            except:
                continue
        
        print("Could not detect LinkedIn version")
        return None

    def _check_login_status(self):
        """Check if we're logged into LinkedIn"""
        for indicator in LINKEDIN_LOGIN_INDICATORS.values():
            try:
                self.driver.find_element(By.CLASS_NAME, indicator)
                self.logged_in = True
                print("Detected logged-in state")
                return
            except:
                continue
        
        self.logged_in = False
        print("Not logged in - some data may be unavailable")

    def _parse_tab_title(self, title: str) -> tuple[str, str]:
        """Parse tab title to extract job title and company"""
        try:
            if not title:
                return None, None
            
            # Common LinkedIn title formats:
            # "(2) Job Title | Company | LinkedIn"
            # "Job Title | Company | LinkedIn"
            # "Job Title at Company | LinkedIn"
            
            # Remove notification count if present
            if title.startswith('('):
                title = title.split(')', 1)[1].strip()
            
            # Handle "at Company" format
            if ' at ' in title:
                parts = title.split(' at ')
                if len(parts) >= 2:
                    job_title = parts[0].strip()
                    company = parts[1].split('|')[0].strip()
                    return job_title, company
            
            # Handle standard separator format
            if '|' in title:
                parts = [part.strip() for part in title.split('|')]
                if len(parts) >= 2:
                    job_title = parts[0]
                    # Remove "LinkedIn" and any other trailing parts
                    company = parts[1].replace('LinkedIn', '').strip()
                    return job_title, company
                
            return None, None
            
        except Exception as e:
            print(f"Warning: Error parsing tab title: {str(e)}")
            return None, None

    def _parse_relative_date(self, text: str, debug: bool = False) -> datetime:
        """Parse relative date text into a datetime object"""
        if debug:
            print(f"Debug: Parsing relative date from: {text}")
        
        # Clean up the text by removing extra whitespace and dots
        text = ' '.join(text.strip().split())
        
        for pattern in LINKEDIN_SELECTORS['posted_patterns']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    amount = int(match.group(1))
                    unit = text.lower()  # Use the full text for unit detection
                    
                    if debug:
                        print(f"Debug: Found amount: {amount}, unit: {unit}")
                    
                    now = datetime.now()
                    
                    if 'minute' in unit:
                        return now - timedelta(minutes=amount)
                    elif 'hour' in unit:
                        return now - timedelta(hours=amount)
                    elif 'day' in unit:
                        return now - timedelta(days=amount)
                    elif 'week' in unit:
                        return now - timedelta(weeks=amount)
                    elif 'month' in unit:
                        return now - timedelta(days=amount * 30)  # Approximate
                    
                except ValueError as e:
                    if debug:
                        print(f"Debug: Error parsing number: {e}")
                    continue
                
        return None

    def _extract_with_selectors(self, job_data: JobData, debug: bool = False):
        """Extract data using all available selectors"""
        SELECTOR_TIMEOUT = 1
        
        # Try to extract salary information using different selectors
        for selector in LINKEDIN_SELECTORS['salary']:
            try:
                if selector.startswith('//'):
                    if debug:
                        print(f"Debug: Trying XPath selector: {selector}")
                    elements = self.driver.find_elements(By.XPATH, selector)
                else:
                    if debug:
                        print(f"Debug: Trying CSS selector: {selector}")
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                
                if elements:
                    for element in elements:
                        text = element.text
                        if debug:
                            print(f"Debug: Found text: {text}")
                        
                        # Try all salary patterns
                        try:
                            for pattern in LINKEDIN_SELECTORS['salary_patterns']:
                                salary_match = re.search(pattern, text)
                                if salary_match:
                                    job_data.salary = salary_match.group(0)
                                    if debug:
                                        print(f"Debug: Found salary: {job_data.salary}")
                                    return
                        except Exception as e:
                            if debug:
                                print(f"Debug: Error matching salary pattern: {str(e)}")
                            continue
                else:
                    if debug:
                        print(f"Debug: No elements found for selector: {selector}")
                    
            except Exception as e:
                if debug:
                    print(f"Debug: Error with selector '{selector}': {str(e)}")
                continue

        if debug and not job_data.salary:
            print("\nDebug: No salary found with any selector")

        # Extract posted date
        if debug:
            print("\nDebug: Starting posted date extraction with full page analysis...")
            print("\nDebug: Current page source excerpt:")
            print(self.driver.page_source[:1000])
            
        for selector in LINKEDIN_SELECTORS['posted_date']:
            try:
                if selector.startswith('//'):
                    if debug:
                        print(f"\nDebug: Trying posted date XPath selector: {selector}")
                    elements = self.driver.find_elements(By.XPATH, selector)
                else:
                    if debug:
                        print(f"\nDebug: Trying posted date CSS selector: {selector}")
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                
                if elements:
                    for element in elements:
                        text = element.text
                        if debug:
                            print(f"Debug: Found element text: '{text}'")
                            print(f"Debug: Element class: {element.get_attribute('class')}")
                        
                        if 'ago' in text.lower():
                            if debug:
                                print(f"Debug: Found 'ago' in text: '{text}'")
                            posted_date = self._parse_relative_date(text, debug)
                            if posted_date:
                                job_data.posted = posted_date.strftime('%Y-%m-%d')
                                if debug:
                                    print(f"Debug: Successfully parsed posted date: {job_data.posted}")
                                return
                else:
                    if debug:
                        print(f"Debug: No elements found for selector: {selector}")
                    
            except Exception as e:
                if debug:
                    print(f"Debug: Error with selector '{selector}': {str(e)}")
                continue

        if debug and not job_data.posted:
            print("\nDebug: No posted date found with any selector")
            
            # Additional debugging - dump page source
            print("\nDebug: Page source excerpt (first 1000 chars):")
            print(self.driver.page_source[:1000])  # Adjust the slice as needed for more/less output

    def extract(self, debug: bool = False) -> JobData:
        """Main extraction method"""
        self.debug = debug
        
        if debug:
            self._dump_page_content()
        
        # Initialize with required fields
        job_data = JobData(
            company="",
            title="",
            location="",
            url=self.driver.current_url
        )
        
        # 1. Try tab title first
        title, company = self._parse_tab_title(self.driver.title)
        if company:
            job_data.company = company
        if title:
            job_data.title = title
        
        # 2. Try salary from multiple locations
        salary = self._extract_salary_all_locations()
        if salary:
            job_data.salary = salary
        
        # Extract remaining data using existing selectors
        self._extract_with_selectors(job_data, debug)
        
        return job_data

    def _dump_page_content(self):
        """Dump page content to JSON file for debugging"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'page_structure_{timestamp}.json'
            
            page_data = {
                'url': self.driver.current_url,
                'title': self.driver.title,
                'page_source': self.driver.page_source,
                'salary_elements': []
            }
            
            # Collect all potential salary elements
            salary_selectors = [
                "//div[contains(@class, 'salary-range')]",
                "//div[contains(text(), 'Base salary')]",
                "//span[contains(text(), 'K/yr')]",
                ".jobs-unified-top-card__salary-details"
            ]
            
            for selector in salary_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH if selector.startswith('//') else By.CSS_SELECTOR, selector)
                    for element in elements:
                        page_data['salary_elements'].append({
                            'selector': selector,
                            'text': element.text,
                            'html': element.get_attribute('outerHTML')
                        })
                except Exception as e:
                    print(f"Debug: Error collecting salary element {selector}: {e}")
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(page_data, f, indent=2, ensure_ascii=False)
            print(f"Debug: Page structure dumped to {filename}")
            
            return filename
        except Exception as e:
            print(f"Debug: Error dumping page content: {str(e)}")
            return None

    def _extract_salary_all_locations(self) -> str:
        """Extract salary from all possible locations."""
        salary_selectors = [
            "//span[contains(text(), 'K/yr')]",
            "//div[contains(text(), 'Base salary')]/..",
            "//div[contains(@class, 'salary-range')]",
            ".jobs-unified-top-card__salary-details",
            "//div[contains(text(), '$')]",
            "//span[contains(text(), '$')]"
        ]

        best_match = ""
        
        for selector in salary_selectors:
            try:
                elements = self.driver.find_elements(
                    By.XPATH if selector.startswith('//') else By.CSS_SELECTOR, 
                    selector
                )
                for element in elements:
                    text = element.text.strip()
                    if 'K/yr' in text or '$' in text:
                        normalized = self._normalize_salary(text)
                        if normalized:
                            # Prefer ranges over single values
                            if ' - ' in normalized:
                                return normalized
                            # Store single value but keep looking for ranges
                            elif not best_match:
                                best_match = normalized
            except Exception as e:
                if self.debug:
                    print(f"Debug: Error with selector {selector}: {e}")
                continue

        return best_match

    def _normalize_salary(self, salary_text: str) -> str:
        """Normalize salary format to standard representation."""
        if not salary_text:
            return ""
        
        if self.debug:
            print(f"Debug: Input salary text: {salary_text}")
        
        def convert_k_notation(num_str):
            """Convert a K-notation value to a full number string."""
            # Remove $, /yr, and any surrounding whitespace
            num_str = num_str.replace('$', '').replace('/yr', '').strip()
            try:
                if 'K' in num_str.upper():
                    # Remove 'K' and convert to float
                    num_str = num_str.upper().replace('K', '')
                    value = float(num_str) * 1000
                else:
                    # Remove commas and convert to float
                    value = float(num_str.replace(',', ''))
                # Format with commas
                return f"${int(value):,}"
            except (ValueError, TypeError):
                if self.debug:
                    print(f"Debug: Failed to convert number: {num_str}")
                return ""
        
        # Handle invalid cases
        if salary_text.startswith('-') or salary_text.endswith('-'):
            if self.debug:
                print("Debug: Invalid format - starts or ends with dash")
            return ""
        
        # Define range patterns with priority
        range_patterns = [
            # K notation with /yr
            r'\$?([\d.]+)K/yr\s*[-–]\s*\$?([\d.]+)K/yr',
            # K notation without /yr
            r'\$?([\d.]+)K\s*[-–]\s*\$?([\d.]+)K',
            # Full numbers with /yr
            r'\$?([\d,]+)/yr\s*[-–]\s*\$?([\d,]+)/yr',
            # Full numbers without /yr
            r'\$?([\d,]+)\s*[-–]\s*\$?([\d,]+)',
            # Mixed formats
            r'\$?([\d,.]+)K?\s*[-–]\s*\$?([\d,.]+)K?',
        ]
        
        # Attempt to match range patterns
        for pattern in range_patterns:
            match = re.search(pattern, salary_text, re.IGNORECASE)
            if match:
                if self.debug:
                    print(f"Debug: Matched range pattern: {pattern}")
                    print(f"Debug: Found groups: {match.groups()}")
                
                start, end = match.groups()
                start_formatted = convert_k_notation(start)
                end_formatted = convert_k_notation(end)
                
                if start_formatted and end_formatted:
                    result = f"{start_formatted} - {end_formatted}"
                    if self.debug:
                        print(f"Debug: Formatted range: {result}")
                    return result
        
        # If no range found, attempt single value patterns
        if not any(x in salary_text for x in ['-', '–', 'to']):
            single_patterns = [
                r'\$?([\d,.]+)K/yr',
                r'\$?([\d,.]+)K',
                r'\$?([\d,.]+)/yr',
                r'\$?([\d,.]+)',
            ]
            
            for pattern in single_patterns:
                match = re.search(pattern, salary_text, re.IGNORECASE)
                if match:
                    if self.debug:
                        print(f"Debug: Matched single pattern: {pattern}")
                    value = convert_k_notation(match.group(1))
                    if value:
                        if self.debug:
                            print(f"Debug: Formatted single value: {value}")
                        return value
        
        if self.debug:
            print("Debug: No patterns matched")
        return ""

    def validate(self, data: JobData) -> bool:
        """Validate extracted data"""
        return bool(data.company and data.company != 'Unknown' and 
                   data.title and data.title != 'Unknown' and
                   data.url)  # Additional URL check for browser extraction

    def _extract_title(self) -> str:
        """Extract job title using multiple selectors"""
        title_selectors = [
            "h1.top-card-layout__title",
            "h1.job-details-jobs-unified-top-card__job-title",
            ".jobs-unified-top-card__job-title",
            ".job-details-jobs-unified-top-card__title"
        ]
        
        for selector in title_selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                raw_title = element.text.strip()
                
                # Skip invalid content
                if not raw_title or raw_title.lower().startswith(('notification', 'skip to', 'united states')):
                    continue
                    
                # Clean the title
                title = self._clean_title(raw_title)
                if title and title.lower() != "unknown":
                    return title
                    
            except NoSuchElementException:
                continue
            
        # Try parsing from the first line if no title found
        try:
            first_line = self.driver.page_source.split('\n')[0].strip()
            if first_line and not first_line.lower().startswith(('notification', 'skip')):
                return self._clean_title(first_line)
        except:
            pass
        
        return "Unknown"

    def _clean_title(self, title: str) -> str:
        """Clean title of common suffixes and metadata"""
        # Remove common suffixes and metadata
        patterns_to_remove = [
            r"\s*[-–]\s*[A-Za-z\s,]+$",  # Location suffix
            r"\s*\([^)]*\)$",            # Parenthetical info
            r"\s*·.*$",                  # Everything after bullet
            r"\s*\$.*$",                 # Salary info
            r"\s+Remote$",               # Remote suffix
            r"\s+Hybrid$",               # Hybrid suffix
            r"\s+[A-Za-z]+,\s*[A-Z]{2}$"  # City, State
        ]
        
        cleaned = title
        for pattern in patterns_to_remove:
            cleaned = re.sub(pattern, '', cleaned)
        
        # Handle multiline titles
        if '\n' in cleaned:
            parts = [p.strip() for p in cleaned.split('\n') if p.strip()]
            cleaned = ' '.join(parts)
        
        return cleaned.strip()

    def _extract_location(self) -> str:
        """Extract and normalize location"""
        location_patterns = [
            r"([A-Za-z\s,]+)(?:\s*·|\s*\(.*\)|\s*$)",  # City, State or Country
            r"([A-Za-z\s,]+)(?:\s+Remote|\s+Hybrid|\s+On-site)",  # Location with workplace type
            r"([A-Za-z\s,]+)(?:\s+or\s+[A-Za-z\s,]+)"  # Multiple locations
        ]
        
        location_selectors = [
            ".jobs-unified-top-card__bullet",
            ".job-details-jobs-unified-top-card__workplace-type",
            "[data-test-id='job-location']"
        ]
        
        for selector in location_selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                raw_location = element.text.strip()
                
                if not raw_location:
                    continue
                    
                # Try each pattern
                for pattern in location_patterns:
                    match = re.match(pattern, raw_location)
                    if match:
                        location = match.group(1).strip()
                        return self._normalize_location(location)
                    
            except NoSuchElementException:
                continue
        
        return ""

    def _clean_location(self, location: str) -> str:
        """Clean location string"""
        # Remove workplace type indicators and other metadata
        patterns_to_remove = [
            r"\s*\([^)]*\)",  # Remove parenthetical info like (Remote), (Hybrid)
            r"\s*or\s+[^·]+",  # Remove alternative locations
            r"\s+Remote$",     # Remove trailing Remote
            r"\s*\([^)]*\)$"   # Remove trailing parenthetical
        ]
        
        cleaned = location
        for pattern in patterns_to_remove:
            cleaned = re.sub(pattern, '', cleaned)
        
        return cleaned.strip()

    def _normalize_location(self, location: str) -> str:
        """Normalize location string with proper capitalization"""
        if not location:
            return ""
        
        # Split into parts (city, state/country)
        parts = [part.strip() for part in location.split(',')]
        normalized_parts = []
        
        for part in parts:
            if len(part) <= 3:  # State abbreviations
                normalized_parts.append(part.upper())
            else:
                # Handle special cases and title case
                words = part.split()
                normalized_words = []
                for word in words:
                    if word.lower() in ['uk', 'usa', 'uae']:
                        normalized_words.append(word.upper())
                    else:
                        normalized_words.append(word.title())
                normalized_parts.append(' '.join(normalized_words))
        
        return ', '.join(normalized_parts)

    def _extract_salary(self, driver) -> str:
        """Extract salary information using multiple strategies"""
        for selector in LINKEDIN_SELECTORS['salary']:
            try:
                if selector.startswith('//'):
                    if self.debug:
                        print(f"Debug: Trying XPath selector: {selector}")
                    elements = driver.find_elements(By.XPATH, selector)
                else:
                    if self.debug:
                        print(f"Debug: Trying CSS selector: {selector}")
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
                if elements:
                    for element in elements:
                        text = element.text.strip()
                        if self.debug:
                            print(f"Debug: Found text: {text}")
                        
                        if '$' in text or '/yr' in text:
                            normalized = self._normalize_salary(text)
                            if normalized:
                                if self.debug:
                                    print(f"Debug: Normalized salary: {normalized}")
                                return normalized
                else:
                    if self.debug:
                        print(f"Debug: No elements found for selector: {selector}")
                    
            except Exception as e:
                if self.debug:
                    print(f"Debug: Error in salary extraction: {str(e)}")
                continue
        
        return ""