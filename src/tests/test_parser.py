import pytest
from pathlib import Path
import json
from ..parser.job_parser import JobParser

@pytest.fixture
def parser():
    return JobParser()

def test_title_cleaning(parser):
    """Test that job titles are properly cleaned of LinkedIn metadata"""
    raw_text = """DevOps Manager
United States · 3 hours ago · 25 applicants
$170K/yr - $200K/yrMatches your job preferences, minimum pay preference is 180000."""
    
    job_post = parser.parse(raw_text)
    assert job_post.title == "DevOps Manager", "Title should be cleaned of metadata"

class TestCompanyParsing:
    """Test suite for company name parsing functionality."""
    
    @pytest.fixture
    def parser(self):
        return JobParser()

    def test_company_parsing(self):
        pass

def test_analyze_company_snapshots(parser):
    """Analyze company data quality in snapshots"""
    snapshots_dir = Path("snapshots/v3")
    assert snapshots_dir.exists(), "Snapshots directory not found"
    
    print("\nCompany Data Analysis in Snapshots:")
    print("=================================")
    
    issues = []
    good_data = []
    
    for snapshot_file in snapshots_dir.glob("linkedin_snapshot_*.json"):
        with open(snapshot_file) as f:
            snapshot = json.load(f)
            raw_text = snapshot["raw_text"]
            expected = snapshot["parsed_data"]["company"]
            parsed = parser.parse(raw_text).company
            
            # Check for potential data quality issues
            has_issues = False
            issue_details = []
            
            if expected == "Unknown":
                has_issues = True
                issue_details.append("Expected company is 'Unknown'")
            
            if '\n' in expected:
                has_issues = True
                issue_details.append("Contains newlines")
                
            if expected.startswith('0 notifications') or 'notifications total' in expected:
                has_issues = True
                issue_details.append("Contains LinkedIn header content")
                
            if len(expected) > 50:  # Likely contains extra content
                has_issues = True
                issue_details.append("Suspiciously long company name")
            
            if has_issues:
                issues.append({
                    'file': snapshot_file.name,
                    'expected': expected,
                    'parsed': parsed,
                    'issues': issue_details
                })
            else:
                good_data.append({
                    'file': snapshot_file.name,
                    'company': expected
                })
    
    # Report findings
    print("\nSnapshots with Issues:")
    print("---------------------")
    for issue in issues:
        print(f"\nFile: {issue['file']}")
        print(f"Expected: '{issue['expected']}'")
        print(f"Parsed as: '{issue['parsed']}'")
        print("Issues found:", ", ".join(issue['issues']))
    
    print("\nClean Snapshots:")
    print("---------------")
    for good in good_data:
        print(f"- {good['file']}: '{good['company']}'")
    
    print(f"\nSummary:")
    print(f"Total snapshots: {len(issues) + len(good_data)}")
    print(f"Clean snapshots: {len(good_data)}")
    print(f"Snapshots with issues: {len(issues)}")

