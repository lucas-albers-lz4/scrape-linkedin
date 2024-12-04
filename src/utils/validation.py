from datetime import datetime
from typing import List
from ..models.job_post import JobPost
import re
from ..parser.constants import LocationPatterns

def validate_job_post(job_post: JobPost) -> List[str]:
    """Comprehensive validation of job post data."""
    errors = []
    
    # Required fields validation
    if not job_post.company or job_post.company == "Unknown":
        errors.append("Missing or invalid company name")
    
    if not job_post.title or job_post.title == "Unknown":
        errors.append("Missing or invalid job title")
    
    # Location validation
    if not job_post.location:
        errors.append("Missing location")
    elif not LocationPatterns.is_us_location(job_post.location):
        errors.append("Location does not appear to be in United States")
    
    # Remote validation
    if "remote" in job_post.location.lower():
        if "hybrid" in job_post.raw_text.lower():
            errors.append("Job claims remote but mentions hybrid work")
        if "on-site" in job_post.raw_text.lower() or "onsite" in job_post.raw_text.lower():
            errors.append("Job claims remote but mentions on-site work")

    # Salary validation
    if job_post.salary:
        if not any(char.isdigit() for char in job_post.salary):
            errors.append("Salary format appears invalid")
        if job_post.salary.count('-') != 1 and 'K' in job_post.salary:
            errors.append("Salary range format appears invalid")
    
    # Date validation - only check date_applied since it's always today's date
    try:
        datetime.strptime(job_post.date_applied, "%m/%d/%Y")
    except ValueError:
        errors.append("Invalid date_applied format (should be MM/DD/YYYY)")
    
    # Posted date validation - allow relative dates
    if job_post.posted and not any(word in job_post.posted.lower() 
                                  for word in ['hour', 'day', 'week', 'month', 'ago']):
        errors.append("Invalid posted date format")
    
    return errors

def validate_salary_format(salary: str) -> bool:
    """Validate salary string format."""
    if not salary:
        return True  # Empty salary is allowed
        
    # Remove common salary formatting
    clean_salary = salary.replace('$', '').replace(',', '').replace(' ', '')
    
    # Check for range format (e.g., "130000-300000" or "130K-300K")
    parts = clean_salary.split('-')
    if len(parts) != 2:
        return False
        
    # Validate each part
    for part in parts:
        part = part.upper()
        if 'K' in part:
            part = part.replace('K', '000')
        if not part.replace('000', '').isdigit():
            return False
    
    return True

def is_csv_data(content: str) -> bool:
    """Check if content appears to be CSV data from a previous run."""
    # Quick initial checks
    if not content or not isinstance(content, str):
        return False
        
    # Check for our exact CSV format (16 fields, all quoted)
    try:
        # Split on comma, preserving quoted content
        fields = content.split('","')
        
        # Should have exactly 16 fields when properly split
        if len(fields) != 16:
            return False
            
        # First field should start with a quote
        if not fields[0].startswith('"'):
            return False
            
        # Last field should end with a quote
        if not fields[-1].endswith('"'):
            return False
            
        # Check for date format in expected positions (5th and 7th fields)
        date_pattern = r'\d{1,2}/\d{1,2}/\d{4}'
        if not (re.search(date_pattern, fields[4]) and re.search(date_pattern, fields[6])):
            return False
            
        # Check for "LinkedIn" in source field (6th field)
        if 'LinkedIn' not in fields[5]:
            return False
            
        return True
        
    except Exception:
        return False
