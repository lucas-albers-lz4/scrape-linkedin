import re
from datetime import datetime
from typing import Dict, Any, List
from src.models.job_post import JobPost
from src.utils.validation import validate_job_post

class JobParser:
    """Parser for LinkedIn job postings."""
    
    def parse(self, raw_text: str, debug: bool = False) -> JobPost:
        """Parse raw text into a JobPost object."""
        today = datetime.now().strftime("%m/%d/%Y")
        
        parsed_data = {
            'company': self._extract_company(raw_text),
            'title': self._extract_title(raw_text),
            'location': self._extract_location(raw_text),
            'salary': self._extract_salary(raw_text),
            'applicants': self._extract_applicants(raw_text),
            'posted': self._extract_posted_date(raw_text),
            'notes': "Easy Apply" if "Easy Apply" in raw_text else "",
            'is_remote': self._is_remote(raw_text),
            'raw_text': raw_text,
            'date': today,  # Today's date for when we found/parsed the job
            'date_applied': today  # Assuming we apply the same day we find it
        }
        
        job_post = JobPost(**parsed_data)
        
        if debug:
            print(f"\nDebug: Extracted applicants: {job_post.applicants}")
            print(f"Debug: Posted date: {job_post.posted}")
            print(f"Debug: Parse/Apply date: {job_post.date}")
            print(f"Debug: Is remote: {job_post.is_remote}")
        
        return job_post
    
    def _extract_company(self, text: str) -> str:
        """Extract company name from text."""
        patterns = [
            r"(?:^|\n)([^·\n]+?)\s+logo\s*(?:\n|$)",  # Company logo text
            r"(?:at|Save.*?at)\s+([^·\n]+?)(?:\s*(?:\n|$))",  # "at Company"
            r"(?:^|\n)([^·\n]+?)\s*·\s*(?:Full-time|[0-9,]+\s+followers)"  # Company followed by common patterns
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            if matches:
                company = matches[0].strip()
                # Filter out navigation text
                if not any(x in company.lower() for x in ['notification', 'skip to', 'search']):
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
            r"(?:^|\n)([^·\n]+?,\s*[A-Z]{2}[^·\n]*?)(?:\s*·\s*[0-9]+\s*(?:hours?|days?|weeks?)\s*ago)",  # City, ST · Time ago
            r"(?:^|\n)([^·\n]+?,\s*[A-Z]{2}[^·\n]*?)(?:\s*·|\s*\n)",  # City, ST followed by delimiter
            r"(?:^|\n)(United States)(?:\s*(?:·|\n|$))",  # United States
            r"Location:\s*([^\n]+)"  # Explicit location field
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                location = matches[0].strip()
                # Filter out non-location text
                if not any(x in location.lower() for x in [
                    'notification', 'skip to', 'search', 'manager', 'engineer', 
                    'director', 'developer', 'architect'
                ]):
                    # Add remote status if applicable
                    if any(term in text.lower() for term in ['remote', 'work anywhere', 'work from home']):
                        if '(remote)' not in location.lower():
                            location += ' (Remote)'
                    return location
        
        return "Unknown"
    
    def _extract_salary(self, text: str) -> str:
        """Extract salary information from text."""
        patterns = [
            r'\$[\d,]+K?\s*(?:-|to)\s*\$[\d,]+K?(?:/yr)?',
            r'\$[\d,]+,[\d,]+\s*(?:-|to)\s*\$[\d,]+,[\d,]+',
            r'(?:Base pay|Salary):\s*\$[\d,]+K?\s*(?:-|to)\s*\$[\d,]+K?'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
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
