LINKEDIN_SELECTORS = {
    'company': [
        ".job-details-jobs-unified-top-card__company-name",
        ".jobs-unified-top-card__company-name",
        ".jobs-company__name",
        "div[data-test-id='job-company-name']",
        "//a[contains(@href, '/company/')]"
    ],
    'location': [
        ".job-details-jobs-unified-top-card__primary-description",
        ".jobs-unified-top-card__bullet",
        ".job-details-jobs-unified-top-card__workplace-type",
        ".jobs-unified-top-card__workplace-type",
        "div[contains(text(), 'Matches your job preferences')]",
        ".jobs-unified-top-card__subtitle-primary",
        ".jobs-unified-top-card__primary-description",
        ".jobs-unified-top-card__subtitle",
        "//span[contains(@class, 'location')]",
        "//div[contains(@class, 'location')]",
        "//div[contains(@class, 'job-insight')]//span[not(contains(text(), 'alum')) and not(contains(text(), 'school'))]",
        "//div[contains(@class, 'jobs-unified-top-card__job-insight')]/span[1]",
        "//div[contains(@class, 'jobs-unified-top-card__workplace-type')]",
        "//span[contains(@class, 'jobs-unified-top-card__workplace-type')]"
    ],
    'metadata': [
        ".jobs-unified-top-card__subtitle-secondary-grouping",
        ".jobs-unified-top-card__posted-date",
        ".jobs-unified-top-card__applicant-count",
        ".jobs-unified-top-card__bullet",
        ".jobs-unified-top-card__subtitle-secondary"
    ],
    'salary': [
        "//div[contains(@class, 'job-details-jobs-unified-top-card__job-insight')]//span[contains(text(), '$')]",
        "//div[contains(@class, 'job-details-jobs-unified-top-card__primary-description')]//span[contains(text(), '$')]",
        "//div[contains(@class, 'job-details-jobs-unified-top-card__job-insight')]//span[contains(text(), '/yr')]",
        "//span[contains(text(), 'K/yr')]",
        "//span[contains(text(), 'matches your job preferences')][contains(text(), '$')]",
        "//span[contains(text(), 'matches your job preferences')][contains(text(), '/yr')]",
        "//div[contains(text(), 'Base salary')]",
        "//span[contains(text(), 'Salary') or contains(text(), 'Pay')]/following-sibling::*",
        "//div[contains(@class, 'salary-range')]",
        ".jobs-unified-top-card__salary-details",
        ".job-details-jobs-unified-top-card__salary"
    ],
    'salary_patterns': [
        r'\$[\d,]+K?(?:/yr)?(?:\s*-\s*\$[\d,]+K?(?:/yr)?)?',
        r'[\d,]+K(?:/yr)?(?:\s*-\s*[\d,]+K(?:/yr)?)?',
        r'\$[\d,]+(?:/yr)?(?:\s*-\s*\$[\d,]+(?:/yr)?)?'
    ],
    'remote_indicators': [
        ".job-details-jobs-unified-top-card__job-insight",
        "span[contains(text(), 'Matches your job preferences')]",
        "span[contains(text(), 'workplace type is Remote')]",
        ".jobs-description__content",
        ".jobs-box__html-content",
        ".jobs-unified-top-card__job-insight",
        ".jobs-unified-top-card__workplace-type",
        "//*[contains(text(), 'Remote') and contains(text(), 'Matches your job preferences')]",
        "//*[contains(text(), 'remote-based role')]",
        "//*[contains(text(), 'This is a remote')]"
    ],
    'remote_text_patterns': [
        r'workplace type is remote',
        r'remote-based role',
        r'this is a remote',
        r'matches your job preferences.*remote',
        r'remote.*matches your job preferences'
    ],
    'posted_date': [
        ".jobs-unified-top-card__subtitle-secondary-grouping span",
        ".jobs-unified-top-card__posted-date",
        ".job-details-jobs-unified-top-card__subtitle-secondary-grouping span",
        ".job-details-jobs-unified-top-card__posted-date",
        "//span[contains(@class, 'jobs-unified-top-card__subtitle-secondary-grouping')]/span[contains(text(), 'ago')]",
        "//span[contains(@class, 'job-details-jobs-unified-top-card__subtitle-secondary-grouping')]/span[contains(text(), 'ago')]",
        "//div[contains(@class, 'unified-top-card')]//span[contains(text(), 'ago')]"
    ],
    'posted_patterns': [
        r'(\d+)\s+(?:minute|hour|day|week|month)s?\s+ago',
        r'Posted\s+(\d+)\s+(?:minute|hour|day|week|month)s?\s+ago',
        r'(\d+)\s+(?:minute|hour|day|week|month)s?\s+ago\s*·',
        r'·\s*(\d+)\s+(?:minute|hour|day|week|month)s?\s+ago'
    ]
}

LINKEDIN_VERSION_INDICATORS = {
    'v1': 'jobs-unified-top-card',
    'v2': 'job-view-layout',
    'v3': 'jobs-details'
}

LINKEDIN_LOGIN_INDICATORS = {
    'nav': 'global-nav__me',
    'profile': 'feed-identity-module'
}

LINKEDIN_VERSION_SELECTORS = {
    'v1': {
        'location': 'jobs-unified-top-card__bullet',
        'metadata': 'jobs-unified-top-card__subtitle-secondary',
        'premium': 'jobs-premium-company-growth',
        'remote': 'jobs-unified-top-card__job-insight'
    },
    'v2': {
        'location': 'job-details-jobs-unified-top-card__job-insight',
        'metadata': 'job-details-jobs-unified-top-card__job-insight',
        'premium': 'jobs-details-premium-insight',
        'remote': 'job-details-jobs-unified-top-card__job-insight'
    },
    'v3': {
        'location': 'job-view-layout jobs-details',
        'metadata': 'jobs-details',
        'premium': 'jobs-premium-applicant-insights',
        'remote': 'jobs-details__job-insight'
    }
}

LINKEDIN_PATTERNS = {
    'salary': r'\$[\d,]+ *[-/to]+ *\$[\d,]+',
    'posted': r'\d+\s*(?:minute|hour|day|week|month)s?\s*ago',
    'applicants': r'\d+\s*applicant',
    'location_indicators': ['greater', 'area', 'remote', ',']
}