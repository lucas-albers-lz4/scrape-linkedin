# Development Notes

## Known Limitations

1. **Automated Field Parsing**
   - Company name and title parsing requires specific LinkedIn format
   - Location parsing is US-centric
   - Salary parsing limited to standard US formats and main job section
   - Remote status detection needs improvement
   - Applicants count may miss some formats
   - Posted date parsing varies by format

2. **Manual Entry Fields**
   - URL (not available in clipboard data)
   - Application status tracking (InitialResponse, Screen, etc.)
   - Notes and custom annotations
   - Interview rounds (First, Second)
   - Rejection tracking

3. **Data Validation**
   - Limited to standard US salary formats
   - May not handle equity or bonus information
   - Doesn't parse hourly rates
   - Missing structured benefits data (401k, insurance, etc.)
   - Needs more robust salary format validation
   - US-centric location validation
   - May miss some valid US locations
   - Remote work detection could be improved
   - Hybrid/flexible work options not standardized
   - Remote work contradiction checks need enhancement

4. **Input Processing**
   - No handling of non-English job postings
   - Clipboard data may be incomplete
   - No handling of malformed HTML content
   - No support for direct LinkedIn API integration
   - Limited error handling for clipboard access
   - No support for batch processing
   - Missing input sanitization
   - No handling of special characters
   - Limited support for different LinkedIn page layouts
   - No support for mobile clipboard formats

## Planned Features

1. **Enhanced Parsing**
   - [ ] Parse benefits information
     - Vision insurance
     - Disability insurance
     - 401k details
     - Other listed benefits
   - [ ] Handle multiple currency formats
   - [ ] Better detection of contract vs full-time
   - [ ] Parse required skills/technologies
     - Required skills
     - Matched skills
     - Missing skills
   - [ ] Company details extraction
     - Company size
     - Industry
     - Employee count
   - [ ] Move regex patterns to config file
   - [ ] Add try/except blocks for regex operations

2. **Data Management**
   - [ ] Local database for tracking applications
   - [ ] Export to different spreadsheet formats
   - [ ] Backup/restore functionality
   - [ ] Standardize field formats
     - Applicants (e.g., "Over 100" vs "100")
     - Posted dates
     - Remote status indicators
   - [ ] Make snapshot directory path configurable
   - [ ] Add configuration file for hard-coded values

3. **Validation Improvements**
   - [ ] More robust remote work validation
   - [ ] Better hybrid work detection
   - [ ] Improved salary range validation
   - [ ] Education requirements parsing
   - [ ] Centralize validation logic
   - [ ] Add input length validation

## Technical Debt

1. **Testing**
   - Need more comprehensive test cases
   - Add integration tests
   - Add test coverage reporting
   - Add tests for malformed input
   - Expand snapshot-based tests
   - Add edge case coverage

2. **Code Structure**
   - Consider splitting parser into smaller components
   - Add type hints throughout codebase
   - Add logging instead of print statements
   - Refactor long methods (especially parse())
   - Make debug output options configurable

3. **Documentation**
   - Add function-level documentation
   - Create API documentation
   - Add more code examples
   - Improve inline comments for complex regex
   - Complete missing type hints
   - Add detailed docstrings for all methods

## Contributing

When contributing to this project, please:
1. Create a feature branch
2. Add tests for new functionality
3. Update documentation
4. Follow existing code style

## Recent Fixes

1. **LinkedIn Preference Messages (2024-01-11)**
   - Fixed issue where job titles included LinkedIn preference messages
   - Added `_clean_linkedin_text` method to JobParser to remove metadata
   - Affects title and other text fields that may contain preference matches
   - Example: "DevOps Manager" instead of "DevOps ManagerMatches your job preferences..."

2. **Salary Parsing Scope (2024-01-11)**
   - Fixed issue where salary was incorrectly extracted from "More jobs" section
   - Modified salary detection to only look at main job posting content
   - Salary field will now be empty if not found in main posting
   - Prevents false matches from recommended job listings
   - Example: No salary shown instead of incorrect salary from similar jobs

## Recent Improvements

### 1. Test Suite Enhancement (2024-01-15)
#### Company Name Parsing
- Added parameterized tests using real LinkedIn formats
- Verified against actual snapshot data
- Improved test readability and maintenance
- Removed artificial test cases
- Added comprehensive documentation for regex patterns

#### Test Coverage
- Added tests for all known company formats:
  - Standard company names
  - Companies with Inc/Corp
  - Companies with special characters
  - Companies with locations
  - Header content handling
  - Unknown company cases

## Next Steps

### 1. Location Parsing Tests
- Parameterize location parsing tests
- Add tests for:
  - US state variations
  - Remote status detection
  - Hybrid work locations
  - Invalid locations
  - International locations (error cases)

### 2. Salary Parsing Tests
- Parameterize salary format tests
- Add tests for:
  - Range formats ($XXk-$YYk)
  - Single value formats
  - Invalid formats
  - Currency variations

### 3. Posted Date Tests
- Parameterize date format tests
- Test variations:
  - Hours ago
  - Days ago
  - Weeks ago
  - Months ago

### 4. Documentation
- Document all regex patterns
- Add examples for each pattern
- Document known limitations
- Add troubleshooting guide
