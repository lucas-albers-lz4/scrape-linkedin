import json
from pathlib import Path
from typing import Dict, List, Set
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class FormatInfo:
    format_type: str
    files: List[str]
    fields: Set[str]
    sample_structure: Dict

def detect_formats(snapshots_dir: str = "snapshots/v3") -> Dict[str, FormatInfo]:
    """Analyze all snapshots to detect different formats"""
    formats = defaultdict(lambda: FormatInfo(
        format_type="unknown",
        files=[],
        fields=set(),
        sample_structure={}
    ))
    
    path = Path(snapshots_dir)
    
    for snapshot_file in path.glob("linkedin_snapshot_*.json"):
        try:
            with open(snapshot_file) as f:
                data = json.load(f)
                
            # Create format signature based on keys and data types
            format_sig = _create_format_signature(data)
            
            # Update format info
            format_info = formats[format_sig]
            format_info.files.append(snapshot_file.name)
            format_info.fields.update(data.keys())
            
            # Store first occurrence as sample
            if not format_info.sample_structure:
                format_info.sample_structure = _simplify_structure(data)
                format_info.format_type = _detect_format_type(data)
                
        except Exception as e:
            print(f"Error processing {snapshot_file.name}: {str(e)}")
            
    return formats

def _create_format_signature(data: Dict) -> str:
    """Create a signature string representing the data format"""
    def get_type_sig(value):
        if isinstance(value, dict):
            return f"dict({','.join(sorted(value.keys()))})"
        return type(value).__name__
    
    fields = sorted(f"{k}:{get_type_sig(v)}" for k, v in data.items())
    return "|".join(fields)

def _simplify_structure(data: Dict, max_depth: int = 3) -> Dict:
    """Create a simplified version of the data structure"""
    if max_depth <= 0:
        return "..."
        
    if isinstance(data, dict):
        return {k: _simplify_structure(v, max_depth - 1) for k, v in data.items()}
    if isinstance(data, (list, set)):
        return [_simplify_structure(next(iter(data)), max_depth - 1)] if data else []
    if isinstance(data, str):
        return f"{data[:50]}..." if len(data) > 50 else data
    return data

def _detect_format_type(data: Dict) -> str:
    """Detect the type of format based on content"""
    if "html" in data:
        return "raw_html"
    if "raw_text" in data and "parsed_data" in data:
        return "parsed_text"
    if "data" in data and isinstance(data["data"], dict):
        return "api_response"
    return "unknown"

def print_format_report(formats: Dict[str, FormatInfo]) -> None:
    """Print a detailed report of detected formats"""
    print("\nSnapshot Format Analysis")
    print("=" * 50)
    
    for i, (sig, info) in enumerate(formats.items(), 1):
        print(f"\nFormat {i}: {info.format_type}")
        print(f"Files: {len(info.files)}")
        print(f"Fields: {', '.join(sorted(info.fields))}")
        print("\nSample Structure:")
        print(json.dumps(info.sample_structure, indent=2))
        print("\nAffected Files:")
        for file in info.files[:5]:  # Show first 5 files
            print(f"- {file}")
        if len(info.files) > 5:
            print(f"... and {len(info.files) - 5} more")
        print("-" * 50)

if __name__ == "__main__":
    formats = detect_formats()
    print_format_report(formats) 