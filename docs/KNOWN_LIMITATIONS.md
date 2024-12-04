# Known Limitations

## Browser Extraction
Currently, the browser extraction functionality (`test_browser_extraction.py`) has some known limitations:

### Data Capture Issues
1. **Location Information**
   - The location data is not consistently captured
   - This may be due to variations in LinkedIn's DOM structure for location elements

2. **Posted Date**
   - Job posting dates are not reliably extracted
   - This might be affected by LinkedIn's dynamic date formatting

### Future Improvements
These issues are tracked and may be addressed in future updates. Possible solutions could include:
- Implementing alternative selector strategies
- Adding fallback extraction methods
- Handling multiple possible DOM structures for these elements

### Workaround
For now, users should validate location and posting date information manually if these fields are critical for their use case. 