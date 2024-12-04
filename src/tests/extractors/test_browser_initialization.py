import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from ...extractors.browser import BrowserExtractor

class TestBrowserInitialization:
    @pytest.fixture
    def mock_driver(self):
        """Create a mock driver for testing"""
        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        yield driver
        driver.quit()

    def test_initialization(self, mock_driver):
        """Test basic browser initialization"""
        extractor = BrowserExtractor(driver=mock_driver)
        assert extractor.driver is not None
        assert not extractor.logged_in 