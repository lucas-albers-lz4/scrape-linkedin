from typing import List
from ..models.job_post import JobPost

def format_csv_row(job_post: JobPost) -> str:
    """Format job post as CSV row."""
    return ','.join(f'"{field}"' for field in job_post.to_csv())

def format_display(job_post: JobPost) -> str:
    """Format job post details for display."""
    return f"Job Details:\n" \
           f"Company: {job_post.company}\n" \
           f"Title: {job_post.title}\n" \
           f"Location: {job_post.location}\n" \
           f"Salary: {job_post.salary}\n" \
           f"Remote: {'Yes' if job_post.is_remote else 'No'}"
