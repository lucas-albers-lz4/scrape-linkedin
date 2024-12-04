import json
from pathlib import Path
import sys

def analyze_snapshot(snapshot_file):
    """Analyze a single snapshot file and print relevant details"""
    print(f"\n{'='*80}")
    print(f"Analyzing: {snapshot_file.name}")
    print(f"{'='*80}")
    
    with open(snapshot_file, 'r') as f:
        snapshot = json.load(f)
        
        # Print Raw Text Analysis
        raw_text = snapshot['raw_text']
        print("\nRAW TEXT ANALYSIS:")
        print(f"Length: {len(raw_text)} characters")
        print("First 200 chars:")
        print("-" * 40)
        print(raw_text[:200])
        print("-" * 40)
        
        # Print Expected Parsing
        print("\nEXPECTED PARSING:")
        print(json.dumps(snapshot['parsed_data'], indent=2))
        
        # Look for key markers
        print("\nKEY MARKERS:")
        markers = {
            "Company Logo": "logo",
            "Share Options": "Share options",
            "Job Title": "title",
            "Location": "location",
            "Remote Indicator": "remote",
            "Notifications": "notifications total"
        }
        
        for name, marker in markers.items():
            if marker in raw_text:
                context = raw_text[raw_text.find(marker)-30:raw_text.find(marker)+30]
                print(f"\n{name} context:")
                print(f"...{context}...")
        
        # Add detailed content analysis
        print("\nCONTENT ANALYSIS:")
        lines = raw_text.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if any(key in line for key in ['Curi', 'Director', 'Raleigh', 'logo', 'Share']):
                context_start = max(0, i-2)
                context_end = min(len(lines), i+3)
                print(f"\nLines {context_start}-{context_end}:")
                for j in range(context_start, context_end):
                    prefix = ">" if j == i else " "
                    print(f"{prefix} {j:3d}: {lines[j]}")

def main():
    # Get snapshots directory
    snapshots_dir = Path("snapshots/v3")
    if not snapshots_dir.exists():
        print(f"Error: Snapshots directory not found at {snapshots_dir}")
        sys.exit(1)
    
    # Analyze each snapshot
    snapshots = list(snapshots_dir.glob("linkedin_snapshot_*.json"))
    print(f"Found {len(snapshots)} snapshots")
    
    # Analyze first failing snapshot or specific one if provided
    if len(sys.argv) > 1:
        target = sys.argv[1]
        snapshots = [s for s in snapshots if target in s.name]
        if not snapshots:
            print(f"No snapshots found matching: {target}")
            sys.exit(1)
    
    for snapshot in snapshots[:1]:  # Start with just one
        analyze_snapshot(snapshot)

if __name__ == "__main__":
    main() 