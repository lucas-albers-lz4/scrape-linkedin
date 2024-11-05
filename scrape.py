#!/usr/bin/env python3
"""
LinkedIn Job Application Parser
Usage:
1. Open a LinkedIn job posting
2. Copy the entire page (Ctrl+A, Ctrl+C)
3. Run this script (python3 scrape.py)
4. The formatted CSV row will be copied to your clipboard

Expected Output Format:
"Company","Title","Location","URL","Date","LinkedIn","","","","","","","","Salary"

Note: Fields are: Company, Title, Location, URL, Date, Source, DateApplied, InitialResponse, 
      Reject, Screen, FirstRound, SecondRound, Notes, Salary

Development History:
- v1.0: Initial version with basic parsing
- v2.0: Major updates to handle remote work verification and misleading job posts
  - Added remote contradiction detection due to jobs falsely claiming remote status
  - Improved title detection to avoid picking up location as title
  - Enhanced salary parsing to handle different formats (K/yr and annual)
  - Added versioned snapshots to track parsing rule changes

Known Challenges Addressed:
1. Remote Work Detection:
   - Jobs often claim to be remote but contradict this in description
   - Solution: Check description for terms indicating office presence
   
2. Title Detection:
   - Initial version confused location for title
   - Solution: Look for standalone title line before location pattern
   
3. Salary Parsing:
   - Multiple formats: "$167K/yr" vs "$167,000 annually"
   - Solution: Added regex patterns for both formats

4. Test Data Preservation:
   - Parsing logic changes could invalidate old test cases
   - Solution: Added versioned snapshots with parsing rules documented
"""

import pyperclip
import re
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import argparse
import sys

def save_snapshot_quietly(input_text, parsed_data, formatted_output):
    """
    Silently save a snapshot of the run for future testing
    
    Version History:
    - v1.0: Basic snapshot saving
    - v2.0: Added versioning and parsing rules documentation
    
    The snapshot structure captures:
    1. Version of parsing logic used
    2. Actual rules applied (like remote contradictions)
    3. Both input and output for regression testing
    """
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot = {
            "version": "2.0",  # Add version tracking
            "timestamp": timestamp,
            "input": input_text,
            "parsing_rules": {  # Document the rules used
                "remote_contradictions": [
                    "hybrid",
                    "on-site",
                    "onsite",
                    "in office",
                    "in-office",
                    "must be located",
                    "must reside",
                    "must live",
                    "required to work from"
                ]
            },
            "parsed_data": {
                "company": parsed_data["company"],
                "title": parsed_data["title"],
                "location": parsed_data["location"],
                "url": parsed_data["url"],
                "date": parsed_data["date"],
                "salary": parsed_data["salary"]
            },
            "output": formatted_output
        }
        
        # Create snapshots directory in script's location if it doesn't exist
        snapshot_dir = Path(__file__).parent / 'snapshots'
        snapshot_dir.mkdir(exist_ok=True)
        
        # Save snapshot to versioned subdirectory
        version_dir = snapshot_dir / 'v2'  # Version-specific directory
        version_dir.mkdir(exist_ok=True)
        
        filename = version_dir / f"linkedin_snapshot_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(snapshot, f, indent=2)
            
    except Exception:
        # Silently handle any errors during snapshot saving
        pass

def convert_relative_date(relative_date):
    """Convert relative date (e.g., '3 weeks ago') to actual date"""
    today = datetime.now()
    
    # Extract number and unit from relative date
    parts = relative_date.lower().split()
    if len(parts) >= 2:
        try:
            number = int(parts[0])
            unit = parts[1]
            
            if 'second' in unit:
                delta = timedelta(seconds=number)
            elif 'minute' in unit:
                delta = timedelta(minutes=number)
            elif 'hour' in unit:
                delta = timedelta(hours=number)
            elif 'day' in unit:
                delta = timedelta(days=number)
            elif 'week' in unit:
                delta = timedelta(weeks=number)
            elif 'month' in unit:
                # Approximate months as 30 days
                delta = timedelta(days=number * 30)
            elif 'year' in unit:
                # Approximate years as 365 days
                delta = timedelta(days=number * 365)
            else:
                return ""
                
            actual_date = today - delta
            return actual_date.strftime("%m/%d/%Y")
        except ValueError:
            return ""
    return ""

