from ..helpers.test_case_base import BaseParserTest
import pytest

class TestLocationParsing(BaseParserTest):
    @pytest.mark.parametrize("test_id, raw_text, expected_location, expected_remote", [
        ("city_state",
         "Software Engineer\nRaleigh, NC · 2 days ago",
         "Raleigh, NC", False),
        
        ("remote_only",
         "Software Engineer\nRemote · 100+ applicants",
         "", True),
        
        ("hybrid",
         "Software Engineer\nNew York, NY (Hybrid) · 3 days ago",
         "New York, NY", False),
        
        ("remote_with_region",
         "Software Engineer\nUnited States (Remote) · Posted 2d ago",
         "United States", True),
        
        ("international",
         "Software Engineer\nLondon, United Kingdom · 1 week ago",
         "London, United Kingdom", False),
    ])
    def test_location_formats(self, parser, test_id, raw_text, expected_location, expected_remote):
        """Test location parsing with various formats"""
        result = parser.parse(raw_text)
        assert result.location == expected_location, \
            f"Location parsing failed for {test_id}\nGot: '{result.location}'\nExpected: '{expected_location}'"
        assert result.is_remote == expected_remote, \
            f"Remote status incorrect for {test_id}\nGot: {result.is_remote}\nExpected: {expected_remote}"

    def test_location_cleaning(self):
        pass
        