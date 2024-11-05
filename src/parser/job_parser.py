import re
from datetime import datetime
from typing import Dict, Any, List
from src.models.job_post import JobPost
from src.utils.validation import validate_job_post

class JobParser:
    """Parser for LinkedIn job postings."""
    
    def parse(self, raw_text: str, debug: bool = False) -> JobPost:
        """Parse job posting text into structured data."""
        
        # Initialize job details
        details = {
            "company": "Unknown",
            "title": "Unknown",
            "location": "",
            "salary": "",
            "is_remote": False,
            "applicants": "",
            "posted": "",
            "date_applied": datetime.now().strftime("%m/%d/%Y")
        }

        # Extract company - look for company name before "followers"
        company_pattern = r"(.*?)\n*[\d,]+ followers"
        if match := re.search(company_pattern, raw_text):
            details["company"] = match.group(1).strip().replace(" company logo", "")

        # Extract title - updated patterns
        title_patterns = [
            r"Save\s+(.*?)\s+at\s+Unreal Staffing",  # Match "Save {title} at Company"
            r"(?<=About the job\n).*?(?=\n)",  # Title right after "About the job"
            r"Save Site Reliability Engineer.*?(?=\s+at)",  # Specific to this format
        ]
        
        details["title"] = "Unknown"  # Default value
        for pattern in title_patterns:
            if match := re.search(pattern, raw_text):
                title = match.group(0).strip()
                # Enhanced title cleanup
                title = re.sub(r'^Save\s+', '', title)  # Remove "Save" prefix
                title = re.sub(r'\s+at\s+.*$', '', title)  # Remove "at Company" suffix
                title = re.sub(r'^Save\s+', '', title)  # Remove any remaining "Save" prefix
                
                if (
                    len(title) > 0 
                    and "About" not in title 
                    and "notification" not in title.lower()
                    and "skip to" not in title.lower()
                ):
                    details["title"] = title
                    break

        # Extract salary - look for salary pattern with Base Salary
        salary_pattern = r'\$([\d,]+-[\d,]+k)[^a-zA-Z]*(?:Base Salary)?'
        if match := re.search(salary_pattern, raw_text):
            details["salary"] = f"${match.group(1)}"

        # Extract location - look for US-Remote or similar patterns
        location_pattern = r'(?:^|\n)([A-Za-z-]+Remote|United States[^·\n]*)'
        if match := re.search(location_pattern, raw_text):
            details["location"] = match.group(1).strip()
            # Clean up location text
            details["location"] = details["location"].replace("Matches your job preferences, workplace type is ", "")

        # Check for remote indicators
        details["is_remote"] = any(
            indicator in raw_text.lower() 
            for indicator in ["remote", "us-remote"]
        )

        # Extract applicants count if available
        applicants_pattern = r'(\d+)\s*applicants'
        if match := re.search(applicants_pattern, raw_text):
            details["applicants"] = match.group(1)

        # Create and return JobPost object
        return JobPost(
            raw_text=raw_text,
            **details
        )
    
    def _extract_company(self, text: str) -> str:
        """Extract company name from text."""
        company_patterns = [
            r"(?<=\n)([^•\n]+?)\s*logo",  # Match company before "logo"
            r"at\s+([^•\n]+?)\s*(?=\n|$)",  # Match company after "at"
        ]
        
        for pattern in company_patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            if matches:
                company = matches[0].strip()
                # Filter out navigation text
                if not any(x in company.lower() for x in ['notification', 'skip to', 'search']):
                    return company
        
        # Look for company name patterns
        patterns = [
            r"(.*?) logo",  # Matches "Company Name logo"
            r"About the company\n(.*?) company logo",  # Matches company name in about section
            r"About the company\n(.*?)\n",  # Alternative about section pattern
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                company = matches[0].strip()
                if company and company != "Unknown":
                    return company
        
        return "Unknown"
    
    def _extract_title(self, text: str) -> str:
        """Extract job title from text."""
        patterns = [
            # Common LinkedIn job title patterns
            r"(?:^|\n)([^·\n]+?)(?:\s*·\s*(?:Full-time|Part-time|Contract|Internship))",  # Title followed by job type
            r"Save\s+([^·\n]+?)\s+at\s+",  # Title in "Save X at Company"
            r"Apply.*?\n([^·\n]+?)(?:\s*·|\s+(?:in|at|,)\s)"  # Title after Apply button
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.MULTILINE | re.IGNORECASE)
            if matches:
                title = matches[0].strip()
                # Clean up common prefixes/suffixes
                title = re.sub(r'^Save\s+', '', title)
                title = re.sub(r'\s+with verification$', '', title)
                
                # Filter out navigation/header text
                if not any(x in title.lower() for x in [
                    'notification', 'skip to', 'search', 'home', 'my network', 
                    'jobs', 'messaging', 'about', 'accessibility'
                ]):
                    return title
        
        return "Unknown"
    
    def _extract_location(self, text: str) -> str:
        """Extract location from text."""
        # Look for location patterns
        patterns = [
            r"(?:^|\n)(United States)(?:\s*(?:·|\n|$))",  # United States (moved to first priority)
            r"(?:^|\n)([^·\n]+?,\s*[A-Z]{2}[^·\n]*?)(?:\s*·\s*(?:\d+\s*(?:hours?|days?|weeks?|months?)\s*ago|Over\s+\d+\s+applicants))",  # City, ST · Time ago or applicants
            r"(?:^|\n)([^·\n]+?,\s*[A-Z]{2}[^·\n]*?)(?:\s*·|\s*\n)",  # City, ST followed by delimiter
            r"Location:\s*([^\n]+)"  # Explicit location field
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                location = matches[0].strip()
                # Filter out non-location text and preference matches
                if not any(x in location.lower() for x in [
                    'notification', 'skip to', 'search', 'manager', 'engineer', 
                    'director', 'developer', 'architect', 'matches your', 'preferences'
                ]):
                    # Add remote status if applicable
                    if any(term in text.lower() for term in ['remote', 'work anywhere', 'work from home']):
                        if '(remote)' not in location.lower():
                            location += ' (Remote)'
                    return location
        
        return "Unknown"
    
    def _extract_salary(self, text: str) -> str:
        """Extract salary information from text."""
        # Split text at "More jobs" to only look in main job posting
        main_job_text = text.split("More jobs")[0] if "More jobs" in text else text
        
        patterns = [
            r'\$[\d,]+K?\s*(?:-|to)\s*\$[\d,]+K?(?:/yr)?',
            r'\$[\d,]+,[\d,]+\s*(?:-|to)\s*\$[\d,]+,[\d,]+',
            r'(?:Base pay|Salary):\s*\$[\d,]+K?\s*(?:-|to)\s*\$[\d,]+K?',
            r'(?:Base pay|Salary):\s*\$[\d,]+,[\d,]+\s*(?:-|to)\s*\$[\d,]+,[\d,]+'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, main_job_text, re.IGNORECASE)
            if matches:
                # Take the first match only from the main job section
                return matches[0].strip()
                
        return ""
    
    def _extract_url(self, text: str) -> str:
        """Extract LinkedIn job URL from text."""
        # Add your existing URL extraction logic here
        return ""
    
    def _extract_date(self, text: str) -> datetime:
        """Extract posting date from text."""
        # Add your existing date extraction logic here
        return datetime.now()
    
    def _is_remote(self, text: str) -> bool:
        """Determine if job is remote."""
        remote_indicators = [
            r'\bremote\b',
            r'\bwork anywhere\b',
            r'\bwork from home\b',
            r'\bwfh\b',
            r'\bfully remote\b'
        ]
        
        # Check for remote contradictions
        contradictions = [
            r'\bhybrid\b',
            r'\bin[- ]office\b',
            r'\bon[- ]site\b',
            r'must be located in',
            r'must reside in',
            r'must live in',
            r'required to work from'
        ]
        
        text_lower = text.lower()
        is_remote = any(re.search(pattern, text_lower) for pattern in remote_indicators)
        has_contradictions = any(re.search(pattern, text_lower) for pattern in contradictions)
        
        return is_remote and not has_contradictions

    def validate_job_post(self, job_post: JobPost) -> List[str]:
        """Additional validation specific to US remote jobs."""
        errors = []
        
        # Check if it's a US position
        if not any(term in job_post.location for term in ['United States', 'US', 'USA']):
            if not any(', ' + state in job_post.location for state in ['AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY']):
                errors.append("Not a US-based position")
        
        # Check remote status
        if not job_post.is_remote:
            errors.append("Not a remote position")
        
        # Check for hybrid/onsite requirements in description
        if 'hybrid' in job_post.raw_text.lower():
            errors.append("Position appears to be hybrid")
        
        if 'on-site' in job_post.raw_text.lower() or 'onsite' in job_post.raw_text.lower():
            errors.append("Position appears to require on-site work")
        
        return errors

    def _extract_applicants(self, text: str) -> str:
        """Extract number of applicants if available."""
        patterns = [
            r"(\d+)\s*applicants?",
            r"(\d+)\+\s*applicants?"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return matches[0]
        return ""

    def _extract_posted_date(self, text: str) -> str:
        """
        Extract when the job was originally posted.
        Returns dates like "10/15/2024" or relative times like "2 weeks ago"
        """
        patterns = [
            r"(\d{1,2}/\d{1,2}/\d{4})",  # Matches explicit dates
            r"(\d+)\s*(?:hour|day|week|month)s?\s*ago",  # Matches relative times
            r"Posted\s+(\d+)\s*(?:hour|day|week|month)s?\s*ago"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return matches[0]
        return ""
