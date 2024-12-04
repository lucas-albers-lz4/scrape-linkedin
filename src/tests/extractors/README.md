# Browser Extractor Tests

## Overview
This directory contains tests for the LinkedIn job data extraction functionality, split into logical components for better organization and maintenance.

## Test Structure
- `conftest.py`: Shared fixtures for browser testing
- `test_browser_initialization.py`: Tests for browser setup and initialization
- `test_extraction.py`: Tests for HTML content extraction
- `test_validation.py`: Tests for job data validation

## Key Fixtures
- `mock_driver`: Provides a headless Chrome instance for testing
- `sample_job_data`: Provides sample LinkedIn job data

## Test Coverage
1. Browser Initialization ✅
   - Basic initialization
   - Login state detection
   - Driver configuration

2. Data Extraction ❌
   - HTML parsing (failing)
   - Field extraction (failing)
   - Error handling (failing)

3. Data Validation ⚠️
   - Required fields (passing)
   - Data format validation (failing)
   - Edge cases (failing)

## Test Status
- Total Tests: 69
- Passing: 37
- Failing: 32

## Known Issues
1. Location parsing failures
2. Title extraction inconsistencies
3. Metadata parsing issues (salary, posted date, applicants)
4. Snapshot test failures
5. Integration test failures

## Removed Tests
1. Connection failure test - Due to timeout issues
2. URL validation test - Moved to integration tests
3. Response handling test - Consolidated into extraction tests
4. Original test_extractors.py - Refactored into separate test files

## Running Tests