#!/bin/bash

# Create main project directory structure
mkdir -p src/{parser,models,utils,tests/snapshots}

# Create Python files with __init__.py files
touch src/__init__.py
touch src/main.py
touch src/config.py

# Parser module
touch src/parser/__init__.py
touch src/parser/job_parser.py
touch src/parser/formatters.py

# Models module
touch src/models/__init__.py
touch src/models/job_post.py

# Utils module
touch src/utils/__init__.py
touch src/utils/clipboard.py
touch src/utils/validation.py

# Tests
touch src/tests/__init__.py
touch src/tests/test_parser.py

# Make the script executable
chmod +x setup_project.sh

# Create a basic .gitignore
echo "# Python
__pycache__/
*.py[cod]
*$py.class
.pytest_cache/
.coverage
htmlcov/
.env
venv/
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Project specific
snapshots/" > .gitignore

# Create a basic README.md
echo "# LinkedIn Job Parser

A tool for parsing LinkedIn job postings and formatting them for tracking applications.

## Setup

1. Create a virtual environment:
\`\`\`bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
\`\`\`

2. Install dependencies:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

## Usage

1. Copy a LinkedIn job posting (Ctrl+A, Ctrl+C)
2. Run the parser:
\`\`\`bash
python -m src.main
\`\`\`
" > README.md

# Create requirements.txt
echo "pyperclip
pytest
python-dateutil" > requirements.txt

echo "Directory structure created successfully!"
