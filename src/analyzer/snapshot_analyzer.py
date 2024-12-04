"""Analyzer for job posting snapshots."""
from pathlib import Path
from typing import Dict, List, Tuple
import json
from datetime import datetime
import shutil

class SnapshotAnalyzer:
    def __init__(self, snapshots_dir: str = "snapshots/v3"):
        self.snapshots_dir = Path(snapshots_dir)
        self.results: List[Dict] = []
        
    def analyze_all(self) -> Tuple[List[Dict], Dict]:
        """Analyze all snapshots and return results with summary."""
        if not self.snapshots_dir.exists():
            print(f"Error: Snapshots directory not found: {self.snapshots_dir}")
            return [], self._empty_summary()
            
        snapshot_files = list(self.snapshots_dir.glob('*.json'))
        
        # Analyze each snapshot
        for file_path in snapshot_files:
            result = self._analyze_snapshot(file_path)
            self.results.append(result)
        
        return self.results, self._generate_summary()
    
    def _analyze_snapshot(self, file_path: Path) -> Dict:
        """Analyze a single snapshot file."""
        result = {
            'file': file_path.name,
            'valid_json': False,
            'has_raw_text': False,
            'has_parsed_data': False,
            'parsed_fields_present': [],
            'parsed_fields_missing': [],
            'file_size': file_path.stat().st_size,
            'date_created': datetime.fromtimestamp(file_path.stat().st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
            'error': None
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                result['valid_json'] = True
                
                # Check for required fields
                if 'raw_text' in data:
                    result['has_raw_text'] = bool(data['raw_text'])
                
                if 'parsed_data' in data:
                    result['has_parsed_data'] = True
                    parsed_data = data['parsed_data']
                    
                    # Check each expected field
                    expected_fields = [
                        'company', 'title', 'location', 'salary',
                        'url', 'is_remote', 'applicants', 'posted',
                        'date_applied'
                    ]
                    
                    for field in expected_fields:
                        if field in parsed_data and parsed_data[field]:
                            result['parsed_fields_present'].append(field)
                        else:
                            result['parsed_fields_missing'].append(field)
                
        except json.JSONDecodeError as e:
            result['error'] = f"Invalid JSON: {str(e)}"
        except Exception as e:
            result['error'] = f"Error: {str(e)}"
            
        return result
    
    def _generate_summary(self) -> Dict:
        """Generate summary statistics from results."""
        if not self.results:
            return self._empty_summary()
            
        return {
            'total_snapshots': len(self.results),
            'valid_json': sum(1 for r in self.results if r['valid_json']),
            'has_raw_text': sum(1 for r in self.results if r['has_raw_text']),
            'has_parsed_data': sum(1 for r in self.results if r['has_parsed_data']),
            'corrupted': sum(1 for r in self.results if r['error']),
            'field_coverage': self._calculate_field_coverage()
        }
    
    def _empty_summary(self) -> Dict:
        """Return empty summary structure."""
        return {
            'total_snapshots': 0,
            'valid_json': 0,
            'has_raw_text': 0,
            'has_parsed_data': 0,
            'corrupted': 0,
            'field_coverage': {}
        }
    
    def _calculate_field_coverage(self) -> Dict[str, float]:
        """Calculate the percentage of snapshots that have each field."""
        if not self.results:
            return {}
            
        field_counts = {}
        for result in self.results:
            for field in result['parsed_fields_present']:
                field_counts[field] = field_counts.get(field, 0) + 1
                
        total = len(self.results)
        return {field: (count / total) * 100 for field, count in field_counts.items()}
    
    def move_corrupted_snapshots(self) -> int:
        """Move corrupted snapshots to a separate directory."""
        corrupted_dir = self.snapshots_dir / 'corrupted'
        corrupted_dir.mkdir(exist_ok=True)
        
        moved = 0
        for result in self.results:
            if result['error']:
                src = self.snapshots_dir / result['file']
                dst = corrupted_dir / result['file']
                shutil.move(src, dst)
                moved += 1
        
        return moved 
    
    def analyze_snapshot_integrity(self) -> Dict:
        """Analyze integrity of all snapshots."""
        integrity_report = {
            'total_snapshots': 0,
            'valid_structure': 0,
            'invalid_structure': [],
            'empty_raw_text': [],
            'empty_parsed_data': [],
            'field_validation': {
                'company': {'valid': 0, 'invalid': []},
                'title': {'valid': 0, 'invalid': []},
                'location': {'valid': 0, 'invalid': []},
                'salary': {'valid': 0, 'invalid': []},
                'is_remote': {'valid': 0, 'invalid': []},
                'applicants': {'valid': 0, 'invalid': []},
                'posted': {'valid': 0, 'invalid': []},
                'url': {'valid': 0, 'invalid': []}
            }
        }
        
        for file_path in self.snapshots_dir.glob('*.json'):
            integrity_report['total_snapshots'] += 1
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Check basic structure
                    if 'raw_text' not in data or 'parsed_data' not in data:
                        integrity_report['invalid_structure'].append(file_path.name)
                        continue
                    
                    integrity_report['valid_structure'] += 1
                    
                    # Check raw text
                    if not data['raw_text'].strip():
                        integrity_report['empty_raw_text'].append(file_path.name)
                    
                    # Check parsed data fields
                    parsed = data['parsed_data']
                    for field in integrity_report['field_validation'].keys():
                        if field in parsed and parsed[field]:
                            integrity_report['field_validation'][field]['valid'] += 1
                        else:
                            integrity_report['field_validation'][field]['invalid'].append(file_path.name)
                            
            except Exception as e:
                integrity_report['invalid_structure'].append(f"{file_path.name} (Error: {str(e)})")
        
        return integrity_report
    
    def check_snapshot_corruption(self) -> Dict:
        """Check for corrupted snapshot files."""
        corruption_report = {
            'total_snapshots': 0,
            'corrupted_files': [],
            'corruption_types': {
                'invalid_json': [],
                'missing_raw_text': [],
                'missing_parsed_data': [],
                'empty_raw_text': [],
                'empty_parsed_data': []
            }
        }
        
        for file_path in self.snapshots_dir.glob('*.json'):
            corruption_report['total_snapshots'] += 1
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        corruption_report['corruption_types']['invalid_json'].append(file_path.name)
                        corruption_report['corrupted_files'].append(file_path.name)
                        continue
                    
                    # Check for missing required sections
                    if 'raw_text' not in data:
                        corruption_report['corruption_types']['missing_raw_text'].append(file_path.name)
                        corruption_report['corrupted_files'].append(file_path.name)
                    elif not data['raw_text'].strip():
                        corruption_report['corruption_types']['empty_raw_text'].append(file_path.name)
                        corruption_report['corrupted_files'].append(file_path.name)
                    
                    if 'parsed_data' not in data:
                        corruption_report['corruption_types']['missing_parsed_data'].append(file_path.name)
                        corruption_report['corrupted_files'].append(file_path.name)
                    elif not any(data['parsed_data'].values()):
                        corruption_report['corruption_types']['empty_parsed_data'].append(file_path.name)
                        corruption_report['corrupted_files'].append(file_path.name)
                        
            except Exception as e:
                corruption_report['corrupted_files'].append(f"{file_path.name} (Error: {str(e)})")
        
        return corruption_report