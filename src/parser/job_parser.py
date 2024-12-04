from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
import logging
import re  # Also needed for regex operations
from src.models.job_post import JobPost
from src.utils.validation import validate_job_post
from .constants import JobPatterns
import usaddress
from selenium.webdriver.common.by import By

logger = logging.getLogger(__name__)

class JobParser:
    """LinkedIn job posting parser that extracts structured data from clipboard content.
    
    This parser is designed to handle LinkedIn job postings copied to clipboard and extract
    key information such as company name, job title, location, and other metadata.
    
    Parsing Strategy:
        1. Company Name: Looks for company name after "company logo" text or in metadata section
        2. Job Title: Extracts from header section, typically before location/metadata
        3. Location: Parses US locations and identifies remote status
        4. Salary: Extracts when available in standard US formats
        
    Known Limitations:
        - Requires specific LinkedIn format (desktop web version)
        - Company detection may fail if logo text is missing
        - Location parsing is US-centric
        - Salary parsing expects standard formats ($XXk-$YYk or similar)
        
    Example Usage:
        parser = JobParser()
        job_post = parser.parse(clipboard_text)
        print(f"Company: {job_post.company}")
        print(f"Title: {job_post.title}")
    
    Error Handling:
        - Returns "Unknown" for company/title if parsing fails
        - Sets empty string for optional fields if not found
        - Maintains original raw text for debugging
    """
    
    # Company Name Patterns
    COMPANY_PATTERNS = [
        # Matches company name after logo text
        r'company logo\s*\n\s*([^\\n]+)',  # Example: "company logo\nAcme Corp"
        
        # Matches company in metadata section
        r'About (.*?) (?:jobs|employees|company)',  # Example: "About Acme Corp jobs"
    ]

    # Location Patterns
    LOCATION_PATTERNS = [
        # Matches US city/state with optional remote
        r'([^·]+(?:, [A-Z]{2})?)\s*(?:\(Remote\))?',  # Example: "New York, NY (Remote)"
        
        # Matches standalone remote indicator
        r'\(Remote\)|Remote',  # Example: "(Remote)" or "Remote"
    ]

    # Salary Patterns
    SALARY_PATTERNS = [
        # Matches range format
        r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)[kK]?\s*-\s*\$(\d+(?:,\d{3})*(?:\.\d{2})?)[kK]?',
        # Example: "$70k - $90k" or "$70,000 - $90,000"
        
        # Matches single value with plus
        r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)[kK]?\+?',
        # Example: "$70k+" or "$70,000+"
    ]

    # Applicant Count Pattern
    APPLICANT_PATTERN = r'(\d+(?:\+)?)\s*applicants?'  # Example: "25+ applicants"

    # Posted Date Patterns
    POSTED_PATTERNS = [
        r'(\d+)\s*(hour|day|week|month)s?\s*ago',  # Example: "2 days ago"
        r'Posted\s*(\d+)\s*(hour|day|week|month)s?\s*ago',  # Example: "Posted 2 days ago"
    ]

    # Text Cleaning Patterns
    CLEANUP_PATTERNS = [
        (r'^\d+\s*notifications?\s*total', ''),  # Remove notification counts
        (r'Show\s*more', ''),  # Remove "Show more" buttons
        (r'Save\s*job', ''),   # Remove "Save job" text
        (r'\s+', ' '),         # Normalize whitespace
    ]

    def __init__(self):
        self.patterns = JobPatterns()
    
    def _extract_location(self, lines: List[str]) -> Tuple[str, bool]:
        """Extract location and remote status from job posting.
        
        Args:
            lines: List of text lines
            
        Returns:
            Tuple of (location string, is_remote boolean)
            
        Example:
            "New York, NY (Remote)" -> ("New York, NY", True)
        """
        # Try pattern matching first
        for pattern in self.patterns.LOCATION_PATTERNS:
            if match := pattern.search(lines[0]):
                location = match.group(1).strip()
                return location, self._check_remote_status(lines[0])

        # Fall back to usaddress parsing
        try:
            parsed = usaddress.tag(lines[0])
            if isinstance(parsed, tuple) and len(parsed) > 0:
                components = parsed[0]
                city = components.get('PlaceName', '')
                state = components.get('StateName', '')
                
                if city and state:
                    location = f"{city}, {state}"
                elif state:
                    location = state
                else:
                    location = city
                    
                return location, self._check_remote_status(lines[0])
                    
        except Exception as e:
            logger.debug(f"usaddress parsing failed: {str(e)}")

        return "", self._check_remote_status(lines[0])

    def _check_remote_status(self, text: str) -> bool:
        """Determine if a position is remote"""
        is_remote = any(pattern.search(text) 
                       for pattern in self.patterns.REMOTE_INDICATORS)
        has_contradictions = any(pattern.search(text) 
                               for pattern in self.patterns.REMOTE_CONTRADICTIONS)
        return is_remote and not has_contradictions

    def _validate_us_location(self, location: str) -> bool:
        """Validate that a location is in the United States"""
        if not location:
            return False
            
        return any(f", {state}" in location.upper() 
                  for state in self.patterns.US_STATE_ABBREVS)

    def _clean_linkedin_text(self, text: str) -> str:
        """Clean and normalize LinkedIn text content.
        
        Removes common LinkedIn artifacts and normalizes text for consistent parsing.
        
        Args:
            text: Raw text string to clean
            
        Returns:
            Cleaned and normalized text string
            
        Cleaning Steps:
            1. Removes "About the job" headers
            2. Strips notification counts
            3. Removes navigation elements
            4. Normalizes whitespace
            5. Removes common UI elements ("Show more", "Save job", etc.)
            
        Example:
            Input: "0 notifications\\nAbout the job\\nShow more\\nActual content"
            Output: "Actual content"
        """
        if not text:
            return text
            
        for pattern, replacement in self.CLEANUP_PATTERNS:
            text = re.sub(pattern, replacement, text)
        return text.strip()

    def _extract_company(self, lines: List[str], debug: bool = False) -> str:
        """Extract company name from job posting text.
        
        Searches for company name using multiple strategies:
        1. Look for text after "company logo"
        2. Check for company metadata section
        3. Parse from structured data section if present
        
        Args:
            lines: List of text lines from job posting
            debug: If True, prints extraction details
            
        Returns:
            Company name or "Unknown" if not found
            
        Examples:
            - "company logo\\nAcme Corp" -> "Acme Corp"
            - "About Acme Corp\\nShow more" -> "Acme Corp"
        """
        for i, line in enumerate(lines):
            if 'company logo' in line.lower():
                if i+1 < len(lines):
                    company = lines[i+1].strip()
                    if company and not any(x in company.lower() for x in ['about', 'show more']):
                        return company
        return "Unknown"

    def _extract_salary(self, text: str) -> str:
        """Parse salary information from job text.
        
        Handles formats: $XXk-$YYk, $XX,XXX+, etc.
        
        Args:
            text: Raw job posting text
            
        Returns:
            Formatted salary string or empty if not found
        """
        if match := re.search(r'\$?(\d{1,3}(?:,\d{3})*K?/yr\s*-\s*\$?\d{1,3}(?:,\d{3})*K?/yr)', text):
            return match.group(1)
        return ""

    def _extract_applicants(self, text: str) -> str:
        """Extract number of applicants from posting.
        
        Args:
            text: Raw job text
            
        Returns:
            Applicant count (e.g., "25+") or empty string
        """
        if match := re.search(r'(\d{1,3}(?:,\d{3})*K?/yr\s*-\s*\$?\d{1,3}(?:,\d{3})*K?/yr)', text):
            count = match.group(1)
            if 'over' in count.lower():
                count = count.replace('over', '').strip()
            return count
        return ""

    def _extract_posted_date(self, text: str) -> str:
        """Extract when job was posted.
        
        Args:
            text: Raw job text
            
        Returns:
            Posted date string (e.g., "2 days ago") or empty
        """
        if match := re.search(r'(\d+ days ago)', text):
            return match.group(1)
        return ""

    def _parse_metadata_line(self, line: str) -> Dict[str, str]:
        """Parse job metadata line containing location/applicants/etc.
        
        Args:
            line: Single line containing metadata
            
        Returns:
            Dict of extracted metadata fields
        """
        parts = [p.strip() for p in line.split('·')]
        
        # First part is usually location
        location = parts[0]
        
        # Look for posted date and applicants in other parts
        for part in parts:
            if 'ago' in part:
                posted = part
            if 'applicant' in part.lower():
                applicants = part.split('applicant')[0].strip()
                if 'over' in applicants.lower():
                    applicants = applicants.replace('over', '').strip()
                break

        return {
            "location": location,
            "posted": posted,
            "applicants": applicants
        }

    def _validate_parsed_data(self, post: JobPost) -> List[str]:
        """Validate parsed job data for required fields.
        
        Args:
            post: Parsed JobPost object
            
        Returns:
            List of validation error messages
        """
        errors = []
        if not post.company:
            errors.append("Company name is required")
        if not post.title:
            errors.append("Job title is required")
        if not post.location:
            errors.append("Location is required")
        if not post.salary:
            errors.append("Salary is required")
        if not post.is_remote:
            errors.append("Remote status is required")
        if not post.applicants:
            errors.append("Applicant count is required")
        if not post.posted:
            errors.append("Posted date is required")
        return errors

    # Keep existing parse() method but update it to use the new helpers
    def parse(self, raw_text: str, debug: bool = False) -> JobPost:
        """Parse job posting text into structured data"""
        if not raw_text:
            return JobPost()
        
        details = {
            "title": "",
            "company": "",
            "location": "",
            "salary": "",
            "posted": "",
            "applicants": "",
            "is_remote": False
        }
        
        lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
        if not lines:
            return JobPost(**details)
        
        # First line is typically the title
        details["title"] = self._clean_linkedin_text(lines[0])
        
        # Find metadata line (contains ·)
        for line in lines[1:]:
            if '·' in line:
                parts = [p.strip() for p in line.split('·')]
                
                # Handle location and remote status
                if parts:
                    location = parts[0]
                    if location.lower() == 'remote':
                        details["is_remote"] = True
                        details["location"] = ""
                    else:
                        # Remove remote/hybrid indicators
                        for pattern in [r'\(remote\)', r'\bremote\b', r'\(hybrid\)', r'\bhybrid\b']:
                            if re.search(pattern, location, re.IGNORECASE):
                                if 'remote' in pattern.lower():
                                    details["is_remote"] = True
                                location = re.sub(pattern, '', location, flags=re.IGNORECASE).strip()
                        
                        # Handle multiple locations
                        if ' or ' in location:
                            location = location.split(' or ')[0].strip()
                        
                        details["location"] = location
                
                # Parse other metadata
                for part in parts[1:]:
                    part = part.strip()
                    # Posted date
                    if re.search(r'(?:Posted|Reposted)\s+(.+ago)', part):
                        details["posted"] = re.search(r'(?:Posted|Reposted)\s+(.+ago)', part).group(1)
                    # Salary
                    elif re.search(r'\$?(\d+K/yr\s*-\s*\$?\d+K/yr)', part):
                        salary = re.search(r'\$?(\d+K/yr\s*-\s*\$?\d+K/yr)', part).group(1)
                        if not salary.startswith('$'):
                            salary = f"${salary}"
                        details["salary"] = salary
                    # Applicants
                    elif 'applicant' in part.lower():
                        count = part.split('applicant')[0].strip()
                        if '+' in count:
                            count = count.replace('+', '').strip()
                        details["applicants"] = count

        # Location and remote status
        try:
            # NOTE: Selectors are defined in src/utils/selectors.py
            # Use them like: self.selectors.LINKEDIN_SELECTORS['location']
            for selector in self.selectors.LINKEDIN_SELECTORS['location']:
                try:
                    location_text = driver.find_element(By.CSS_SELECTOR, selector).text.lower()
                    if 'remote' in location_text:
                        job_data['is_remote'] = True
                        location_text = re.sub(r'\bremote\b', '', location_text, flags=re.IGNORECASE)
                
                    if location_text and not location_text.isspace():
                        job_data['location'] = location_text.strip()
                        break
                except:
                    continue
                
            # Additional check for remote indicators
            if not job_data.get('is_remote'):
                for selector in self.selectors.LINKEDIN_SELECTORS['remote_indicators']:
                    try:
                        if driver.find_element(By.CSS_SELECTOR, selector):
                            job_data['is_remote'] = True
                            break
                    except:
                        continue
                    
        except Exception as e:
            print(f"Error getting location: {e}")

        return JobPost(**details)

    def parse_title(self, text):
        """Extract job title from LinkedIn job posting text."""
        if not text or text.isspace():
            return "Unknown"

        # First check if this is debug output
        if text.startswith(("python", "Debug:", "Copied to clipboard:")):
            match = re.search(r'Title:\s*([^\n]+)', text)
            if match:
                title = match.group(1).strip()
                return "Unknown" if title == "Title" else title
            return "Unknown"

        # Split into lines and clean
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # If the text starts with certain patterns, it's likely not a valid job page
        if any(lines[0].startswith(x) for x in ['notifications total', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']):
            return "Unknown"

        # Look for title after specific markers
        for i, line in enumerate(lines):
            if "logo" in line and i + 2 < len(lines):
                company_line = lines[i+1]
                potential_title = lines[i+2]
                
                # Validate the potential title
                if (potential_title and
                    not any(x in potential_title.lower() for x in ['logo', 'notifications', 'total', 'united states', '$']) and
                    not potential_title.endswith(('ago', 'applicants')) and
                    len(potential_title.split()) <= 10):
                    return potential_title

            if "Share options" in line or "Show more options" in line:
                next_line = lines[i+1] if i + 1 < len(lines) else ""
                if (next_line and
                    not any(x in next_line.lower() for x in ['logo', 'notifications', 'total', 'united states', '$']) and
                    not next_line.endswith(('ago', 'applicants')) and
                    len(next_line.split()) <= 10):
                    return next_line

        return "Unknown"