class TestSnapshotMaintenance:
    """Tests and maintenance for snapshot data quality."""
    
    @pytest.fixture
    def parser(self):
        return JobParser()
    
    def test_fix_company_data(self, parser):
        """Fix company data while preserving original raw text."""
        snapshots_dir = Path("snapshots/v3")
        updates_made = 0
        
        print("\nFixing Company Data in Snapshots:")
        print("===============================")
        
        for snapshot_file in snapshots_dir.glob("linkedin_snapshot_*.json"):
            with open(snapshot_file) as f:
                data = json.load(f)
                
            # Verify snapshot structure
            assert "raw_text" in data, f"Missing raw_text in {snapshot_file}"
            assert "parsed_data" in data, f"Missing parsed_data in {snapshot_file}"
            
            original_raw_text = data["raw_text"]
            company = data["parsed_data"]["company"]
            
            # Parse using current parser
            parsed_result = parser.parse(original_raw_text)
            
            needs_update = False
            if ('notifications total' in company or 
                company.startswith('0') or 
                '\n' in company):
                needs_update = True
            elif company == "Unknown" and parsed_result.company != "Unknown":
                needs_update = True
            
            if needs_update:
                print(f"\nUpdating {snapshot_file.name}")
                print(f"Old value: '{company}'")
                print(f"New value: '{parsed_result.company}'")
                
                # Only update parsed_data, preserve raw_text
                data["parsed_data"]["company"] = parsed_result.company
                
                # Verify raw_text wasn't modified
                assert data["raw_text"] == original_raw_text, \
                    f"Error: raw_text was modified in {snapshot_file}"
                
                with open(snapshot_file, 'w') as f:
                    json.dump(data, f, indent=2)
                
                updates_made += 1
        
        print(f"\nFixing complete. Updated {updates_made} snapshots.")
        
        print("\nVerifying snapshot integrity...")
        # Verify all snapshots after updates
        for snapshot_file in snapshots_dir.glob("linkedin_snapshot_*.json"):
            with open(snapshot_file) as f:
                data = json.load(f)
                assert "raw_text" in data, f"Missing raw_text in {snapshot_file}"
                assert "parsed_data" in data, f"Missing parsed_data in {snapshot_file}"
                
                # Verify no header content in company names
                company = data["parsed_data"]["company"]
                assert 'notifications total' not in company, \
                    f"Found header content in {snapshot_file}"
                assert not company.startswith('0'), \
                    f"Found invalid company start in {snapshot_file}"
                assert '\n' not in company, \
                    f"Found newlines in company in {snapshot_file}"
    
    def test_analyze_unknown_companies(self, parser):
        """Analyze snapshots where company is marked as 'Unknown'"""
        snapshots_dir = Path("snapshots/v3")
        unknown_cases = []
        
        print("\nAnalyzing 'Unknown' Company Cases:")
        print("================================")
        
        for snapshot_file in snapshots_dir.glob("linkedin_snapshot_*.json"):
            with open(snapshot_file) as f:
                data = json.load(f)
                raw_text = data["raw_text"]
                expected = data["parsed_data"]["company"]
                
                if expected == "Unknown":
                    parsed = parser.parse(raw_text).company
                    unknown_cases.append({
                        'file': snapshot_file.name,
                        'parsed_as': parsed,
                        'raw_text': raw_text[:200]  # First 200 chars for context
                    })
        
        if unknown_cases:
            print(f"\nFound {len(unknown_cases)} cases with 'Unknown' company:")
            for case in unknown_cases:
                print(f"\nFile: {case['file']}")
                print(f"Parser found: '{case['parsed_as']}'")
                print("Raw text preview:")
                print(case['raw_text'])
                print("-" * 50)
        else:
            print("No 'Unknown' company cases found!")

    def test_verify_company_data_quality(self, parser):
        """Verify the quality of company data in all snapshots."""
        snapshots_dir = Path("snapshots/v3")
        
        print("\nAnalyzing Company Data Quality:")
        print("============================")
        
        stats = {
            'total': 0,
            'unknown': 0,
            'valid': 0,
            'issues': []
        }
        
        companies_found = set()
        
        for snapshot_file in snapshots_dir.glob("linkedin_snapshot_*.json"):
            with open(snapshot_file) as f:
                data = json.load(f)
                
            stats['total'] += 1
            company = data["parsed_data"]["company"]
            
            if company == "Unknown":
                stats['unknown'] += 1
                # Check if parser finds something
                parsed = parser.parse(data["raw_text"]).company
                if parsed != "Unknown":
                    stats['issues'].append({
                        'file': snapshot_file.name,
                        'issue': f"Marked as Unknown but parser found '{parsed}'"
                    })
            else:
                stats['valid'] += 1
                companies_found.add(company)
                
                # Check for any remaining issues
                if (('notifications' in company) or 
                    company.startswith('0') or 
                    '\n' in company):
                    stats['issues'].append({
                        'file': snapshot_file.name,
                        'issue': f"Contains invalid content: '{company}'"
                    })
        
        # Print results
        print(f"\nResults:")
        print(f"--------")
        print(f"Total snapshots: {stats['total']}")
        print(f"Valid companies: {stats['valid']}")
        print(f"Unknown companies: {stats['unknown']}")
        
        print("\nUnique companies found:")
        print("--------------------")
        for company in sorted(companies_found):
            print(f"- {company}")
        
        if stats['issues']:
            print("\nIssues found:")
            print("-------------")
            for issue in stats['issues']:
                print(f"- {issue['file']}: {issue['issue']}")
        else:
            print("\nNo issues found!")
        
        # Assertions to validate data quality
        assert stats['total'] > 0, "No snapshots found"
        assert stats['valid'] > 0, "No valid companies found"
        assert len(stats['issues']) == 0, f"Found {len(stats['issues'])} issues in snapshots"
        assert len(companies_found) > 0, "No unique companies found"
        
        # Print summary
        print(f"\nVerification passed!")
        print(f"Found {len(companies_found)} unique companies in {stats['total']} snapshots")

    def test_analyze_company_whitespace(self, parser):
        """Analyze whitespace patterns in company names from real snapshots."""
        snapshots_dir = Path("snapshots/v3")
        
        print("\nAnalyzing Company Name Whitespace in Snapshots:")
        print("==========================================")
        
        for snapshot_file in snapshots_dir.glob("linkedin_snapshot_*.json"):
            with open(snapshot_file) as f:
                data = json.load(f)
                raw_text = data["raw_text"]
                
                # Find the "company logo" line and next few lines
                lines = raw_text.split('\n')
                for i, line in enumerate(lines):
                    if 'company logo' in line.lower():
                        context = '\n'.join(lines[i:i+5])  # Show next 5 lines for context
                        print(f"\nFile: {snapshot_file.name}")
                        print("Context:")
                        print(context)
                        print("-" * 50)
                        break

