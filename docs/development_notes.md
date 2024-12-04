# Development Notes

## Recent Refactors
1. **Snapshot Data Structure**
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

2. **Test Framework Improvements**
   - Added `TestSnapshotMaintenance` class
   - Implemented data quality verification
   - Added assertions for data integrity
   - Preserved original data during cleanup

## Next Steps

### Immediate Tasks
1. **Field Verification**
   - [ ] Job Title parsing
   - [ ] Location parsing
   - [ ] Salary information
   - [ ] Remote status
   - [ ] Application count

2. **Test Data**
   - [ ] Create baseline test cases using verified companies
   - [ ] Document expected parsing behavior
   - [ ] Add edge cases to test suite

3. **Parser Improvements**
   - [ ] Review "Unknown" case handling
   - [ ] Add validation for parsed fields
   - [ ] Improve error reporting

### Future Enhancements
1. **Automated Maintenance**
   - Regular snapshot verification
   - Automated cleanup procedures
   - Data quality reports

2. **Parser Robustness**
   - Handle more company name formats
   - Improve field extraction accuracy
   - Better error handling

## Development Process
1. **For Each Field:**
   ```python
   # 1. Analyze current data
   test_verify_field_data_quality()
   
   # 2. Clean problematic data
   test_fix_field_data()
   
   # 3. Verify cleanup
   test_verify_field_data_quality()
   
   # 4. Add to test suite
   test_field_baseline()
   ```

2. **When Adding Features:**
   - Add test cases first
   - Preserve raw data
   - Document changes
   - Update verification tests 