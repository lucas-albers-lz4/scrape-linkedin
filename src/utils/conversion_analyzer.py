from pathlib import Path
import json
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class ConversionConfidence:
    can_convert: bool
    confidence: float  # 0.0 to 1.0
    missing_data: List[str]
    reasons: List[str]

def analyze_conversion_confidence(snapshot_file: Path) -> ConversionConfidence:
    """Analyze if a Format 1 snapshot can be converted to Format 2"""
    try:
        with open(snapshot_file) as f:
            data = json.load(f)
            
        reasons = []
        missing = []
        confidence = 1.0
        
        # Check if raw_text contains actual job content
        raw_text = data.get('raw_text', '')
        job_indicators = ['experience', 'skills', 'qualifications', 'about', 'responsibilities']
        has_job_content = any(ind in raw_text.lower() for ind in job_indicators)
        
        if not has_job_content:
            reasons.append("No job-related content found in raw_text")
            confidence *= 0.3
            
        # Check for navigation content
        nav_content = ['notifications total', 'Skip to search', 'Skip to main']
        if any(nav in raw_text for nav in nav_content):
            reasons.append("Contains navigation content")
            confidence *= 0.7
            
        parsed = data.get('parsed_data', {})
        
        # Check critical fields
        critical_fields = {
            'title': 'Job title',
            'company': 'Company name',
            'location': 'Location'
        }
        
        for field, desc in critical_fields.items():
            value = parsed.get(field, '')
            if not value:
                missing.append(field)
                reasons.append(f"Missing {desc}")
                confidence *= 0.5
            elif any(nav in value.lower() for nav in ['skip to', 'notifications']):
                reasons.append(f"Corrupted {desc}")
                confidence *= 0.4
                
        # Overall assessment
        can_convert = confidence > 0.3  # Threshold for attempted conversion
        
        return ConversionConfidence(
            can_convert=can_convert,
            confidence=confidence,
            missing_data=missing,
            reasons=reasons
        )
        
    except Exception as e:
        return ConversionConfidence(
            can_convert=False,
            confidence=0.0,
            missing_data=['all'],
            reasons=[f"Error analyzing file: {str(e)}"]
        )

def analyze_all_snapshots(snapshots_dir: str = "snapshots/v3") -> None:
    """Analyze conversion confidence for all snapshots"""
    path = Path(snapshots_dir)
    results = {
        'convertible': [],
        'risky': [],
        'not_convertible': []
    }
    
    for snapshot_file in path.glob("linkedin_snapshot_*.json"):
        confidence = analyze_conversion_confidence(snapshot_file)
        
        if confidence.confidence > 0.7:
            category = 'convertible'
        elif confidence.confidence > 0.3:
            category = 'risky'
        else:
            category = 'not_convertible'
            
        results[category].append((snapshot_file.name, confidence))
    
    # Print report
    print("\nSnapshot Conversion Analysis")
    print("=" * 50)
    
    for category, items in results.items():
        print(f"\n{category.title()} Snapshots: {len(items)}")
        if items:
            print("-" * 30)
            for filename, conf in items[:5]:  # Show first 5 of each category
                print(f"\n{filename}")
                print(f"Confidence: {conf.confidence:.2%}")
                print(f"Missing: {', '.join(conf.missing_data) if conf.missing_data else 'None'}")
                print(f"Issues:")
                for reason in conf.reasons:
                    print(f"- {reason}")
            if len(items) > 5:
                print(f"\n... and {len(items) - 5} more")

if __name__ == "__main__":
    analyze_all_snapshots() 