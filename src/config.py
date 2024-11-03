"""Configuration constants for the LinkedIn job parser."""

# Minimum length for valid job posting text
MIN_TEXT_LENGTH = 100

# Remote work contradiction terms
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

# CSV field order
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
    'Salary'
]
