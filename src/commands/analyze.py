"""Command handler for analyzing snapshots."""
from ..analyzer.snapshot_analyzer import SnapshotAnalyzer

def handle_analyze(args):
    """Handle the analyze command."""
    analyzer = SnapshotAnalyzer()
    
    if args.check_integrity:
        integrity = analyzer.analyze_snapshot_integrity()
        print("\nSnapshot Integrity Report:")
        print(f"Total snapshots: {integrity['total_snapshots']}")
        print(f"Valid structure: {integrity['valid_structure']}")
        
        if integrity['invalid_structure']:
            print("\nInvalid structure files:")
            for file in integrity['invalid_structure']:
                print(f"  - {file}")
        
        print("\nField Validation:")
        for field, stats in integrity['field_validation'].items():
            valid_pct = (stats['valid'] / integrity['total_snapshots'] * 100)
            print(f"  {field}: {valid_pct:.1f}% valid")
            if stats['invalid']:
                print("    Invalid in files:")
                for file in stats['invalid'][:3]:  # Show first 3
                    print(f"    - {file}")
        return

    if args.check_corruption:
        corruption = analyzer.check_snapshot_corruption()
        print("\nSnapshot Corruption Report:")
        print(f"Total snapshots: {corruption['total_snapshots']}")
        print(f"Corrupted files: {len(corruption['corrupted_files'])}")
        
        if corruption['corrupted_files']:
            print("\nCorruption details:")
            for category, files in corruption['corruption_types'].items():
                if files:
                    print(f"\n{category}:")
                    for file in files:
                        print(f"  - {file}")

    results, summary = analyzer.analyze_all()
    
    print("\nSnapshot Analysis Summary:")
    print(f"Total snapshots: {summary['total_snapshots']}")
    print(f"Valid JSON: {summary['valid_json']}")
    print(f"Has raw text: {summary['has_raw_text']}")
    print(f"Has parsed data: {summary['has_parsed_data']}")
    print(f"Corrupted files: {summary['corrupted']}")
    
    if args.detailed:
        print("\nField coverage:")
        for field, coverage in sorted(summary['field_coverage'].items()):
            print(f"  {field}: {coverage:.1f}%")
        
        print("\nParsing Success by Field:")
        total = summary['total_snapshots']
        print(f"  Company detection: {summary['valid_json']/total*100:.1f}%")
        print(f"  Title detection: {summary['has_parsed_data']/total*100:.1f}%")
        
        if args.move_corrupted and summary['corrupted'] > 0:
            moved = analyzer.move_corrupted_snapshots()
            print(f"\nMoved {moved} corrupted snapshots to 'corrupted' directory")
