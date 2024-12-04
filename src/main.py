from argparse import ArgumentParser
from src.extractors import ClipboardExtractor, BrowserExtractor
from src.diagnostics.chrome import ChromeDiagnostics

def main():
    parser = ArgumentParser()
    parser.add_argument('--mode', choices=['clipboard', 'browser'], default='clipboard')
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--diagnose', action='store_true')
    args = parser.parse_args()
    
    if args.diagnose:
        diagnostics = ChromeDiagnostics()
        diagnostics.run_all_diagnostics()
        return
    
    extractor = BrowserExtractor() if args.mode == 'browser' else ClipboardExtractor()
    job_data = extractor.extract()
    
    if job_data:
        print("Job data extracted successfully")
        print(job_data)

if __name__ == "__main__":
    main()
