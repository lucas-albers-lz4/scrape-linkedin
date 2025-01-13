# LinkedIn Job Parser

A tool for parsing LinkedIn job postings and formatting them for tracking applications.

## Prerequisites

- Python 3.8+
- Google Chrome
- ChromeDriver matching your Chrome version
- LinkedIn account (for browser-based extraction)

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy environment template and configure:
```bash
cp .env.example .env
# Edit .env with your settings
```

## Usage

### Clipboard Mode
1. Copy a LinkedIn job posting (Ctrl+A, Ctrl+C)
2. Run the parser:
```bash
python -m src.main --mode clipboard
```

### Browser Mode
1. Start Chrome in debug mode:
```bash
./chrome.debug.sh
```

2. Run the parser:
```bash
python -m src.main --mode browser
```

### Optional Flags
- `--debug`: Show detailed parsing information
- `--no-snapshot`: Skip creating snapshot files
- `--diagnose`: Run Chrome connection diagnostics

## Features

- Extracts key information:
  - Company name
  - Job title
  - Location (with remote status)
  - Salary range
  - Application dates
  - Posting details (applicants, post date)
- Validates US locations and remote work status
- Formats data for spreadsheet tracking
- Prevents accidental reprocessing
- Creates snapshots for testing
- Tracks manual additions (URL, notes, application status)

## Data Format

Automatically Populated:
- Company (parsed from posting)
- Title (parsed from posting)
- Location (parsed with remote status)
- Date (current date)
- Source (always "LinkedIn")
- DateApplied (current date)
- Salary (when available in posting)

Conditionally Populated (if available):
- Applicants (e.g., "100+", "31")
- Posted (e.g., "2 weeks ago")

Manual Entry Required:
- URL (not available from clipboard)
- InitialResponse
- Reject
- Screen
- FirstRound
- SecondRound
- Notes

## Configuration

The application can be configured through environment variables or `.env` file:

- `CHROME_PROFILE`: Chrome profile to use (default: "Profile 1")
- `CHROME_DEBUG_PORT`: Debug port for Chrome (default: "9222")
- `CHROME_USER_DATA_DIR`: Chrome user data directory
- `SNAPSHOTS_DIR`: Directory for saving job snapshots
- `DEBUG_MODE`: Enable debug logging

## Development

### Running Tests
```bash
# Run all tests
pytest

# Test specific modules
python3 -m src.tests.test_clipboard
python3 -m src.tests.test_validation
```

### Code Style
```bash
flake8 src tests
black src tests
```

## Known Limitations

1. **Automated Field Parsing**
   - Company name and title parsing requires specific LinkedIn format
   - Location parsing is US-centric
   - Salary parsing limited to standard US formats
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
   - URL field is not automatically populated
   - Limited to standard US salary formats

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT License - See LICENSE file for details

