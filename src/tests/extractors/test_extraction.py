from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from src.extractors.browser import BrowserExtractor
from src.models.job import JobData
import pytest
from unittest.mock import patch
from src.constants.selectors import JOB_TITLE_SELECTORS
from src.utils.extraction_utils import extract_text_with_selectors

class TestExtraction:
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

    def test_extract_title(self, mock_driver):
        # Setup your test page content if needed
        title = extract_text_with_selectors(mock_driver, JOB_TITLE_SELECTORS, debug=True)
        # Assert that title extraction meets expectations
        assert title != "", "Title should not be empty."