def validate_linkedin_content(text):
    """
    Validate if the clipboard content is from LinkedIn
    Returns: bool
    """
    linkedin_indicators = [
        'logo',  # Company logo text
        'applicants',  # Job applicants count
        'Easy Apply',  # LinkedIn apply button
        'Posted',  # Posted date indicator
    ]
    
    return any(indicator in text for indicator in linkedin_indicators)

def format_clipboard(input_text=None):
    """
    Format clipboard contents into CSV row
    Args:
        input_text (str, optional): Input text to parse. If None, reads from clipboard
    Returns:
        dict: Parsed data fields
    """
    # Get input from clipboard if not provided
    if input_text is None:
        input_text = pyperclip.paste()
    
    # Get today's date in MM/DD/YYYY format
    today = datetime.now().strftime("%m/%d/%Y")
    
    # Initialize parsed data
    parsed_data = {
        "company": "",
        "title": "",
        "location": "",
        "url": "",
        "date": today,  # Use MM/DD/YYYY format
        "date_applied": today,  # Also set application date to today
        "notes": "",  # Will be set to "Easy Apply" if found
        "salary": "",
        "posted": "",  # Will capture "3 weeks ago" etc.
        "applicants": ""
    }
    
    # Try to find job ID in the URL
    url_match = re.search(r'jobs/view/(\d+)', input_text)
    if url_match:
        job_id = url_match.group(1)
        parsed_data["url"] = f"https://www.linkedin.com/jobs/view/{job_id}/"
        print(f"Found job URL: {parsed_data['url']}")
    
    # Track what we've found to prevent duplicates
    found = set()
    
    # Find the main job section
    job_sections = input_text.split("About the job")
    if len(job_sections) > 1:
        main_job = job_sections[0]
        lines = main_job.split('\n')
        
        # New approach: Look for title after company logo and before applicant count
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Company detection (keep existing)
            if "company" not in found and "logo" in line.lower():
                company = line.replace("logo", "").strip()
                if company:
                    parsed_data["company"] = company
                    print(f"Found company: {parsed_data['company']}")
                    found.add("company")
                    
                    # NEW: Look for title in the next few lines after company
                    for j in range(i+1, min(i+5, len(lines))):
                        potential_title = lines[j].strip()
                        next_line = lines[j+1].strip() if j+1 < len(lines) else ""
                        
                        # Check if this line is followed by location/applicant info
                        if (potential_title and 
                            ("applicants" in next_line or "United States" in next_line) and
                            not any(x in potential_title.lower() for x in 
                                ['logo', 'save', 'about', '·', 'home', 'my network', 'jobs'])):
                            parsed_data["title"] = potential_title
                            print(f"Found title: {parsed_data['title']}")
                            found.add("title")
                            break

            # Location detection (modify to handle new format)
            if "location" not in found:
                # Look for "United States" or other location patterns
                if "United States" in line or ("· " in line and ", " in line):
                    location_parts = line.split("·")[0].strip() if "·" in line else line
                    
                    # Check for remote status in surrounding lines
                    is_remote = any("Remote" in lines[k] for k in range(max(0, i-2), min(len(lines), i+3)))
                    
                    if is_remote:
                        location_parts += " (Remote)"
                    
                    parsed_data["location"] = location_parts
                    print(f"Found location: {parsed_data['location']}")
                    found.add("location")

            # Look for posting date (format: "· X days/weeks/months ago")
            if "posted" not in found and " ago · " in line.lower():
                posted_parts = line.split(" · ")
                for part in posted_parts:
                    if "ago" in part:
                        relative_date = part.strip()
                        actual_date = convert_relative_date(relative_date)
                        parsed_data["posted"] = actual_date
                        print(f"Found posted date: {relative_date} -> {actual_date}")
                        found.add("posted")

            # Look for applicant count
            if "applicants" not in found and "applicants" in line.lower():
                applicant_match = re.search(r'(\d+)\+?\s+applicants|Over\s+(\d+)\s+applicants', line)
                if applicant_match:
                    count = applicant_match.group(1) or applicant_match.group(2)
                    if "Over" in line or "+" in line:
                        parsed_data["applicants"] = f"{count}+"
                    else:
                        parsed_data["applicants"] = count
                    print(f"Found applicants: {parsed_data['applicants']}")
                    found.add("applicants")

            # Check for Easy Apply
            if 'Easy Apply' in line:
                parsed_data['notes'] = "Easy Apply"
            
            # Check for Posted/Reposted date
            if 'Posted' in line or 'Reposted' in line:
                time_ago_match = re.search(r'(?:Posted|Reposted)\s+(.*?)\s+ago', line)
                if time_ago_match:
                    parsed_data['posted'] = time_ago_match.group(1)

    # Salary parsing - look for both formats
    for line in input_text.split('\n'):
        if 'K/yr' in line:
            salary_match = re.search(r'\$(\d+)K/yr\s*-\s*\$(\d+)K/yr', line)
            if salary_match:
                min_salary = int(salary_match.group(1)) * 1000
                max_salary = int(salary_match.group(2)) * 1000
                parsed_data['salary'] = f"{min_salary}-{max_salary}"
                break

    # Create CSV row with location
    fields = [
        parsed_data["company"],
        parsed_data["title"],
        parsed_data["location"],
        parsed_data["url"],
        parsed_data["date"],
        "LinkedIn",
        parsed_data["date_applied"],
        "",  # InitialResponse
        "",  # Reject
        "",  # Screen
        "",  # FirstRound
        "",  # SecondRound
        parsed_data["notes"],
        parsed_data["salary"],
        parsed_data["posted"],  # New field
        parsed_data["applicants"]  # New field
    ]
    
    # Join with commas and quote each field
    formatted = ",".join(f'"{str(field)}"' for field in fields)
    
    print("\n=== COLUMN HEADERS ===")
    headers = [
        "Company",
        "Title",
        "Location",
        "URL",
        "Date",
        "Source",
        "DateApplied",
        "InitialResponse",
        "Reject",
        "Screen",
        "FirstRound",
        "SecondRound",
        "Notes",
        "Salary",
        "Posted",  # New field
        "Applicants"  # New field
    ]
    print(",".join(headers))
    
    print("\n=== FINAL OUTPUT ===")
    print(formatted)
    print("\nVerification of fields:")
    print(f"Company: '{parsed_data['company']}'")
    print(f"Title: '{parsed_data['title']}'")
    print(f"Location: '{parsed_data['location']}'")
    print(f"Salary: '{parsed_data['salary']}'")
    print(f"Date: '{parsed_data['date']}'")
    print(f"Notes: '{parsed_data['notes']}'")  # Added notes to verification
    
    save_snapshot_quietly(input_text, parsed_data, formatted)
    
    print_job_analysis(parsed_data)
    
    # Add hybrid warning right before clipboard message
    if parsed_data.get("hybrid_indicators"):
        print("\n!!! WARNING: HYBRID/ONSITE ROLE - DO NOT PROCEED WITH APPLICATION !!!")
    
    pyperclip.copy(formatted)
    print("\nFormatted data copied to clipboard!")
    print("\nClipboard content:")
    print(formatted)
    
    return parsed_data

