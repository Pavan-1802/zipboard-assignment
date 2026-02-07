import re
from collections import Counter


STOPWORDS = {
    "this","that","with","from","your","have","will","into",
    "using","use","used","can","how","what","when","where",
    "there","their","about","which","while","should",
    "could","would","these","those","been","being",
    "them","then","than","also","more","such",
    "only","other","some","each","very","much",
    "many","over","under","between","does","did",
    "doing","done","you","are","for","the","and",
    "but","not","all","any","our","out","get",
    "set","add","new","zipboard","click","screen"
}


def extract_keywords(article, top_n=10):
    """
    Extracts the most frequent and relevant keywords from an article based on headers, bold text, and body content.

    Args:
        article (BeautifulSoup element): The article element to extract keywords from.
        top_n (int): The number of top keywords to return. Defaults to 10.

    Returns:
        list: A list of the top N keywords found in the article.
    """

    freq = Counter()

    for tag in article.find_all(['h1','h2','h3']):
        words = re.findall(r'[a-z]+', tag.get_text().lower())
        freq.update([w for w in words if w not in STOPWORDS and len(w) > 3] * 3)

    for tag in article.find_all(['strong','b']):
        words = re.findall(r'[a-z]+', tag.get_text().lower())
        freq.update([w for w in words if w not in STOPWORDS and len(w) > 3] * 2)

    body_words = re.findall(r'[a-z]+', article.get_text().lower())
    freq.update([w for w in body_words if w not in STOPWORDS and len(w) > 3])

    return [word for word, _ in freq.most_common(top_n)]