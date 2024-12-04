from pathlib import Path
import json
from typing import Dict, Any

class SnapshotHelper:
    def __init__(self, snapshots_dir: str = "snapshots/v3"):
        self.snapshots_dir = Path(snapshots_dir)
        if not self.snapshots_dir.exists():
            raise FileNotFoundError(f"Snapshots directory not found: {snapshots_dir}")

    def load_snapshot(self, snapshot_id: str) -> Dict[str, Any]:
        """Load a specific snapshot by ID (YYYYMMDD_HHMMSS)"""
        snapshot_file = self.snapshots_dir / f"linkedin_snapshot_{snapshot_id}.json"
        if not snapshot_file.exists():
            raise FileNotFoundError(f"Snapshot not found: {snapshot_id}")
            
        with open(snapshot_file) as f:
            return json.load(f)

    def get_raw_text(self, snapshot_id: str) -> str:
        """Get raw text from snapshot"""
        return self.load_snapshot(snapshot_id)["raw_text"]

    def get_expected_data(self, snapshot_id: str) -> Dict[str, Any]:
        """Get expected parsed data from snapshot"""
        return self.load_snapshot(snapshot_id)["parsed_data"]
        
    def print_debug_info(self, snapshot_id: str, parsed_result, expected_data):
        """Print debug information for failed tests"""
        raw_text = self.get_raw_text(snapshot_id)
        print(f"\nDebug info for snapshot: {snapshot_id}")
        print(f"First 200 characters:\n{raw_text[:200]}")
        
        for field in ["company", "title", "location"]:
            if getattr(parsed_result, field) != expected_data[field]:
                print(f"\n{field.title()} mismatch:")
                print(f"Expected: '{expected_data[field]}'")
                print(f"Got: '{getattr(parsed_result, field)}'")
                
                # Show relevant lines from raw text
                print("\nRelevant lines:")
                for line in raw_text.splitlines():
                    if expected_data[field] in line:
                        print(f"-> {line}")