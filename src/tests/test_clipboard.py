import pytest
from ..utils.validation import is_csv_data

def test_csv_detection():
    # Test cases
    test_cases = [
        # Should detect as CSV (True cases)
        (
            '"Veeva Systems","Senior Engineering Manager - Cloud Infrastructure","Pleasanton, CA (Remote)","","11/03/2024","LinkedIn","11/03/2024","","","","","","Easy Apply","$130,000 - $300,000","7","4"',
            True,
            "Should detect our CSV format"
        ),
        
        # Should not detect as CSV (False cases)
        (
            "Senior Engineering Manager - Cloud Infrastructure\nVeeva Systems · Full-time\nPleasanton, CA · 7 hours ago",
            False,
            "Should not detect LinkedIn job posting as CSV"
        ),
        (
            "",
            False,
            "Should not detect empty string as CSV"
        ),
        (
            "Company,Title,Location",
            False,
            "Should not detect simple comma-separated text as CSV"
        ),
        (
            "Just some random text with, commas, in it",
            False,
            "Should not detect text with commas as CSV"
        )
    ]
    
    # Run tests
    for content, expected, message in test_cases:
        result = is_csv_data(content)
        assert result == expected, f"Failed: {message}\nContent: {content[:50]}..."
        print(f"✓ {message}")

if __name__ == "__main__":
    test_csv_detection()
