"""Configuration settings for LinkedIn Job Parser."""

import os
from pathlib import Path
from typing import Dict, Any

# Chrome Configuration
CHROME_PROFILE = os.getenv('CHROME_PROFILE', 'Profile 1')
CHROME_DEBUG_PORT = os.getenv('CHROME_DEBUG_PORT', '9222')
CHROME_USER_DATA_DIR = os.getenv('CHROME_USER_DATA_DIR', 
    str(Path.home() / "Library/Application Support/Google/Chrome"))

# Application Paths
SNAPSHOTS_DIR = os.getenv('SNAPSHOTS_DIR', 'snapshots/v3')
TEST_DATA_DIR = os.getenv('TEST_DATA_DIR', 'src/tests/test_data')

# Debug Settings
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
SAVE_SNAPSHOTS = os.getenv('SAVE_SNAPSHOTS', 'True').lower() == 'true'

# LinkedIn Parsing Configuration
MIN_TEXT_LENGTH = 100  # Minimum length for valid job posting text
MAX_TITLE_LENGTH = 150  # Maximum length for job titles

# Field Validation
REMOTE_CONTRADICTIONS = [
    'hybrid',
    'on-site',
    'onsite',
    'in office',
    'in-office',
    'must be located',
    'must reside',
    'must live'
]

# CSV Export Configuration
CSV_FIELDS = [
    'Company',
    'Title',
    'Location',
    'URL',
    'Date',
    'Source',
    'DateApplied',
    'InitialResponse',
    'Reject',
    'Screen',
    'FirstRound',
    'SecondRound',
    'Notes',
    'Salary',
    'Posted',
    'Applicants'
]

def get_chrome_options() -> Dict[str, Any]:
    """Get Chrome configuration options."""
    return {
        'profile': CHROME_PROFILE,
        'debug_port': CHROME_DEBUG_PORT,
        'user_data_dir': CHROME_USER_DATA_DIR
    }

def get_paths() -> Dict[str, Path]:
    """Get application paths."""
    return {
        'snapshots': Path(SNAPSHOTS_DIR),
        'test_data': Path(TEST_DATA_DIR)
    }