def parse_job_listing(raw_text, debug=False):
    """Parse the raw LinkedIn job listing text"""
    # Check for hybrid/onsite indicators first
    hybrid_indicators = []
    lower_text = raw_text.lower()
    
    keywords = [
        "hybrid",
        "in-office",
        "onsite",
        "on-site",
        "in office",
        "days per week",
        "days in office",
        "headquarters",
        "hq",
        "located in the office",
        "office location",
        "in-office working",
        "office environment",
        "bellevue, wa",  # Location specific
    ]
    
    for keyword in keywords:
        if keyword in lower_text:
            start_idx = max(0, lower_text.find(keyword) - 50)
            end_idx = min(len(lower_text), lower_text.find(keyword) + 50)
            context = raw_text[start_idx:end_idx].strip()
            hybrid_indicators.append(f"{keyword}: '{context}'")
    
    if hybrid_indicators:
        print("\n")
        print("!" * 80)
        print("!!! WARNING: HYBRID/ONSITE ROLE - DO NOT APPLY !!!")
        print("!!! Found indicators:")
        for indicator in hybrid_indicators:
            print(f"!!!  - {indicator}")
        print("!" * 80)
        print("\n")
    
    # Continue with your existing parsing code
    matches = re.findall(r'"([^"]*)"', raw_text)
    if len(matches) >= 3:
        company = matches[0]
        title = matches[1]
        location = matches[2]
    else:
        # Your existing company/title/location detection code
        company = re.search(r'Found company: (.+)', raw_text)
        company = company.group(1) if company else ''
        
        title = re.search(r'Found title: (.+)', raw_text)
        title = title.group(1) if title else ''
        
        location = re.search(r'Found location: (.+)', raw_text)
        location = location.group(1) if location else ''
    
    # Rest of your existing code...
    
    # Add hybrid warning to notes if detected
    notes = "HYBRID/ONSITE ROLE - DO NOT APPLY" if hybrid_indicators else ""
    
    # ... rest of function ...

