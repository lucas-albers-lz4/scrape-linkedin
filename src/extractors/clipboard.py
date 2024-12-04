import pyperclip
from .base import JobExtractor
from ..models.job import JobData

class ClipboardExtractor(JobExtractor):
    def connect(self):
        """Verify clipboard access"""
        try:
            pyperclip.paste()
        except:
            raise ConnectionError("Cannot access clipboard")

    def extract(self) -> JobData:
        """Extract job data from clipboard"""
        self.connect()
        
        # Get clipboard content
        content = pyperclip.paste()
        if not content:
            raise ValueError("Clipboard is empty")

        # Initialize empty job data
        job_data = {
            'company': 'Unknown',
            'title': 'Unknown',
            'location': '',
            'salary': '',
            'is_remote': False,
            'posted': '',
            'applicants': '',
            'url': ''
        }

        # Parse clipboard content
        # Implementation depends on expected clipboard format
        # This is a basic implementation
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Basic parsing logic - can be enhanced based on requirements
            if not job_data['title'] or job_data['title'] == 'Unknown':
                job_data['title'] = line
                continue
                
            if not job_data['company'] or job_data['company'] == 'Unknown':
                job_data['company'] = line
                continue
                
            if not job_data['location'] and (',' in line or 'remote' in line.lower()):
                job_data['location'] = line
                job_data['is_remote'] = 'remote' in line.lower()
                continue

        return JobData(**job_data)

    def validate(self, data: JobData) -> bool:
        """Validate extracted data"""
        return bool(data.company and data.company != 'Unknown' and 
                   data.title and data.title != 'Unknown') 