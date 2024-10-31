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
from datetime import datetime
import json
import os
from pathlib import Path

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

def format_clipboard():
    text = pyperclip.paste()
    today = datetime.now().strftime("%m/%d/%Y")
    
    print("=== PROCESSING CLIPBOARD CONTENT ===")
    
    # Initialize variables
    parsed_data = {
        "company": "",
        "title": "",
        "location": "",
        "url": "",
        "date": today,
        "salary": ""
    }
    
    # Track what we've found to prevent duplicates
    found = set()
    
    # Find the main job section
    job_sections = text.split("About the job")
    if len(job_sections) > 1:
        main_job = job_sections[0]
        
        lines = main_job.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Company detection
            if "company" not in found and "logo" in line.lower():
                company = line.replace("logo", "").strip()
                if company:
                    parsed_data["company"] = company
                    print(f"Found company: {parsed_data['company']}")
                    found.add("company")
            
            # Title detection - look for standalone title line
            if "title" not in found and line and not any(x in line.lower() for x in ['logo', 'save', 'about', '·', ',']):
                # Check if next line contains location pattern
                if i + 1 < len(lines) and "· " in lines[i + 1]:
                    title = line.strip()
                    if title and len(title.split()) <= 6:  # Most titles are 2-6 words
                        parsed_data["title"] = title
                        print(f"Found title: {parsed_data['title']}")
                        found.add("title")
            
            # Location detection with remote verification
            if "location" not in found and ", " in line and "· " in line:
                # Get base location (City, State)
                location_parts = line.split("· ")[0].strip()
                
                # First check if it claims to be remote
                is_remote = False
                for check_line in lines[i:i+3]:
                    if "Remote" in check_line:
                        is_remote = True
                        break
                
                # Now verify against the job description for contradictions
                job_description = job_sections[1] if len(job_sections) > 1 else ""
                has_contradiction = any(phrase in job_description.lower() for phrase in [
                    "hybrid",
                    "on-site",
                    "onsite",
                    "in office",
                    "in-office",
                    "must be located",
                    "must reside",
                    "must live",
                    "required to work from"
                ])
                
                # Only mark as remote if there are no contradictions
                if is_remote and not has_contradiction:
                    location_parts += " (Remote)"
                elif is_remote and has_contradiction:
                    location_parts += " (Claims Remote - Check Description)"
                    
                parsed_data["location"] = location_parts
                print(f"Found location: {parsed_data['location']}")
                found.add("location")
            
            # Salary detection
            if "salary" not in found:
                # Try K/yr format
                if "$" in line and "/yr" in line and "-" in line:
                    salary_match = re.search(r'\$?(\d+)K?/yr\s*-\s*\$?(\d+)K?/yr', line)
                    if salary_match:
                        start_salary = int(salary_match.group(1)) * 1000
                        end_salary = int(salary_match.group(2)) * 1000
                        parsed_data["salary"] = f"{start_salary}-{end_salary}"
                        print(f"Found salary: {parsed_data['salary']}")
                        found.add("salary")
                # Try annual format in description
                elif "annually" in line.lower() and "$" in line:
                    salary_match = re.search(r'\$?([\d,]+)-\$?([\d,]+)', line)
                    if salary_match:
                        start_salary = salary_match.group(1).replace(',', '')
                        end_salary = salary_match.group(2).replace(',', '')
                        parsed_data["salary"] = f"{start_salary}-{end_salary}"
                        print(f"Found salary: {parsed_data['salary']}")
                        found.add("salary")

    # Create CSV row with location
    fields = [
        parsed_data["company"],
        parsed_data["title"],
        parsed_data["location"],
        parsed_data["url"],
        parsed_data["date"],
        "LinkedIn",
        "",  # DateApplied
        "",  # InitialResponse
        "",  # Reject
        "",  # Screen
        "",  # FirstRound
        "",  # SecondRound
        "",  # Notes
        parsed_data["salary"]  # Salary at the end
    ]
    
    # Join with commas and quote each field
    formatted = ",".join(f'"{str(field)}"' for field in fields)
    
    print("\n=== FINAL OUTPUT ===")
    print(formatted)
    print("\nVerification of fields:")
    print(f"Company: '{parsed_data['company']}'")
    print(f"Title: '{parsed_data['title']}'")
    print(f"Location: '{parsed_data['location']}'")
    print(f"Salary: '{parsed_data['salary']}'")
    print(f"Date: '{parsed_data['date']}'")
    
    save_snapshot_quietly(text, parsed_data, formatted)
    
    pyperclip.copy(formatted)
    print("\nFormatted data copied to clipboard!")
    print("\nClipboard content:")
    print(formatted)

if __name__ == "__main__":
    format_clipboard()
