"""Generate test cases from snapshots with known good parsed data."""
from pathlib import Path
import json
from jinja2 import Template

def generate_baseline_tests():
    """Generate test cases from snapshots with known good parsed data."""
    snapshots_dir = Path("snapshots/v3")
    test_cases = []
    
    for snapshot_file in snapshots_dir.glob("linkedin_snapshot_*.json"):
        with open(snapshot_file) as f:
            snapshot = json.load(f)
            test_cases.append({
                'name': snapshot_file.stem,
                'raw_text': snapshot['raw_text'],
                'expected': snapshot['parsed_data']
            })
    
    # Template for test file
    template = """
import pytest
from src.parser.job_parser import JobParser

class TestBaselineParsing:
    @pytest.fixture
    def parser(self):
        return JobParser()

    {% for test in test_cases %}
    def test_{{ test.name }}(self, parser):
        \"\"\"Test parsing from snapshot {{ test.name }}\"\"\"
        raw_text = \"\"\"{{ test.raw_text }}\"\"\"
        expected = {{ test.expected }}

        result = parser.parse(raw_text)

        # Verify required fields
        assert result.company == expected["company"]
        assert result.title == expected["title"]
        assert result.location == expected["location"]
        assert result.is_remote == expected["is_remote"]
        assert result.posted == expected["posted"]
        
        # Verify salary only if expected
        if expected["salary"]:
            assert result.salary == expected["salary"], "Salary should match when present"
        else:
            assert result.salary == "", "Salary should be empty when not present"
    {% endfor %}
"""
    
    # Render template with test cases
    rendered = Template(template).render(test_cases=test_cases)
    
    # Write test file
    with open('src/tests/test_baseline_parsing.py', 'w') as f:
        f.write(rendered)

if __name__ == "__main__":
    generate_baseline_tests() 