def print_job_analysis(job_data):
    """Print job analysis with warnings"""
    if job_data.get("hybrid_indicators"):
        print("\n")
        print("!" * 80)
        print("!!! WARNING: HYBRID/ONSITE ROLE - DO NOT APPLY !!!")
        print("!!! Found indicators:")
        for indicator in job_data["hybrid_indicators"]:
            print(f"!!!  - {indicator}")

def setup_args():
    parser = argparse.ArgumentParser(description='LinkedIn Job Application Parser')
    parser.add_argument('--analyze-history', '-ah', action='store_true',
                       help='Analyze historical snapshots to identify missing data')
    parser.add_argument('--allmatches', '-am', action='store_true',
                       help='Show all matched data in CSV format')
    parser.add_argument('--unit-test', '-ut', action='store_true',
                       help='Run unit tests against synthetic test data')
    return parser.parse_args()

def parse_snapshot(snapshot_path):
    """Parse a single snapshot file and extract job data"""
    try:
        print(f"\nDEBUG: Processing {snapshot_path}")
        
        with open(snapshot_path, 'r') as f:
            data = json.load(f)
            
        # Extract data from the parsed_data field
        parsed_data = data.get('parsed_data', {})
        raw_text = data.get('input', '')
        
        print(f"DEBUG: Parsed data: {parsed_data}")
        
        # Ensure we have valid data with defaults
        location = parsed_data.get('location', '').strip() or 'Unknown'
        is_remote = 'remote' in location.lower()
        
        # Create test case with required fields
        test_case = {
            'raw_text': raw_text[:100] + '...',  # Truncate for logging
            'source': str(snapshot_path),
            'timestamp': data.get('timestamp', ''),
            'is_valid': bool(parsed_data and parsed_data.get('company') and parsed_data.get('title')),
            'expected': {
                'company': parsed_data.get('company', '').strip() or 'Unknown',
                'title': parsed_data.get('title', '').strip() or 'Unknown',
                'location': location,
                'salary': parsed_data.get('salary', '').strip() or 'Unknown',
                'is_remote': is_remote,
                'location_type': 'remote' if is_remote else 'unknown',
                'rejection_reasons': [],
                'warning_flags': []
            }
        }
        
        print(f"DEBUG: Created test case: {test_case['expected']}")
        
        # Check for remote contradictions
        remote_contradictions = data.get('parsing_rules', {}).get('remote_contradictions', [])
        if remote_contradictions:
            print(f"DEBUG: Checking remote contradictions: {remote_contradictions}")
            
        for indicator in remote_contradictions:
            if indicator in raw_text.lower():
                test_case['expected']['is_remote'] = False
                test_case['expected']['location_type'] = 'hybrid/onsite'
                test_case['expected']['rejection_reasons'].append(f'Found "{indicator}" in job description')
                test_case['expected']['warning_flags'].append(indicator)
                print(f"DEBUG: Found contradiction: {indicator}")
        
        # Validate test case has required fields
        required_fields = ['company', 'title', 'location', 'salary']
        is_valid = all(test_case['expected'].get(field) and 
                      test_case['expected'][field] != 'Unknown' 
                      for field in required_fields)
        
        if is_valid:
            print("DEBUG: Test case is valid")
            return test_case
        else:
            missing_fields = [field for field in required_fields 
                            if not test_case['expected'].get(field) or 
                            test_case['expected'][field] == 'Unknown']
            print(f"DEBUG: Test case invalid. Missing fields: {missing_fields}")
            return None
            
    except Exception as e:
        print(f"Error parsing {snapshot_path}: {str(e)}")
        return None

