# LinkedIn Job Parser

A tool for parsing LinkedIn job postings and formatting them for tracking applications.

## Prerequisites

- Python 3.8+
- Google Chrome
- ChromeDriver matching your Chrome version installed and accessible in your PATH.
- LinkedIn account (for browser-based extraction)

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd scrape-linkedin
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure environment variables:**
    Copy the example file:
    ```bash
    cp .env.example .env
    ```
    Then, edit the `.env` file with your specific settings (like Chrome user data directory if not default). See the [Configuration](#configuration) section for details.

## Usage

This tool can operate in two modes:

### Clipboard Mode

Parses job posting text copied directly from LinkedIn.

1.  Navigate to a LinkedIn job posting in your browser.
2.  Select all text (Ctrl+A or Cmd+A).
3.  Copy the selected text (Ctrl+C or Cmd+C).
4.  Run the parser:
    ```bash
    python -m src.main --mode clipboard
    ```
    The parsed data will be formatted and copied back to your clipboard, ready to paste into a spreadsheet or tracking system. Snapshots of the raw and parsed data are saved by default.

### Browser Mode

Directly extracts job posting data from an active LinkedIn tab using Chrome's debug mode.

1.  **Start Chrome in debug mode:**
    Ensure Chrome is fully closed, then run the appropriate script for your OS (you might need to adjust the Chrome path):
    *   **macOS:** `./chrome-debug.sh`
    *   **Linux:** `./chrome-debug.sh` (adjust path if necessary)
    *   **Windows:** `chrome-debug.bat` (adjust path if necessary)
    This opens a new Chrome instance connected to the debug port.

2.  **Navigate to a job posting:** In the debug-mode Chrome window, go to the LinkedIn job posting you want to parse.

3.  **Run the parser:**
    ```bash
    python3 browser_extract.py 
    ```
    The tool will connect to the debug-mode Chrome instance, extract the data from the active tab, parse it, and copy the formatted results to your clipboard. Snapshots are also saved by default. Then paste into your google sheet or whatever, and whala you have all the data from your most recent application.

### Optional Flags

-   `--debug`: Enable detailed logging output for parsing steps.
-   `--no-snapshot`: Prevent the creation of snapshot files in the snapshots directory.
-   `--diagnose` (Browser Mode): Run diagnostics to check the connection to the Chrome debug instance.

## Features

-   Extracts key job details:
    -   Company Name
    -   Job Title
    -   Location (identifies remote status, primarily for US locations)
    -   Salary Range (when available in standard formats)
    -   Job Posting Date (e.g., "2 weeks ago")
    -   Applicant Count (e.g., "31 applicants")
-   Automatically populates fields commonly used for application tracking:
    -   `Company`
    -   `Title`
    -   `Location`
    -   `Date` (current date of parsing)
    -   `Source` (defaults to "LinkedIn")
    -   `DateApplied` (current date of parsing)
    -   `Salary` (if found)
    -   `Applicants` (if found)
    -   `Posted` (if found)
-   Leaves placeholders for manual entry fields:
    -   `URL` (cannot be reliably extracted from clipboard/browser DOM in all cases)
    -   `InitialResponse`
    -   `Reject`
    -   `Screen`
    -   `FirstRound`, `SecondRound`, etc.
    -   `Notes`
-   Validates extracted data (e.g., US location format).
-   Formats output data (tab-separated) for easy pasting into spreadsheets.
-   Creates timestamped JSON snapshots of raw and parsed data for testing and reprocessing (`/snapshots` directory).
-   Includes logic to prevent accidental reprocessing of identical clipboard content within a short timeframe.

## Configuration

Configure the application via a `.env` file in the project root or environment variables:

-   `CHROME_USER_DATA_DIR`: Path to your Chrome user data directory. Required for Browser Mode to connect to the correct instance.
    *   *Example macOS*: `/Users/your_user/Library/Application Support/Google/Chrome`
    *   *Example Windows*: `C:\Users\your_user\AppData\Local\Google\Chrome\User Data`
-   `CHROME_PROFILE`: Chrome profile directory name (default: "Default", common alternatives: "Profile 1", "Profile 2"). Check your `CHROME_USER_DATA_DIR` to see profile directory names.
-   `CHROME_DEBUG_PORT`: Port for Chrome debugging connection (default: "9222"). Ensure this matches the port in the `chrome-debug` script.
-   `SNAPSHOTS_DIR`: Directory to save job data snapshots (default: "snapshots").
-   `DEBUG_MODE`: Set to `True` to enable debug logging (equivalent to `--debug` flag).

## Development

### Running Tests

Ensure you have the development dependencies installed (`pip install -r requirements-dev.txt` if applicable, or ensure `pytest` is installed).

```bash
pytest
```
This command will discover and run all tests in the `src/tests` directory.

### Code Style

We use `black` for formatting and `flake8` for linting.

```bash
black src src/tests
flake8 src src/tests
```

### Development Documentation

For details on the data structure, development process, and maintenance, see the [Development Guide](./docs/DEVELOPMENT_GUIDE.md).

## Known Limitations

This tool relies on the structure of LinkedIn job postings, which can change. Current known limitations include:

-   Parsing accuracy depends on the specific format and consistency of LinkedIn's HTML/text structure. Changes by LinkedIn may break parsing for certain fields.
-   Location parsing and remote status detection are primarily designed for US-based postings.
-   Salary parsing may not capture all possible formats.

For a detailed list of current limitations and potential areas for improvement, please see [Known Limitations](./docs/KNOWN_LIMITATIONS.md).

## Contributing

Contributions are welcome! Please follow these steps:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix (`git checkout -b feature/your-feature-name`).
3.  Make your changes and add tests as appropriate.
4.  Ensure all tests pass (`pytest`).
5.  Format and lint your code (`black src src/tests`, `flake8 src src/tests`).
6.  Commit your changes (`git commit -m 'Add some feature'`).
7.  Push to your branch (`git push origin feature/your-feature-name`).
8.  Create a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

