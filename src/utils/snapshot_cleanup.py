import json
from pathlib import Path
from typing import Dict, Optional
import re

class SnapshotCleaner:
    def __init__(self, snapshots_dir: str = "snapshots/v3"):
        self.snapshots_dir = Path(snapshots_dir)
        
    def clean_raw_text(self, raw_text: str) -> str:
        """Remove navigation and irrelevant content from raw text"""
        # Split into lines and filter out navigation
        lines = raw_text.split('\n')
        cleaned_lines = []
        
        skip_patterns = [
            r'notifications?\s+total',
            r'Skip to',
            r'Keyboard shortcuts',
            r'My Network',
            r'Messaging',
            r'Home$',
            r'Jobs$',
            r'^Search',
            r'new feed updates'
        ]
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if any(re.search(pattern, line, re.I) for pattern in skip_patterns):
                continue
            cleaned_lines.append(line)
            
        return '\n'.join(cleaned_lines)
    
    def extract_job_data(self, raw_text: str) -> Dict[str, str]:
        """Extract structured job data from cleaned text"""
        cleaned_text = self.clean_raw_text(raw_text)
        
        # Basic extraction patterns
        patterns = {
            'title': r'^([^•\n]+?)(?:\s+at|\s+•|\s+in|\s+\(|$)',
            'company': r'(?:at\s+)?([^•\n]+?)\s+(?:•|$)',
            'location': r'(?:•\s*)?([^•\n]+?,\s*(?:[A-Z]{2}|[A-Za-z]+))\s*(?:•|$)',
        }
        
        data = {}
        for field, pattern in patterns.items():
            match = re.search(pattern, cleaned_text)
            if match:
                data[field] = match.group(1).strip()
        
        return data
    
    def cleanup_snapshot(self, snapshot_file: Path) -> Optional[Dict]:
        """Clean up a single snapshot file"""
        try:
            with open(snapshot_file) as f:
                data = json.load(f)
            
            if 'raw_text' not in data:
                print(f"Missing raw_text in {snapshot_file.name}")
                return None
                
            # Extract clean data
            job_data = self.extract_job_data(data['raw_text'])
            
            # Create cleaned snapshot
            cleaned = {
                'raw_text': self.clean_raw_text(data['raw_text']),
                'parsed_data': job_data
            }
            
            return cleaned
            
        except Exception as e:
            print(f"Error processing {snapshot_file.name}: {str(e)}")
            return None
    
    def cleanup_all(self, dry_run: bool = True) -> None:
        """Clean up all snapshots in directory"""
        for snapshot_file in self.snapshots_dir.glob("linkedin_snapshot_*.json"):
            print(f"\nProcessing: {snapshot_file.name}")
            
            cleaned = self.cleanup_snapshot(snapshot_file)
            if not cleaned:
                continue
                
            if dry_run:
                print("Would write cleaned data:")
                print(json.dumps(cleaned, indent=2))
            else:
                backup_file = snapshot_file.with_suffix('.json.bak')
                snapshot_file.rename(backup_file)
                
                with open(snapshot_file, 'w') as f:
                    json.dump(cleaned, f, indent=2)
                print(f"Cleaned and saved: {snapshot_file.name}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true', help='Actually apply changes (default is dry-run)')
    args = parser.parse_args()
    
    cleaner = SnapshotCleaner()
    cleaner.cleanup_all(dry_run=not args.apply)
