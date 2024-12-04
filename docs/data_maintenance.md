# Data Maintenance Procedures

## Snapshot Data Cleanup
Process for cleaning and verifying LinkedIn job posting snapshots.

### Company Name Cleanup Process
1. **Initial Analysis**
   - Run verification test to identify issues
   - Check for header content contamination
   - Identify "Unknown" cases
   - Preserve original raw data

2. **Cleanup Steps**
   ```bash
   # Run company data verification
   pytest -s src/tests/test_parser.py::TestSnapshotMaintenance::test_verify_company_data_quality -v
   ```

3. **Current Status**
   - 49 total snapshots
   - 46 valid companies
   - 3 legitimate "Unknown" cases
   - 9 unique companies verified

4. **Verified Companies**
   - CSI
   - Curi
   - Geotab
   - HR Acuity
   - HireKeyz Inc
   - Latitude.sh
   - Phaxis
   - RemoteWorker CA
   - Whatnot

### Best Practices
- Always preserve `raw_text` in snapshots
- Only modify `parsed_data` section
- Validate data after modifications
- Keep track of legitimate "Unknown" cases 