import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Set, Dict

def backup_snapshots(snapshots_dir: str = "snapshots/v3") -> Path:
    """Create a backup of all snapshots before deletion"""
    source_path = Path(snapshots_dir)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = source_path.parent / f"backup_{timestamp}"
    
    shutil.copytree(source_path, backup_path)
    print(f"Created backup at: {backup_path}")
    return backup_path

def get_clean_snapshots() -> Set[str]:
    """Return set of known clean snapshot filenames"""
    return {
        'linkedin_snapshot_20241106_132718.json',
        'linkedin_snapshot_20241116_112810.json',
        'linkedin_snapshot_20241118_144214.json',
        'linkedin_snapshot_20241106_132813.json'
    }

def delete_imperfect_snapshots(snapshots_dir: str = "snapshots/v3", dry_run: bool = True) -> None:
    """Delete all snapshots except the perfect ones"""
    path = Path(snapshots_dir)
    clean_snapshots = get_clean_snapshots()
    
    # Count snapshots
    all_snapshots = list(path.glob("linkedin_snapshot_*.json"))
    to_delete = [f for f in all_snapshots if f.name not in clean_snapshots]
    
    print(f"\nFound {len(all_snapshots)} total snapshots")
    print(f"Clean snapshots: {len(clean_snapshots)}")
    print(f"Snapshots to delete: {len(to_delete)}")
    
    if dry_run:
        print("\nDRY RUN - No files will be deleted")
        print("\nWould delete:")
        for file in to_delete[:5]:
            print(f"- {file.name}")
        if len(to_delete) > 5:
            print(f"... and {len(to_delete) - 5} more")
    else:
        print("\nDeleting imperfect snapshots...")
        for file in to_delete:
            file.unlink()
            print(f"Deleted: {file.name}")
            
        print(f"\nDeletion complete. Kept {len(clean_snapshots)} clean snapshots.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true', 
                      help='Actually delete files (default is dry-run)')
    args = parser.parse_args()
    
    # Always create backup first
    backup_path = backup_snapshots()
    
    # Delete imperfect snapshots
    delete_imperfect_snapshots(dry_run=not args.apply)
    
    if not args.apply:
        print("\nTo actually delete files, run:")
        print("python src/utils/cleanup_snapshots.py --apply") 