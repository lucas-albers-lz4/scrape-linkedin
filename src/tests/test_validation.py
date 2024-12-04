import pytest
from ..utils.validation import validate_job_post, validate_salary_format
from ..models.job_post import JobPost

def test_salary_validation():
    print("\nTesting Salary Validation:")
    
    # Test valid formats
    valid_formats = [
        "$130,000 - $300,000",
        "130K-300K",
        "130000-300000"
    ]
    for salary in valid_formats:
        assert validate_salary_format(salary)
        print(f"✓ Accepted valid salary format: {salary}")
    
    # Test invalid formats
    invalid_formats = [
        "Invalid",
        "100K",
        "100K+"
    ]
    for salary in invalid_formats:
        assert not validate_salary_format(salary)
        print(f"✓ Rejected invalid salary format: {salary}")

if __name__ == "__main__":
    print("Running Validation Tests...")
    test_salary_validation()
    print("\nAll validation tests passed! ✓") 