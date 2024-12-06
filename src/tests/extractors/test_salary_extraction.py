import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from src.extractors.browser import BrowserExtractor
from unittest.mock import Mock, patch

class TestSalaryExtraction:
    @pytest.fixture
    def mock_driver(self):
        driver = Mock()
        driver.find_elements.return_value = []
        return driver
        
    @pytest.fixture
    def extractor(self, mock_driver):
        extractor = BrowserExtractor(mock_driver)
        return extractor

    def test_normalize_salary_full_numbers(self, extractor):
        """Test salary normalization with full numbers"""
        test_cases = [
            ("$126,000/yr - $207,000/yr", "$126,000 - $207,000"),
            ("$126,000 - $180,000", "$126,000 - $180,000"),
            ("$126,500", "$126,500"),
            ("126000/yr", "$126,000"),
        ]
        
        for input_text, expected in test_cases:
            result = extractor._normalize_salary(input_text)
            assert result == expected, f"Failed to normalize {input_text}"

    def test_extract_salary_from_elements(self, extractor, mock_driver):
        """Test salary extraction from page elements"""
        def create_mock_element(text):
            element = Mock(spec=WebElement)
            element.text = text
            return element

        test_cases = [
            ([create_mock_element("Base salary\n$126,000/yr - $207,000/yr")], "$126,000 - $207,000"),
            ([], ""),
        ]

        for elements, expected in test_cases:
            mock_driver.find_elements.return_value = elements
            result = extractor._extract_salary_all_locations()
            assert result == expected, f"Failed to extract from elements: {elements}"

    @pytest.mark.parametrize("html_content,expected", [
        ("""
        <div>
            <div>Base salary</div>
            <div>$126,000/yr - $207,000/yr</div>
        </div>
        """, "$126,000 - $207,000"),
    ])
    def test_integrated_salary_extraction(self, extractor, mock_driver, html_content, expected):
        """Test integrated salary extraction with different HTML structures"""
        def create_mock_element(text):
            element = Mock(spec=WebElement)
            element.text = text
            return element

        mock_driver.page_source = html_content
        mock_driver.find_elements.return_value = [
            create_mock_element(line.strip()) 
            for line in html_content.split('\n') 
            if '$' in line
        ]
        
        result = extractor._extract_salary_all_locations()
        assert result == expected, f"Failed to extract salary from HTML: {html_content}"