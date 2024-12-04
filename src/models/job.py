from dataclasses import dataclass
from typing import Optional

@dataclass
class JobData:
    """Data class for storing job information"""
    company: str
    title: str
    location: str
    url: str
    salary: Optional[str] = ''
    is_remote: Optional[bool] = False
    posted: Optional[str] = ''
    applicants: Optional[str] = '' 