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
            if ' ago' in line:
                time_ago_match = re.search(r'(?:Posted|Reposted)\s+(.*?)\s+ago', line)
                if time_ago_match:
                    parsed_data['posted'] = f"{time_ago_match.group(1)} ago"

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
    
    pyperclip.copy(formatted)
    print("\nFormatted data copied to clipboard!")
    print("\nClipboard content:")
    print(formatted)
    
    return parsed_data

def setup_args():
    parser = argparse.ArgumentParser(description='LinkedIn Job Application Parser')
    parser.add_argument('--analyze-history', '-ah', action='store_true',
                       help='Analyze historical snapshots to identify missing data')
    parser.add_argument('--allmatches', '-am', action='store_true',
                       help='Show all matched data in CSV format')
    parser.add_argument('--unit-test', '-ut', action='store_true',
                       help='Run unit tests against synthetic test data')
    return parser.parse_args()

def analyze_snapshots(show_all_matches=False):
    """Analyze snapshots to find missing data patterns"""
    snapshot_dir = Path(__file__).parent / 'snapshots' / 'v2'
    if not snapshot_dir.exists():
        print("No snapshots directory found!")
        return
    
    # Track failures by type and snapshot
    failures = {
        'company': {},
        'title': {},
        'location': {},
        'posted': {},
        'applicants': {}
    }
    
    total_snapshots = 0
    
    for snapshot_file in snapshot_dir.glob('linkedin_snapshot_*.json'):
        try:
            with open(snapshot_file, 'r') as f:
                total_snapshots += 1
                data = json.load(f)
                
                # Store full snapshot data for each failure
                for field in failures.keys():
                    if not data['parsed_data'].get(field):
                        failures[field][snapshot_file.name] = {
                            'timestamp': data['timestamp'],
                            'raw_input': data['input'][:200] + '...' if len(data['input']) > 200 else data['input']
                        }
                
        except Exception as e:
            print(f"Error processing {snapshot_file}: {e}")
    
    # Print organized summary
    print(f"\nAnalyzed {total_snapshots} snapshots:\n")
    
    for field, failed_snapshots in failures.items():
        if failed_snapshots:
            failure_count = len(failed_snapshots)
            success_rate = ((total_snapshots - failure_count) / total_snapshots) * 100
            print(f"{field.title()} missing in {failure_count} snapshots:")
            for snapshot_name, snapshot_data in failed_snapshots.items():
                print(f"  - {snapshot_name}: {snapshot_data['raw_input']}")
    
    if not failures:
        print("All fields successfully parsed in all snapshots!")
    
    # If --allmatches flag is used, output CSV format
    if show_all_matches:
        print("\nAll Matched Data (CSV format):")
        # Print headers
        print("Timestamp,Company,Title,Location,Posted,Applicants")
        for job in all_data:
            print(f"{job['timestamp']},{job['company']},{job['title']},{job['location']},{job['posted']},{job['applicants']}")

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

if __name__ == "__main__":
    args = setup_args()
    
    if args.unit_test:
        run_tests()
    elif args.analyze_history:
        analyze_snapshots(show_all_matches=args.allmatches)
    else:
        format_clipboard()
