import json
from pathlib import Path
import pytest

def validate_snapshots():
    """Validate snapshot data quality and identify potentially corrupt snapshots"""
    snapshots_dir = Path("snapshots/v3")
    if not snapshots_dir.exists():
        print("Error: Snapshots directory not found")
        return []
    
    issues = []
    snapshot_count = 0
    
    print(f"\nChecking snapshots in: {snapshots_dir}")
    print("-" * 50)
    
    for snapshot_file in snapshots_dir.glob("linkedin_snapshot_*.json"):
        snapshot_count += 1
        print(f"\nAnalyzing: {snapshot_file.name}")
        
        try:
            with open(snapshot_file) as f:
                data = json.load(f)
                
                # Check for navigation content in raw_text
                nav_indicators = [
                    "notifications total",
                    "Skip to search",
                    "Skip to main content",
                    "Keyboard shortcuts",
                    "My Network",
                    "Messaging"
                ]
                
                if "raw_text" in data:
                    if any(ind in data["raw_text"] for ind in nav_indicators):
                        issue = f"Contains navigation content"
                        issues.append(f"{snapshot_file.name}: {issue}")
                        print(f"  ❌ {issue}")
                        
                # Check for expected fields
                expected_fields = ["company", "title", "location", "raw_text", "parsed_data"]
                missing_fields = [field for field in expected_fields if field not in data]
                if missing_fields:
                    issue = f"Missing fields: {missing_fields}"
                    issues.append(f"{snapshot_file.name}: {issue}")
                    print(f"  ❌ {issue}")
                    
                # Check for empty or invalid values
                if data.get("raw_text", "").strip() == "":
                    issue = "Empty raw_text"
                    issues.append(f"{snapshot_file.name}: {issue}")
                    print(f"  ❌ {issue}")
                    
                if "parsed_data" in data:
                    parsed = data["parsed_data"]
                    if not parsed.get("title") or parsed.get("title") == "Unknown":
                        issue = "Missing or invalid title"
                        issues.append(f"{snapshot_file.name}: {issue}")
                        print(f"  ❌ {issue}")
                    if not parsed.get("location"):
                        issue = "Missing location"
                        issues.append(f"{snapshot_file.name}: {issue}")
                        print(f"  ❌ {issue}")
                
                if not issues:
                    print("  ✅ Snapshot looks valid")
                    
        except json.JSONDecodeError:
            issue = "Invalid JSON format"
            issues.append(f"{snapshot_file.name}: {issue}")
            print(f"  ❌ {issue}")
            
    print("\n" + "=" * 50)
    print(f"Snapshot Analysis Summary:")
    print(f"Total snapshots checked: {snapshot_count}")
    print(f"Issues found: {len(issues)}")
    
    if issues:
        print("\nDetailed Issues:")
        for issue in issues:
            print(f"- {issue}")
            
    return issues

def test_clean_snapshots():
    """Test that we're using only clean snapshots in our test suite"""
    issues = validate_snapshots()
    assert not issues, f"Found {len(issues)} issues with snapshots"

if __name__ == "__main__":
    validate_snapshots()