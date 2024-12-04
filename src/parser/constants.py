"""Constants used for parsing LinkedIn job postings."""
from typing import List, Dict, Pattern
import re

# Compile regex patterns once for better performance
class JobPatterns:
    def __init__(self):
        """Initialize compiled regex patterns"""
        self.US_STATE_ABBREVS: List[str] = [
            'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 
            'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 
            'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 
            'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 
            'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
        ]

        self.LOCATION_PATTERNS: List[Pattern] = [
            re.compile(r"Location\s*[:\n]\s*(.*?)(?=\n)", re.IGNORECASE),
            re.compile(r"(?:^|\n)([^·\n]+?Metropolitan Area)(?:\s*·)", re.IGNORECASE),
            re.compile(
                rf"(?:^|\n)([^·\n]+?,\s*(?:{'|'.join(self.US_STATE_ABBREVS)}))(?:\s*·)", 
                re.IGNORECASE
            )
        ]

        self.REMOTE_INDICATORS: List[Pattern] = [
            re.compile(pattern, re.IGNORECASE) for pattern in [
                r'\bremote\b',
                r'\bwork anywhere\b',
                r'\bwork from home\b',
                r'\bwfh\b',
                r'\bfully remote\b'
            ]
        ]

        self.REMOTE_CONTRADICTIONS: List[Pattern] = [
            re.compile(pattern, re.IGNORECASE) for pattern in [
                r'\bhybrid\b',
                r'\bin[- ]office\b',
                r'\bon[- ]site\b',
                r'must be located in',
                r'must reside in',
                r'must live in'
            ]
        ]

        self.TITLE_PATTERNS: List[Pattern] = [
            re.compile(pattern, re.IGNORECASE | re.MULTILINE) for pattern in [
                r'(?:Quick Apply|Show more options)\s*([\w\s-]+?)\s+(?:United States|·)',  # Title before location/bullet
                r'Save\s+([\w\s-]+?)\s+at',  # Title in save text
                r'As (?:the|a|an)\s+([\w\s-]+?)(?:,|\s+you)',  # Title in overview
            ]
        ]

        self.TITLE_BLACKLIST: List[str] = [
            'notification', 'skip to', 'search', 'about',
            'keyboard', 'home', 'my network', 'jobs', 'messaging'
        ]

        # Company detection patterns
        self.COMPANY_PATTERNS = [
            re.compile(pattern, re.IGNORECASE | re.MULTILINE) for pattern in [
                r'([A-Za-z0-9][A-Za-z0-9\s&.-]+?) logo\b',  # Company logo pattern
                r'Save .+ at ([A-Za-z0-9][A-Za-z0-9\s&.-]+)',  # "Save job at Company"
                r'About ([A-Za-z0-9][A-Za-z0-9\s&.-]+)',  # About section
                r'Tell me more about ([A-Za-z0-9][A-Za-z0-9\s&.-]+)'  # Tell me more section
            ]
        ]

        # Title detection patterns
        self.TITLE_PATTERNS = [
            re.compile(pattern, re.IGNORECASE | re.MULTILINE) for pattern in [
                r'([A-Za-z][A-Za-z0-9\s,&.-]+?)\s*(?:·|United States)',  # Title before bullet or location
                r'Save ([^·\n]+?) at',  # Title in save text
                r'As (?:the|a|an)\s+([^,\n]+)',  # Title in overview
            ]
        ]

        # Salary patterns
        self.SALARY_PATTERNS = [
            re.compile(pattern, re.IGNORECASE) for pattern in [
                r'\$(\d{1,3}(?:,\d{3})*K?/yr\s*-\s*\$\d{1,3}(?:,\d{3})*K?/yr)',  # "$170K/yr - $200K/yr"
                r'(\$\d{1,3}(?:,\d{3})*\s*-\s*\$\d{1,3}(?:,\d{3})*)',  # "$170,000 - $200,000"
            ]
        ]

class LocationPatterns:
    US_STATES = {
        'AL': ['Alabama', 'AL'],
        'AK': ['Alaska', 'AK'],
        'AZ': ['Arizona', 'AZ'],
        # ... (all states)
        'WY': ['Wyoming', 'WY']
    }

    US_TERRITORIES = {
        'PR': ['Puerto Rico', 'PR'],
        'GU': ['Guam', 'GU'],
        'VI': ['Virgin Islands', 'VI'],
        'MP': ['Northern Mariana Islands', 'MP'],
        'AS': ['American Samoa', 'AS']
    }

    US_REFERENCES = [
        'United States',
        'USA',
        'U.S.',
        'U.S.A.',
        'US'
    ]

    @classmethod
    def is_us_location(cls, location: str) -> bool:
        """Check if a location is in the United States."""
        location = location.upper()
        
        # Check state abbreviations and names
        for state_data in cls.US_STATES.values():
            if any(loc.upper() in location for loc in state_data):
                return True
                
        # Check territory abbreviations and names
        for territory_data in cls.US_TERRITORIES.values():
            if any(loc.upper() in location for loc in territory_data):
                return True
                
        # Check general US references
        return any(ref.upper() in location for ref in cls.US_REFERENCES)
