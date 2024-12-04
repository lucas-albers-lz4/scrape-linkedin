from dataclasses import dataclass
from typing import Optional
import re
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@dataclass
class JobPost:
    """Represents a LinkedIn job posting"""
    title: str = ''
    company: str = ''
    location: str = ''
    url: str = ''
    salary: str = ''
    raw_text: str = ''
    is_remote: bool = False
    applicants: str = ''
    posted: str = ''
    date_applied: str = ''

    def __init__(self, raw_data: str = '', **kwargs):
        """Initialize with raw job post data or individual fields"""
        logger.debug(f"Initializing JobPost with raw_data:\n{raw_data}")
        logger.debug(f"Additional kwargs: {kwargs}")
        
        # Initialize default values
        self.title = kwargs.get('title', '')
        self.company = kwargs.get('company', 'Unknown')
        self.location = kwargs.get('location', '')
        self.salary = kwargs.get('salary', '')
        self.posted = kwargs.get('posted', '')
        self.applicants = kwargs.get('applicants', '')
        self.url = kwargs.get('url', '')
        self.is_remote = kwargs.get('is_remote', False)
        
        # Handle raw_text alias for raw_data
        if not raw_data and 'raw_text' in kwargs:
            raw_data = kwargs['raw_text']
        
        # Store and parse raw data if provided
        self.raw_data = raw_data
        if raw_data:
            self.parse_raw_data()

    def parse_raw_data(self):
        """Parse the raw data into structured fields"""
        logger.debug("=== Starting parse_raw_data ===")
        logger.debug(f"Raw data:\n{self.raw_data}")
        
        # Split into lines and clean
        lines = [line.strip() for line in self.raw_data.split('\n') if line.strip()]
        logger.debug(f"Cleaned lines ({len(lines)}):\n" + '\n'.join(f"{i}: {line}" for i, line in enumerate(lines)))
        
        # First line is usually the title
        if lines:
            logger.debug(f"Processing title from first line: {lines[0]}")
            self.title = self.clean_title(lines[0])
            logger.debug(f"Cleaned title: {self.title}")
            
        # Look for location in second line
        if len(lines) > 1:
            location_line = lines[1]
            logger.debug(f"Processing location from second line: {location_line}")
            
            if '·' in location_line:
                parts = location_line.split('·')
                logger.debug(f"Location parts after splitting on '·': {parts}")
                self.location = parts[0].strip()
                self.is_remote = 'Remote' in location_line
                logger.debug(f"Extracted location: {self.location}, is_remote: {self.is_remote}")
                
        # Process remaining lines for metadata
        for line in lines[2:]:
            logger.debug(f"Processing metadata line: {line}")
            
            if '$' in line:
                logger.debug("Found salary indicator")
                self.salary = self.clean_salary(line)
                logger.debug(f"Cleaned salary: {self.salary}")
                
            elif 'applicants' in line:
                logger.debug("Found applicants indicator") 
                self.applicants = self.clean_applicants(line)
                logger.debug(f"Cleaned applicants: {self.applicants}")
                
            elif 'ago' in line:
                logger.debug("Found posted date indicator")
                self.posted = self.clean_posted(line)
                logger.debug(f"Cleaned posted date: {self.posted}")
                
            elif 'company logo' in line.lower():
                logger.debug("Found company indicator")
                self.company = self.clean_company(line)
                logger.debug(f"Cleaned company: {self.company}")
                
        logger.debug("=== Final parsed values ===")
        logger.debug(f"Title: {self.title}")
        logger.debug(f"Company: {self.company}")
        logger.debug(f"Location: {self.location}")
        logger.debug(f"Salary: {self.salary}")
        logger.debug(f"Posted: {self.posted}")
        logger.debug(f"Applicants: {self.applicants}")
        logger.debug(f"Is Remote: {self.is_remote}")
        logger.debug("=== End parse_raw_data ===")

    def clean_title(self, text: str) -> str:
        """Clean job title by removing location and metadata"""
        logger.debug(f"Cleaning title: {text}")
        if not text:
            return ''
            
        # Remove location if it appears after a dash
        if ' - ' in text:
            logger.debug("Found location separator")
            text = text.split(' - ')[0]
            logger.debug(f"After removing location: {text}")
            
        # Remove common suffixes
        suffixes = [
            '(Remote)',
            '(Hybrid)',
            '(On-site)'
        ]
        
        for suffix in suffixes:
            if suffix in text:
                logger.debug(f"Removing suffix: {suffix}")
                text = text.replace(suffix, '').strip()
                
        result = text.strip()
        logger.debug(f"Final cleaned title: {result}")
        return result

    def clean_location(self, text: str) -> str:
        """Clean location string and set remote status"""
        if not text:
            return ''
        
        # Handle pure remote case first
        if text.strip().lower() == 'remote':
            self.is_remote = True
            return ''

        # Extract location before any metadata
        location = text.strip()
        
        # Remove work type indicators and set flags
        work_type_patterns = [
            (r'\s*\(remote\)', True),
            (r'\s*\bremote\b', True),
            (r'\s*\(hybrid\)', False),
            (r'\s*\bhybrid\b', False),
            (r'\s*\(on-site\)', False),
            (r'\s*\bon-site\b', False)
        ]
        
        for pattern, is_remote in work_type_patterns:
            if re.search(pattern, location, re.IGNORECASE):
                self.is_remote = is_remote
                location = re.sub(pattern, '', location, flags=re.IGNORECASE)
        
        # Handle multiple locations (take first)
        if ' or ' in location:
            location = location.split(' or ')[0]
        
        return location.strip()

    def clean_salary(self, text: str) -> str:
        """Standardize salary format"""
        if not text:
            return ''
        
        # Ensure $ prefix on all numbers
        cleaned = re.sub(r'(\d+K)', r'$\1', text)
        
        # Standardize range separator
        cleaned = re.sub(r'\s*-\s*', ' - ', cleaned)
        
        return cleaned

    def clean_posted(self, text: str) -> str:
        """Clean posted date string"""
        logger.debug(f"Cleaning posted date: {text}")
        if not text:
            return ''

        # Remove prefixes
        prefixes = ['Posted', 'Reposted']
        cleaned = text
        for prefix in prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned.replace(prefix, '').strip()

        logger.debug(f"Final cleaned posted date: {cleaned}")
        return cleaned

    def clean_applicants(self, text: str) -> str:
        """Clean applicants count string"""
        logger.debug(f"Cleaning applicants: {text}")
        if not text:
            return ''
            
        # Extract just the number
        match = re.search(r'(\d+)(?:\+)?\s*applicants?', text)
        if match:
            result = match.group(1)
            logger.debug(f"Extracted applicants count: {result}")
            return result
            
        logger.debug("No applicants count found")
        return text.strip()

    def clean_company(self, text: str) -> str:
        """Extract company name from various formats"""
        if not text:
            return 'Unknown'
        
        # Remove common suffixes
        patterns = [
            r'\scompany logo$',
            r'\slogo$',
            r'\sShare options$',
            r'\n.*Follow.*$',
            r'\n.*followers.*$'
        ]
        
        return self.clean_metadata(text, remove_patterns=patterns)

    def clean_metadata(self, text: str) -> dict:
        """Extract and clean all metadata fields"""
        metadata = {
            'salary': '',
            'posted': '',
            'applicants': ''
        }
        
        if not text:
            return metadata
        
        # Extract salary (ensure $ prefix)
        salary_match = re.search(r'(\$?\d+K/yr\s*-\s*\$?\d+K/yr)', text)
        if salary_match:
            salary = salary_match.group(1)
            # Ensure $ prefix on both numbers
            salary = re.sub(r'(\d+K/yr)', r'$\1', salary)
            metadata['salary'] = salary
        
        # Extract posted date (remove prefix)
        posted_match = re.search(r'(?:Posted|Reposted)\s+(\d+\s+(?:hour|day|week|month)s?\s+ago)', text)
        if posted_match:
            metadata['posted'] = posted_match.group(1)
        
        # Extract applicants (just the number)
        applicants_match = re.search(r'(\d+)\+?\s*applicants?', text)
        if applicants_match:
            metadata['applicants'] = applicants_match.group(1)
        
        return metadata

    def clean(self) -> 'JobPost':
        """Clean all fields and return a new JobPost instance"""
        return JobPost(
            title=self.clean_title(),
            company=self.company,
            location=self.clean_location(),
            url=self.url,
            salary=self.clean_salary(),
            raw_text=self.raw_text,
            is_remote=self.is_remote,
            applicants=self.clean_applicants(),
            posted=self.clean_posted(),
            date_applied=self.date_applied
        )

    @classmethod
    def from_dict(cls, data: dict) -> 'JobPost':
        """Create JobPost instance from a dictionary"""
        return cls(**{
            k: v for k, v in data.items() 
            if k in cls.__dataclass_fields__
        })

    def parse(self, text: str) -> None:
        """Parse job post text and extract all fields"""
        if not text:
            return
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # First line is typically the title
        if lines:
            self.title = lines[0]
        
        # Find location line (contains '·')
        location_line = ''
        metadata_line = ''
        for line in lines[1:]:  # Skip title line
            if '·' in line:
                parts = [p.strip() for p in line.split('·')]
                # First part before · is usually location
                location_line = parts[0]
                # Join remaining parts for metadata
                metadata_line = ' · '.join(parts[1:])
                break
        
        # Clean location first (this sets remote status)
        location_line = location_line.lower()
        if location_line == 'remote':
            self.is_remote = True
            self.location = ''
        else:
            # Process location and remote status
            location = location_line
            
            # Check for remote/hybrid indicators
            remote_patterns = [
                (r'\s*\(remote\)', ''),
                (r'\s*\bremote\b', ''),
                (r'\s*\(hybrid\)', ''),
                (r'\s*\bhybrid\b', ''),
                (r'\s*\(on-site\)', ''),
                (r'\s*\bon-site\b', '')
            ]
            
            for pattern, replacement in remote_patterns:
                if re.search(pattern, location, re.IGNORECASE):
                    if 'remote' in pattern.lower():
                        self.is_remote = True
                    location = re.sub(pattern, replacement, location, flags=re.IGNORECASE)
            
            # Handle multiple locations
            if ' or ' in location:
                location = location.split(' or ')[0]
            
            # Title case each part
            parts = [p.strip() for p in location.split(',')]
            self.location = ', '.join(p.title() for p in parts if p)
        
        # Parse metadata
        if metadata_line:
            # Extract salary (ensure $ prefix on both parts)
            salary_match = re.search(r'\$?(\d+K/yr)\s*-\s*\$?(\d+K/yr)', metadata_line)
            if salary_match:
                start, end = salary_match.groups()
                self.salary = f"${start} - ${end}"
            
            # Extract posted date (remove prefix)
            posted_match = re.search(r'(?:Posted|Reposted)\s+(\d+\s+(?:hour|day|week|month)s?\s+ago)', metadata_line)
            if posted_match:
                self.posted = posted_match.group(1)  # Just the duration part
            
            # Extract applicants (just the number)
            applicants_match = re.search(r'(\d+)\+?\s*applicants?', metadata_line)
            if applicants_match:
                self.applicants = applicants_match.group(1)  # Just the number
