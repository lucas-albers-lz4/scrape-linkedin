from abc import ABC, abstractmethod
from typing import Dict, Optional
from dataclasses import dataclass
from ..models.job import JobData

@dataclass
class JobData:
    """Standardized job data structure"""
    company: str
    title: str
    location: str
    salary: Optional[str] = None
    is_remote: bool = False
    applicants: Optional[str] = None
    posted: Optional[str] = None
    url: Optional[str] = None
    raw_data: Optional[str] = None

class JobExtractor(ABC):
    """Base class for job data extractors"""
    
    @abstractmethod
    def connect(self):
        """Ensure connection to data source is active"""
        pass
        
    @abstractmethod
    def extract(self) -> JobData:
        """Extract job data from source"""
        pass
    
    @abstractmethod
    def validate(self, data: JobData) -> bool:
        """Validate extracted data"""
        pass
    
    def save_snapshot(self, data: JobData) -> str:
        """Save data snapshot"""
        # Common snapshot saving logic
        pass 