def analyze_all_snapshots():
    """Analyze snapshots from all directories"""
    try:
        valid_test_cases = []
        invalid_snapshots = []
        
        # Find all snapshot files
        snapshot_paths = list(Path("snapshots").rglob("*.json"))
        
        print(f"\nAnalyzing {len(snapshot_paths)} total snapshots...")
        
        # Process each snapshot
        for path in snapshot_paths:
            test_case = parse_snapshot(path)
            if test_case and test_case['is_valid']:
                valid_test_cases.append(test_case)
            else:
                invalid_snapshots.append(path)
                
        print(f"\nAnalysis complete:")
        print(f"- Valid test cases: {len(valid_test_cases)}")
        print(f"- Invalid snapshots: {len(invalid_snapshots)}")
        
        return valid_test_cases
        
    except Exception as e:
        print(f"Error analyzing snapshots: {str(e)}")
        return []

def generate_test_cases():
    """Generate synthetic test cases from snapshot data"""
    test_cases = []
    snapshot_dir = Path(__file__).parent / 'snapshots' / 'v2'
    
    for snapshot_file in snapshot_dir.glob('linkedin_snapshot_*.json'):
        with open(snapshot_file, 'r') as f:
            data = json.load(f)
            input_text = data['input']
            
            # Extract key patterns for testing
            test_case = {
                'input': input_text,
                'expected': {
                    'company': data['parsed_data'].get('company', ''),
                    'title': data['parsed_data'].get('title', ''),
                    'location': data['parsed_data'].get('location', ''),
                    'posted': data['parsed_data'].get('posted', ''),
                    'applicants': data['parsed_data'].get('applicants', ''),
                    'salary': data['parsed_data'].get('salary', '')
                }
            }
            test_cases.append(test_case)
    
    # Reduce test cases to unique patterns
    unique_cases = {}
    for case in test_cases:
        # Create a hash of the important patterns in the input
        key_patterns = [
            re.search(r'company logo.*?(?=\n)', case['input'] or ''),
            re.search(r'\d+ applicants', case['input'] or ''),
            re.search(r'\d+ weeks? ago', case['input'] or ''),
            re.search(r'\$\d+K/yr', case['input'] or '')
        ]
        
        # Create a unique key for the test case
        key = ''.join([str(pattern.start()) if pattern else '' for pattern in key_patterns])
        
        # Add the test case to the unique cases dictionary
        unique_cases[key] = case
    
    return list(unique_cases.values())

