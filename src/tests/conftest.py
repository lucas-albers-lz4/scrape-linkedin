import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from ..extractors.browser import BrowserExtractor
from ..extractors.base import JobData

@pytest.fixture
def mock_browser():
    """Mock browser for testing without actual Chrome instance"""
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()

@pytest.fixture
def sample_job_data():
    """Sample job data for testing"""
    return JobData(
        company="Test Company",
        title="Software Engineer",
        location="New York, NY",
        salary="$100k-$150k",
        is_remote=True,
        applicants="100+",
        posted="2 days ago",
        url="https://linkedin.com/jobs/test",
        raw_data="Sample raw data"
    ) 