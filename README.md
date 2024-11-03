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

## Data Format

Outputs CSV data with the following fields:
- Company
- Title
- Location
- URL
- Date
- Source
- DateApplied
- InitialResponse
- Reject
- Screen
- FirstRound
- SecondRound
- Notes
- Salary
- Posted
- Applicants

## Development

### Running Tests
```bash
# Test clipboard handling
python3 -m src.tests.test_clipboard

# Test data validation
python3 -m src.tests.test_validation
```

