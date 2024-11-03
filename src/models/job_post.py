from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

@dataclass
class JobPost:
    """
    Represents a parsed LinkedIn job posting with fields matching the tracking spreadsheet.
    """
    company: str
    title: str
    location: str
    url: str = ""
    date: str = field(default_factory=lambda: datetime.now().strftime("%m/%d/%Y"))
    source: str = "LinkedIn"
    date_applied: str = field(default_factory=lambda: datetime.now().strftime("%m/%d/%Y"))
    initial_response: str = ""
    reject: str = ""
    screen: str = ""
    first_round: str = ""
    second_round: str = ""
    notes: str = ""
    salary: str = ""
    posted: str = ""  # When the job was originally posted (e.g., "2 weeks ago", "10/15/2024")
    applicants: str = ""
    is_remote: bool = False
    raw_text: str = ""
    validation_errors: List[str] = field(default_factory=list)

    def to_csv(self) -> List[str]:
        """Convert job post to CSV fields in the exact spreadsheet order."""
        return [
            self.company,
            self.title,
            self.location,
            self.url,
            self.date,
            self.source,
            self.date_applied,
            self.initial_response,
            self.reject,
            self.screen,
            self.first_round,
            self.second_round,
            self.notes,
            self.salary,
            self.posted,
            self.applicants
        ]

    def is_valid(self) -> bool:
        """Check if the job post has all required fields and no validation errors."""
        required_fields = ['company', 'title', 'location']
        has_required = all(getattr(self, field) for field in required_fields)
        return has_required and not self.validation_errors

    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"{self.company} - {self.title} ({self.location})"
