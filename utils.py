def get_word_count(article):
    """
    Calculates the word count of the provided article element.

    Args:
        article (BeautifulSoup element): The article element to count words from.

    Returns:
        int: The number of words in the article.
    """
    text = article.get_text(" ", strip=True)
    words = text.split()
    return len(words)

def has_screenshots(article):
    """
    Checks if the article contains screenshots, excluding common icons and logos.

    Args:
        article (BeautifulSoup element): The article element to check for screenshots.

    Returns:
        str: "Yes" if screenshots are found, otherwise "No".
    """
    images = article.find_all("img")

    for img in images:
        src = img.get("src", "")
        if any(x in src.lower() for x in ["logo", "icon", "avatar"]):
            continue
        if "docs/assets" in src:
            return "Yes"
            
    return "No"
