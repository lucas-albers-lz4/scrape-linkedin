# LinkedIn Job Parser

A tool for parsing LinkedIn job postings and formatting them for tracking applications.

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

## Usage

1. Copy a LinkedIn job posting (Ctrl+A, Ctrl+C)
2. Run the parser:
```bash
python -m src.main
```

Optional flags:
- `--debug`: Show detailed parsing information
- `--no-snapshot`: Skip creating snapshot files

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

Note: The parser focuses on extracting information directly available in the job posting. 
Application tracking fields must be manually maintained as you progress through the 
application process.

## Development

### Running Tests
```bash
# Test clipboard handling
python3 -m src.tests.test_clipboard

# Test data validation
python3 -m src.tests.test_validation
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
   - URL field is not automatically populated (requires manual entry)
   - URL is not available in clipboard data from LinkedIn
   - Limited to standard US salary formats

