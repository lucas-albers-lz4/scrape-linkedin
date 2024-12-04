"""Command handler for parsing job postings."""
from ..utils.clipboard import get_clipboard_content, set_clipboard_content
from ..parser.job_parser import JobParser
from ..parser.formatters import format_display, format_csv_row

def handle_parse(args):
    """Handle the parse command."""
    # Get clipboard content
    raw_text = get_clipboard_content()
    
    if args.debug:
        print("\nDebug: Clipboard content analysis:")
        print(f"Length: {len(raw_text)} characters")
        print(f"First 100 chars: {raw_text[:100]}")
        quote_count = raw_text.count("'")
        print(f"Contains quotes: {quote_count}")
        print(f"Contains commas: {raw_text.count(',')}")
        print(f"Number of lines: {raw_text.count(chr(10)) + 1}")
    
    # Parse the job posting
    parser = JobParser()
    job_post = parser.parse(raw_text, debug=args.debug)
    
    # Display results
    print("\nJob Details:")
    print(format_display(job_post))
    
    # Set clipboard content with JobPost object
    set_clipboard_content(job_post)
    
    # Format and display CSV
    csv_row = format_csv_row(job_post)
    print("\nCopied to clipboard:")
    print(csv_row)
    
    # Save snapshot if enabled
    if not args.no_snapshot:
        job_post.save_snapshot()
        print("\nSnapshot saved!")
    