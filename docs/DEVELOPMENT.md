# Development Guide

This document outlines the development process, data structures, maintenance procedures, and future plans for the project.

## Snapshot Data Structure

Job posting snapshots are stored in JSON format with the following structure:

```json
{
  "raw_text": "original clipboard content",
  "parsed_data": {
    "company": "Company Name",
    "title": "Job Title",
    // other fields...
  },
  "timestamp": "YYYYMMDD_HHMMSS"
}
```
- `raw_text`: Contains the original, unmodified content extracted from the source (e.g., clipboard).
- `parsed_data`: Holds the structured data extracted from `raw_text`.
- `timestamp`: Indicates when the snapshot was created.

## Development Process

Follow these steps when developing new features or refining data parsing:

1.  **Analyze Existing Data:** Use verification tests to assess the current state of the target data field.
    ```python
    # Example for a 'field'
    test_verify_field_data_quality()
    ```
2.  **Implement Parsing/Cleanup Logic:** Write or modify the code responsible for parsing or cleaning the data. Add specific tests for any problematic cases identified.
    ```python
    # Example fix function/test
    test_fix_field_data()
    ```
3.  **Verify Changes:** Rerun the verification tests to ensure the changes have improved data quality and haven't introduced regressions.
    ```python
    test_verify_field_data_quality()
    ```
4.  **Update Baseline Tests:** Add new test cases using verified data examples to cover the implemented logic and ensure future stability.
    ```python
    test_field_baseline()
    ```
5.  **Document:** Update documentation, including `KNOWN_LIMITATIONS.md` if necessary.

### Testing Strategy

-   **Data Quality Verification:** Tests (`TestSnapshotMaintenance`) are used to identify issues like header contamination, "Unknown" cases, and general data integrity across all snapshots.
-   **Baseline Tests:** Specific tests should exist for each verified company/data point to ensure consistent parsing behavior.
-   **Test-Driven Development (TDD):** Add test cases *before* implementing new parsing logic or fixing bugs.

## Data Maintenance

Maintaining the quality and integrity of snapshot data is crucial.

### Best Practices
-   Always preserve the original `raw_text` in snapshots.
-   Only modify the `parsed_data` section during cleanup.
-   Validate data using verification tests after any modifications.
-   Keep track of legitimate "Unknown" or ambiguous cases.

### Cleanup Example: Company Names

This process was followed to clean up company names:

1.  **Initial Analysis:**
    ```bash
    # Run company data verification
    pytest -s src/tests/test_parser.py::TestSnapshotMaintenance::test_verify_company_data_quality -v
    ```
    This identified issues and legitimate "Unknown" cases.

2.  **Cleanup:** Manual or scripted updates were applied to the `parsed_data.company` field in affected snapshot files.

3.  **Verification:** The verification test was rerun to confirm the fixes.

4.  **Status (at time of cleanup):**
    -   49 total snapshots
    -   46 valid companies extracted
    -   3 legitimate "Unknown" cases identified
    -   9 unique companies verified

### Verified Companies (Examples)
The following companies had their parsing verified during the initial cleanup:
-   CSI
-   Curi
-   Geotab
-   HR Acuity
-   HireKeyz Inc
-   Latitude.sh
-   Phaxis
-   RemoteWorker CA
-   Whatnot

## Recent Refactors

-   Standardized snapshot data structure (see above).
-   Improved test framework with `TestSnapshotMaintenance` for data quality checks.
-   Enhanced assertions for data integrity during tests.

## Roadmap

### Immediate Tasks
-   **Field Verification & Parsing:**
    -   [ ] Job Title
    -   [ ] Location
    -   [ ] Salary information
    -   [ ] Remote status
    -   [ ] Application count
-   **Test Data:**
    -   [ ] Create baseline test cases using verified companies for all fields.
    -   [ ] Document expected parsing behavior for edge cases.
    -   [ ] Add more diverse edge cases to the test suite.
-   **Parser Improvements:**
    -   [ ] Systematically review and document handling of "Unknown" cases for all fields.
    -   [ ] Add validation logic within the parser for essential fields.
    -   [ ] Improve error reporting during parsing failures.

### Future Enhancements
-   **Automated Maintenance:**
    -   Scheduled job for regular snapshot verification.
    -   Explore possibilities for automated cleanup suggestions or actions.
    -   Generate data quality reports.
-   **Parser Robustness:**
    -   Handle a wider variety of company name formats and job posting layouts.
    -   Improve field extraction accuracy using more sophisticated techniques if needed.
    -   Implement more robust error handling and recovery mechanisms. 