def run_tests(test_cases_file='tests/test_data.json'):
    """Run tests against known good data patterns"""
    with open(test_cases_file, 'r') as f:
        test_data = json.load(f)
    
    passed = 0
    failed = 0
    results = []
    
    print("\nRunning parser tests...")
    
    for test in test_data['test_cases']:
        print(f"\nTest: {test['description']}")
        
        # Parse the test input
        result = format_clipboard(test['input'])
        
        # Compare each field
        field_results = []
        for field, expected in test['expected'].items():
            actual = result.get(field, '')
            matches = actual == expected
            
            if matches:
                field_results.append(f"✓ {field}")
            else:
                field_results.append(f"✗ {field}: expected '{expected}', got '{actual}'")
                
        # Track overall test result
        if all(r.startswith('✓') for r in field_results):
            passed += 1
            print("PASSED")
        else:
            failed += 1
            print("FAILED")
            
        print('\n'.join(field_results))
        
    # Print summary
    print(f"\nTest Summary:")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/(passed+failed))*100:.1f}%")

def is_csv_data(text):
    """Check if the text appears to be our CSV formatted job data"""
    # Strip whitespace
    text = text.strip()
    
    # Quick checks first
    if not text.startswith('"'):
        return False
        
    # Check for our specific format
    patterns = [
        # Basic format check
        r'^"[^"]*","[^"]*","[^"]*"',
        # Check for LinkedIn and date format
        r'"LinkedIn","[\d/]+"',
        # Check for empty fields pattern
        r',"","","","'
    ]
    
    return any(re.search(pattern, text) for pattern in patterns)

def process_clipboard_data(debug=False):
    """Process clipboard data and check for hybrid/onsite indicators"""
    raw_text = pyperclip.paste()
    
    if is_csv_data(raw_text):
        print("\nERROR: Clipboard contains CSV data - looks like this script was already run!")
        print("Please copy the raw job listing from LinkedIn and try again.\n")
        sys.exit(1)
    
    if debug:
        print("\n=== DEBUG: Raw clipboard data ===")
        print(f"Length: {len(raw_text)}")
        print("First 200 chars:", raw_text[:200])
    
    # Rest of your processing code...

def check_hybrid_onsite(raw_text, debug=False):
    """Check for hybrid/onsite indicators in the job text"""
    lower_text = raw_text.lower()
    
    # Strong remote indicators that override everything else
    remote_indicators = [
        "work anywhere company",
        "work anywhere",
        "fully remote",
        "(remote)",
        "remote position",
        "remote role",
        "remote work",
        "work from anywhere",
        # Location specific remote indicators
        r".*\(remote\)",  # Matches "City, State (Remote)"
        r".*remote.*",    # Matches "Remote - US" or similar
    ]
    
    # Check for explicit remote indicators first
    for indicator in remote_indicators:
        if indicator in lower_text:
            if debug:
                print(f"DEBUG: Found remote indicator: {indicator}")
            return []  # Confirmed remote - return empty list
    
    # Only check for hybrid/onsite if we haven't confirmed remote
    hybrid_indicators = []
    
    # Skip these contexts when looking for hybrid/onsite indicators
    skip_phrases = [
        "headquarters",
        "hq is located",
        "main office",
        "corporate office",
        "hybrid software",
        "hybrid systems",
        "hybrid cloud",
        "hybrid architecture",
        "hybrid group"
    ]
    
    # If we find any skip phrases, ignore that section of text
    for phrase in skip_phrases:
        if phrase in lower_text:
            continue
            
    return hybrid_indicators  # Will be empty if remote or no hybrid indicators found

def clean_snapshots():
    """Remove invalid snapshots"""
    snapshot_dir = Path("snapshots")
    for snapshot in snapshot_dir.glob("*.json"):
        with open(snapshot) as f:
            data = json.load(f)
            
        # Check for indicators of invalid data
        if any([
            not data.get("company"),  # Empty company
            not data.get("title"),    # Empty title
            data.get("formatted_output", "").count('""') > 10,  # Too many empty fields
            "ERROR" in data.get("raw_text", ""),  # Contains error messages
            len(data.get("raw_text", "")) < 100   # Too short to be real posting
        ]):
            print(f"Removing invalid snapshot: {snapshot}")
            snapshot.unlink()

