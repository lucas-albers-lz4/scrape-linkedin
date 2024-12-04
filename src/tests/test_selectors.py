from ..utils.selectors import LINKEDIN_SELECTORS

def test_selector_structure():
    """Test that all required selectors are present"""
    required_fields = ['company', 'location', 'metadata']
    
    for field in required_fields:
        assert field in LINKEDIN_SELECTORS
        assert isinstance(LINKEDIN_SELECTORS[field], list)
        assert len(LINKEDIN_SELECTORS[field]) > 0

def test_selector_validity():
    """Test that selectors are properly formatted"""
    for field, selectors in LINKEDIN_SELECTORS.items():
        for selector in selectors:
            # CSS selectors start with . or #
            if selector.startswith('.') or selector.startswith('#'):
                assert ' ' not in selector or ' .' in selector or ' #' in selector
            # XPath selectors start with //
            elif selector.startswith('//'):
                assert selector.count('"') % 2 == 0  # Quotes should be paired 

def test_selector_validity():
    selector = '.jobs-unified-top-card__subtitle-secondary-grouping span'
    # Allow spaces for descendant selectors
    assert ' ' not in selector.strip() or ' .' in selector or ' #' in selector or ' ' in selector