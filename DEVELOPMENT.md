# Development Notes

## Known Limitations

1. **LinkedIn Format Dependencies**
   - Parser assumes specific LinkedIn job posting format
   - May break if LinkedIn changes their layout
   - Currently only handles English language postings

2. **Salary Parsing**
   - Limited to standard US salary formats
   - May not handle equity or bonus information
   - Doesn't parse hourly rates

3. **Location Detection**
   - US-centric location validation
   - May miss some valid US locations
   - Remote work detection could be improved

## Planned Features

1. **Enhanced Parsing**
   - [ ] Parse benefits information
   - [ ] Handle multiple currency formats
   - [ ] Better detection of contract vs full-time
   - [ ] Parse required skills/technologies

2. **Data Management**
   - [ ] Local database for tracking applications
   - [ ] Export to different spreadsheet formats
   - [ ] Backup/restore functionality

3. **Validation Improvements**
   - [ ] More robust remote work validation
   - [ ] Better hybrid work detection
   - [ ] Improved salary range validation

## Technical Debt

1. **Testing**
   - Need more comprehensive test cases
   - Add integration tests
   - Add test coverage reporting

2. **Code Structure**
   - Consider splitting parser into smaller components
   - Add type hints throughout codebase
   - Add logging instead of print statements

3. **Documentation**
   - Add function-level documentation
   - Create API documentation
   - Add more code examples

## Contributing

When contributing to this project, please:
1. Create a feature branch
2. Add tests for new functionality
3. Update documentation
4. Follow existing code style