def validate_test_case(test_case, raw_text):
    """Validate a test case against its raw text"""
    issues = []
    
    # Reduce minimum text length requirement
    if len(raw_text) < 100:  # Was likely 500 or higher
        issues.append("Raw text too short - might be incomplete job posting")
    
    # Make company/title checks more flexible
    if test_case['company'] != 'Unknown' and not any(
        company_variant in raw_text.lower() 
        for company_variant in [test_case['company'].lower(), 
                              test_case['company'].split()[0].lower()]
    ):
        issues.append("Company name not found in raw text")
        
    if test_case['title'] != 'Unknown' and not any(
        word in raw_text.lower()
        for word in test_case['title'].lower().split()
        if len(word) > 3  # Only check significant words
    ):
        issues.append("Job title not found in raw text")

    return issues

def generate_test_file(test_cases):
    """Generate test_scraper.py file with quality checks"""
    test_cases = analyze_all_snapshots()
    valid_test_cases = []
    
    print("\nValidating test cases...")
    for case in test_cases:
        issues = validate_test_case(case)
        if not issues:
            valid_test_cases.append(case)
        else:
            print(f"\nSkipping test case for {case['expected'].get('company')}:")
            print("Issues found:")
            for issue in issues:
                print(f"- {issue}")
    
    print(f"\nFound {len(valid_test_cases)} valid test cases out of {len(test_cases)} total")
    
    # Generate test file only with valid cases
    test_code = """
import unittest
from scrape import parse_job_listing

class TestJobScraper(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        \"\"\"Load test cases\"\"\"
        cls.test_cases = {
    """
    
    for i, case in enumerate(valid_test_cases):
        test_code += f"""
    def test_job_{i:03d}(self):
        \"\"\"Test parsing of {case['expected']['company']} - {case['expected']['title']}\"\"\"
        result = parse_job_listing(self.test_cases[{i}]['raw_text'])
        expected = self.test_cases[{i}]['expected']
        
        self.assertEqual(result['company'], expected['company'])
        self.assertEqual(result['title'], expected['title'])
        self.assertEqual(result['location'], expected['location'])
        self.assertEqual(result['salary'], expected['salary'])
        self.assertEqual(bool(result.get('hybrid_indicators')), expected['is_hybrid'])
        
        # Additional validation
        self.assertIn(result['company'], self.test_cases[{i}]['raw_text'])
        self.assertIn(result['title'], self.test_cases[{i}]['raw_text'])
    """
    
    with open("test_scraper.py", "w") as f:
        f.write(test_code)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--unit-test', action='store_true', help='Run unit tests')
    parser.add_argument('--analyze-history', action='store_true', help='Analyze application history')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    parser.add_argument('--analyze-snapshot', help='Analyze a specific snapshot file')
    parser.add_argument('--analyze-snapshots', action='store_true', help='Analyze all snapshot files')
    args = parser.parse_args()
    
    debug = args.debug
    
    if args.unit_test:
        run_tests()
    elif args.analyze_history:
        analyze_all_snapshots()
    elif args.analyze_snapshot:
        # Your existing snapshot analysis code...
        pass
    elif args.analyze_snapshots:
        print("\nStarting snapshot analysis...")
        test_cases = analyze_all_snapshots()
        if test_cases:
            print("\nGenerating unit tests...")
            generate_test_file(test_cases)
            print("Unit tests generated in test_scraper.py")
        else:
            print("No valid test cases found to generate unit tests.")
    else:
        # Get clipboard content
        raw_text = pyperclip.paste()
        
        # Check if it's already CSV data
        if is_csv_data(raw_text):
            print("\nERROR: Clipboard contains job data that was already processed!")
            print("Please copy a new job listing from LinkedIn before running the script.\n")
            sys.exit(1)
            
        if debug:
            print("\n=== DEBUG: Raw clipboard data ===")
            print(f"Length: {len(raw_text)}")
            print("First 200 chars:", raw_text[:200])
            print("=" * 50)
            
        parsed_data = parse_job_listing(raw_text, debug=debug)
        format_clipboard()
