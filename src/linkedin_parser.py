from typing import Dict, Union
import re
from pathlib import Path

def parse_linkedin_job(raw_text: Union[str, None]) -> Dict[str, Union[str, bool]]:
    """Parse LinkedIn job posting text into structured data"""
    # Initialize default response
    result = {
        'title': '',
        'company': '',
        'location': '',
        'salary': '',
        'is_remote': False,
        'applicants': '',
        'posted': '',
        'date_applied': '',
        'url': ''
    }
    
    if not raw_text:
        return result
        
    # Clean the input text
    if not isinstance(raw_text, str):
        return result
        
    # Remove navigation content
    lines = [line.strip() for line in raw_text.split('\n') 
            if line.strip() and 'Skip to' not in line 
            and 'notifications total' not in line]
    
    cleaned_text = ' '.join(lines)
    
    # Extract job title (usually first meaningful line)
    title_match = re.search(r'^(.*?)\s*(?:at|•|\|)', cleaned_text)
    if title_match:
        result['title'] = title_match.group(1).strip()
    
    # Extract company name
    company_match = re.search(r'(?:at|•|\|)\s*([\w\s&]+)', cleaned_text)
    if company_match:
        result['company'] = company_match.group(1).strip()
    
    # Extract location
    location_match = re.search(r'(?:in|•)\s*([\w\s,]+?)(?:\s*•|\s*$)', cleaned_text)
    if location_match:
        result['location'] = location_match.group(1).strip()
    
    # Check for remote indicators
    result['is_remote'] = bool(re.search(r'remote|work from home|wfh', 
                                       cleaned_text.lower()))
    
    # Extract salary if present
    salary_match = re.search(r'\$[\d,]+(?:\s*-\s*\$[\d,]+)?(?:/(?:yr|year|month|hr|hour))?', 
                           cleaned_text)
    if salary_match:
        result['salary'] = salary_match.group(0)
    
    # Extract applicants count
    applicants_match = re.search(r'(\d+(?:\+|\s*applicants?))', cleaned_text)
    if applicants_match:
        result['applicants'] = applicants_match.group(1)
    
    # Extract posting date
    posted_match = re.search(r'(?:Posted|Listed)\s+(\d+\s+(?:days?|hours?|weeks?)\s+ago)', 
                           cleaned_text)
    if posted_match:
        result['posted'] = posted_match.group(1)
    
    return result

def load_snapshot(file_path: Union[str, Path]) -> Dict:
    """Load and parse a LinkedIn job snapshot file"""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Snapshot file not found: {file_path}")
        
    with open(path) as f:
        data = json.load(f)
        
    if 'raw_text' not in data:
        raise ValueError(f"Invalid snapshot format in {file_path}")
        
    return parse_linkedin_job(data['raw_text'])

if __name__ == "__main__":
    # Example usage
    import json
    
    # Test with a sample snapshot
    snapshots_dir = Path("snapshots/v3")
    sample_file = next(snapshots_dir.glob("linkedin_snapshot_*.json"))
    
    with open(sample_file) as f:
        data = json.load(f)
        
    result = parse_linkedin_job(data['raw_text'])
    print(f"Parsed data from {sample_file.name}:")
    print(json.dumps(result, indent=2)) 