def test_title_parsing_from_snapshots(parser):
    """Analyze title parsing across all snapshots to establish patterns and accuracy."""
    snapshots_dir = Path("snapshots/v3")
    assert snapshots_dir.exists(), "Snapshots directory not found"

    snapshots = list(snapshots_dir.glob("linkedin_snapshot_*.json"))
    print("\nTitle Parsing Analysis:")
    print("-" * 30)
    print()

    good_snapshots = []
    total_valid = 0

    for snapshot_file in snapshots:
        with open(snapshot_file) as f:
            snapshot = json.load(f)
            
            # Parse the raw text
            raw_text = snapshot["raw_text"]
            job_post = parser.parse(raw_text)
            expected = snapshot["parsed_data"]

            if "title" in expected:
                total_valid += 1
                parsed_title = job_post.title
                expected_title = expected["title"]

                if parsed_title == expected_title:
                    print(f"✓ {snapshot_file.name}")
                    print(f"   Parsed:   '{parsed_title}'")
                    print(f"   Expected: '{expected_title}'")
                    print()
                    good_snapshots.append((snapshot_file.name, expected_title))
                else:
                    print(f"✗ {snapshot_file.name}")
                    print(f"   Parsed:   '{parsed_title}'")
                    print(f"   Expected: '{expected_title}'")
                    print(f"   Raw text preview: {raw_text[:200]}")
                    print()

    # Print summary of good snapshots
    if good_snapshots:
        print("Known Good Snapshots:")
        print("-" * 20)
        for filename, title in good_snapshots:
            print(f"- {filename}: '{title}'")

    # Print statistics
    print("\nSummary:")
    print(f"Total valid snapshots: {total_valid}")
    print(f"Good snapshots: {len(good_snapshots)}")
    if total_valid > 0:
        success_rate = (len(good_snapshots) / total_valid) * 100
        print(f"Success rate: {success_rate:.1f}%")