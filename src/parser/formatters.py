from typing import List
from ..models.job_post import JobPost

def format_csv_row(job_post: JobPost) -> str:
    """Format job post as CSV row."""
    return ','.join(f'"{field}"' for field in job_post.to_csv())

def format_display(job_post: JobPost) -> str:
    """Format job post details for display."""
    return f"""
Job Details:
Company: {job_post.company}
Title: {job_post.title}
Location: {job_post.location}
Salary: {job_post.salary}
Remote: {'Yes' if job_post.is_remote else 'No'}
"""
