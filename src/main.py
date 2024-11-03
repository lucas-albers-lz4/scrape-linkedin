#!/usr/bin/env python3
"""
LinkedIn Job Application Parser
Usage:
1. Open a LinkedIn job posting
2. Copy the entire page (Ctrl+A, Ctrl+C)
3. Run this script
4. The formatted CSV row will be copied to your clipboard
"""

import argparse
from datetime import datetime
from pathlib import Path
import json
import pyperclip

from src.utils.clipboard import get_clipboard_content, set_clipboard_content, format_csv_row
from src.parser.job_parser import JobParser
from src.parser.formatters import format_display
from src.models.job_post import JobPost
from src.utils.validation import is_csv_data

def save_snapshot(job_post: JobPost, debug: bool = False) -> None:
    """Save job post snapshot for future testing."""
    snapshots_dir = Path("snapshots/v3")
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"linkedin_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    snapshot_data = {
        "date_parsed": job_post.date,
        "raw_text": job_post.raw_text,
        "parsed_data": {
            "company": job_post.company,
            "title": job_post.title,
            "location": job_post.location,
            "salary": job_post.salary,
            "url": job_post.url,
            "is_remote": job_post.is_remote,
            "applicants": job_post.applicants,
            "posted": job_post.posted,
            "date_applied": job_post.date_applied
        },
        "validation_errors": job_post.validation_errors
    }
    
    with open(snapshots_dir / filename, 'w') as f:
        json.dump(snapshot_data, f, indent=2)
        
    if debug:
        print(f"Snapshot saved: {filename}")

def main():
    parser = argparse.ArgumentParser(description="Parse LinkedIn job postings from clipboard")
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    parser.add_argument('--no-snapshot', action='store_true', help='Disable snapshot saving')
    args = parser.parse_args()
    
    try:
        # Get clipboard content
        content = pyperclip.paste()
        
        if args.debug:
            print("\nDebug: Clipboard content analysis:")
            print(f"Length: {len(content)} characters")
            print(f"First 100 chars: {content[:100]}...")
            print(f"Contains quotes: {content.count('"')}")
            print(f"Contains commas: {content.count(',')}")
            print(f"Number of lines: {content.count('\n') + 1}")
            
        if is_csv_data(content):
            print("\nError: Clipboard contains previously processed job data.")
            print("Please copy a new job posting from LinkedIn before running again.")
            return 1
            
        raw_text = content
        
        job_parser = JobParser()
        job_post = job_parser.parse(raw_text, debug=args.debug)
        
        # Show parsing results
        print(format_display(job_post))
        
        if job_post.validation_errors:
            print("\nWarnings:")
            for error in job_post.validation_errors:
                print(f"- {error}")
        
        # Copy to clipboard and show what was copied
        csv_data = format_csv_row(job_post)
        pyperclip.copy(csv_data)
        print("\nCopied to clipboard:")
        print(csv_data)
        print("\nJob data copied to clipboard!")
        
        # Save snapshot unless disabled
        if not args.no_snapshot:
            save_snapshot(job_post, debug=args.debug)
        
        return 0
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    main()
