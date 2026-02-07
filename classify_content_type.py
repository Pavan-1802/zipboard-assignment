import re

def classify_content_type(title):
    """
    Classifies the content type of an article based on its title using pre-defined patterns.

    Args:
        title (str): The title of the article.

    Returns:
        str: The classified content type (e.g., "Troubleshooting", "How-To Guide", etc.).
    """
    t = title.lower().strip()

    troubleshooting_patterns = [
        r'error',
        r'issue',
        r'fix',
        r'stuck',
        r'not working',
        r'failed',
        r'problem',
        r'why am i',
        r'what happens if',
    ]

    if any(re.search(p, t) for p in troubleshooting_patterns):
        return "Troubleshooting"

    howto_patterns = [
        r'^how\b',
        r'^how to',
        r'^how do i',
        r'^how can i',
    ]

    if any(re.search(p, t) for p in howto_patterns):
        return "How-To Guide"

    faq_patterns = [
        r'^can i',
        r'^does',
        r'^do i',
        r'^will',
        r'^is there',
        r'^are there',
        r'\?$'
    ]

    if any(re.search(p, t) for p in faq_patterns):
        return "FAQ"

    onboarding_patterns = [
        r'getting started',
        r'workflow',
        r'guide',
        r'introduction',
        r'best practices'
    ]

    if any(re.search(p, t) for p in onboarding_patterns):
        return "Onboarding / Guide"

    concept_patterns = [
        r'^what is',
        r'^what are',
        r'difference between',
        r'understanding',
        r'overview',
        r'roles and permissions',
        r'parts of'
    ]

    if any(re.search(p, t) for p in concept_patterns):
        return "Concept / Explanation"

    feature_patterns = [
        r'new update',
        r'streamlining',
        r'latest',
        r'feature',
        r'powered'
    ]

    if any(re.search(p, t) for p in feature_patterns):
        return "Feature Announcement"

    return "General Guide"