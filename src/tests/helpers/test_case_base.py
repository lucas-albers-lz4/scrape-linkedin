import pytest
from .snapshot_helper import SnapshotHelper
from src.parser.job_parser import JobParser

class BaseParserTest:
    @pytest.fixture
    def parser(self):
        return JobParser()
    
    @pytest.fixture
    def helper(self):
        return SnapshotHelper()
    
    def assert_parsing(self, result, expected, snapshot_id):
        """Assert parsing results with detailed error messages"""
        fields = ["company", "title", "location", "is_remote", "posted"]
        
        for field in fields:
            assert getattr(result, field) == expected[field], \
                f"{field.title()} mismatch in {snapshot_id}\n" \
                f"Expected: '{expected[field]}'\n" \
                f"Got: '{getattr(result, field)}'"
        
        # Special handling for salary
        if expected["salary"]:
            assert result.salary == expected["salary"], \
                f"Salary mismatch in {snapshot_id}\n" \
                f"Expected: '{expected['salary']}'\n" \
                f"Got: '{result.salary}'"
