import pytest
from ..utils.validation import validate_job_post, validate_salary_format
from ..models.job_post import JobPost

def test_location_validation():
    print("\nTesting Location Validation:")
    
    # Valid US locations
    test_job = JobPost(
        company="Test Co",
        title="Test Job",
        location="New York, NY (Remote)",
        salary="100K-200K"
    )
    errors = validate_job_post(test_job)
    assert not any("United States" in err for err in errors)
    print("✓ Accepted valid US location")
    
    # Invalid locations
    test_job = JobPost(
        company="Test Co",
        title="Test Job",
        location="Toronto, Canada",
        salary="100K-200K"
    )
    errors = validate_job_post(test_job)
    assert any("United States" in err for err in errors)
    print("✓ Caught non-US location")

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

def test_remote_validation():
    print("\nTesting Remote Validation:")
    
    # Test hybrid warning
    test_job = JobPost(
        company="Test Co",
        title="Test Job",
        location="New York, NY (Remote)",
        raw_text="This is a hybrid position requiring some office time"
    )
    errors = validate_job_post(test_job)
    assert any("hybrid" in err.lower() for err in errors)
    print("✓ Detected hybrid in remote job")
    
    # Test onsite warning
    test_job = JobPost(
        company="Test Co",
        title="Test Job",
        location="New York, NY (Remote)",
        raw_text="This position requires onsite work"
    )
    errors = validate_job_post(test_job)
    assert any("on-site" in err.lower() for err in errors)
    print("✓ Detected on-site requirement in remote job")

if __name__ == "__main__":
    print("Running Validation Tests...")
    test_location_validation()
    test_salary_validation()
    test_remote_validation()
    print("\nAll validation tests passed! ✓") 