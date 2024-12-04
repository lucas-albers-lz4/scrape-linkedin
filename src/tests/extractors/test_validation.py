from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from src.extractors.browser import BrowserExtractor
from src.models.job import JobData
import pytest

class TestDataValidation:
    @pytest.fixture
    def mock_driver(self):
        """Create a mock driver for testing"""
        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        yield driver
        driver.quit()

    @pytest.fixture
    def sample_job_data(self):
        """Sample job data for testing"""
        return JobData(
            company="Test Company",
            title="Software Engineer",
            location="New York, NY",
            salary="$100k-$150k",
            is_remote=True,
            applicants="100+",
            posted="2 days ago",
            url="https://linkedin.com/jobs/test"
        )

    def test_validate_method(self, mock_driver, sample_job_data):
        """Test data validation method"""
        extractor = BrowserExtractor(driver=mock_driver)
        assert extractor.validate(sample_job_data) == True
        
        # Test invalid data
        invalid_data = JobData(
            company="",
            title="",
            location="",
            url="",
            salary="",
            is_remote=False,
            posted="",
            applicants=""
        )
        assert extractor.validate(invalid_data) == False