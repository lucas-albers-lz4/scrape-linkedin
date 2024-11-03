import pytest
from pathlib import Path
import json
from datetime import datetime

from ..parser.job_parser import JobParser
from ..models.job_post import JobPost

@pytest.fixture
def parser():
    return JobParser()

@pytest.fixture
def sample_job_text():
    return """
    Senior Software Engineer
    Acme Corp · Full-time
    San Francisco, CA (Remote)
    
    $150,000 - $200,000 a year
    
    About the job
    We're looking for a Senior Software Engineer...
    """

def test_basic_parsing(parser, sample_job_text):
    job_post = parser.parse(sample_job_text)
    assert job_post.company == "Acme Corp"
    assert job_post.title == "Senior Software Engineer"
    assert job_post.location == "San Francisco, CA (Remote)"
    assert job_post.is_remote == True
    assert job_post.salary == "$150,000 - $200,000 a year"
    assert not job_post.validation_errors

def test_validation_errors():
    job_post = JobPost(
        company="",
        title="Test",
        location="Unknown",
        salary="",
        raw_text="Too short"
    )
    assert len(job_post.validation_errors) > 0
    assert not job_post.is_valid()

def load_snapshot_tests():
    """Load all v3 snapshots for testing."""
    snapshot_dir = Path("snapshots/v3")
    test_cases = []
    
    if not snapshot_dir.exists():
        return test_cases
        
    for snapshot_file in snapshot_dir.glob("*.json"):
        with open(snapshot_file) as f:
            data = json.load(f)
            test_cases.append({
                'raw_text': data['raw_text'],
                'expected': data['parsed_data']
            })
            
    return test_cases

@pytest.mark.parametrize("test_case", load_snapshot_tests())
def test_snapshot(parser, test_case):
    job_post = parser.parse(test_case['raw_text'])
    expected = test_case['expected']
    
    assert job_post.company == expected['company']
    assert job_post.title == expected['title']
    assert job_post.location == expected['location']
    assert job_post.salary == expected['salary']
    assert job_post.is_remote == expected['is_remote']

def test_veeva_job_parsing(parser):
    """Test parsing a Veeva Systems job posting."""
    sample_text = """
    Senior Engineering Manager - Cloud Infrastructure
    Veeva Systems · Full-time
    Pleasanton, CA · 7 hours ago · 4 applicants
    $130K/yr - $300K/yr
    
    About the job
    Veeva Systems is a mission-driven organization...
    """
    
    job_post = parser.parse(sample_text)
    
    assert job_post.company == "Veeva Systems"
    assert job_post.title == "Senior Engineering Manager - Cloud Infrastructure"
    assert job_post.location == "Pleasanton, CA"
    assert job_post.salary == "$130K/yr - $300K/yr"

def test_generic_remote_job(parser):
    """Test parsing a generic remote job posting."""
    sample_text = """
    Staff Software Engineer
    TechCorp · Full-time
    United States (Remote) · 2 days ago
    $180,000 - $250,000 a year
    """
    
    job_post = parser.parse(sample_text)
    
    assert job_post.company == "TechCorp"
    assert job_post.title == "Staff Software Engineer"
    assert job_post.location == "United States (Remote)"
    assert job_post.salary == "$180,000 - $250,000 a year"
