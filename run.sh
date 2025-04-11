#!/bin/bash

# LinkedIn Job Parser Runner
# This script provides a convenient way to run the LinkedIn job parser

# Check if Chrome is running with debug port
if ! lsof -i :9222 &>/dev/null; then
    echo "Starting Chrome in debug mode..."
    ./chrome.debug.sh
    sleep 2
fi

# Run the job parser
python3 linkedin_job_parser.py "$@" 