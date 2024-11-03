import csv
import pyperclip
from io import StringIO
from typing import Optional
from ..models.job_post import JobPost
from .validation import is_csv_data

def get_clipboard_content() -> str:
    """
    Get and validate clipboard content.
    Raises ValueError if content appears to be already processed data.
    """
    content = pyperclip.paste()
    if not content:
        raise ValueError("Clipboard is empty")
        
    if is_csv_data(content):
        raise ValueError("Clipboard contains already processed job data")
        
    return content

def set_clipboard_content(job_post: JobPost) -> None:
    """Format job post as CSV and copy to clipboard."""
    # Create a string buffer to write CSV to
    output = StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_ALL)  # Quote all fields for consistency
    
    # Write single row using JobPost's to_csv method
    writer.writerow(job_post.to_csv())
    
    # Get the string value and remove trailing newline
    formatted = output.getvalue().rstrip()
    pyperclip.copy(formatted)

def format_csv_row(job_post: JobPost) -> str:
    """Format job post as CSV string for display purposes."""
    output = StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_ALL)
    writer.writerow(job_post.to_csv())
    return output.getvalue().rstrip()
