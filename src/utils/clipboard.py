import csv
import pyperclip
from io import StringIO
from typing import Optional
from ..models.job_post import JobPost
from ..parser.formatters import format_csv_row
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
    # Format the job post as CSV
    csv_row = format_csv_row(job_post)
    # Copy to clipboard
    pyperclip.copy(csv_row)
