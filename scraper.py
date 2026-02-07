"""
scraper.py
Fetches data from zipBoard Help Center and returns it as a list of dictionaries.
"""
import time
import requests
from bs4 import BeautifulSoup
from classify_content_type import classify_content_type
from utils import get_word_count, has_screenshots
from extract_keywords import extract_keywords

BASE_URL = "https://help.zipboard.co"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch(url):
    """
    Fetches the content of a URL and returns a BeautifulSoup object.

    Args:
        url (str): The URL to fetch.

    Returns:
        BeautifulSoup: The parsed HTML content.
    """
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return BeautifulSoup(response.text, 'html.parser')

def get_categories():
    """
    Retrieves all article category URLs from the base URL.

    Returns:
        list: A list of unique category URLs.
    """
    soup = fetch(BASE_URL)
    categories = []
    for link in soup.find_all('a', href=True):
        if link['href'].startswith('/category'):
            categories.append(BASE_URL + link['href'])
    return list(set(categories))

def get_articles_from_category(category_url):
    """
    Retrieves all article URLs from a specific category page.

    Args:
        category_url (str): The URL of the category page.

    Returns:
        list: A list of tuples containing (article_url, category_title).
    """
    soup = fetch(category_url)
    category_title = soup.find('h1').text if soup.find('h1') else "No Title"
    article_list = soup.find('ul', class_='articleList')
    
    if not article_list: return []
    
    articles = []
    for link in article_list.find_all('a', href=True):
        if link['href'].startswith('/article'):
            articles.append((BASE_URL + link['href'], category_title))
    return articles

def parse_article(article_url, category_title):
    """
    Parses an individual article page to extract metadata and content details.

    Args:
        article_url (str): The URL of the article.
        category_title (str): The title of the category the article belongs to.

    Returns:
        dict: A dictionary containing extracted article data, or None if parsing fails.
    """
    try:
        soup = fetch(article_url)
        article_container = soup.find("article", id="fullArticle")
        if not article_container: return None

        article_title = soup.find('h1').text if soup.find('h1') else "No Title"
        article_id = article_url.split('/article/')[1].split('-')[0]
        
        last_updated = soup.find('time', class_='lu')
        last_updated_txt = last_updated.text.replace("Last updated on ", "") if last_updated else "Not Available"

        return {
            "Article ID": article_id,
            "Article Title": article_title,
            "Category": category_title,
            "URL": article_url,
            "Last Updated": last_updated_txt,
            "Content Type": classify_content_type(article_title),
            "Keywords": ", ".join(extract_keywords(article_container)), 
            "Word Count": get_word_count(article_container),
            "Has Screenshots": has_screenshots(article_container),
            "Gaps Identified": "" 
        }
    except Exception as e:
        print(f"[ERROR] Parsing {article_url}: {e}")
        return None

def scrape_all_articles():
    """
    Main scraping function that iterates through all categories and articles to collect data.

    Returns:
        dict: A dictionary of scraped article data, keyed by URL.
    """
    print("[SUCCESS] Scraper started...")
    categories = get_categories()
    print(f"[SUCCESS] Found {len(categories)} categories. Fetching articles...")
    
    scraped_data = {}
    visited_urls = set()

    for category in categories:
        articles = get_articles_from_category(category)
        for url, cat_title in articles:
            if url in visited_urls: continue
            
            data = parse_article(url, cat_title)
            if data:
                scraped_data[url] = data
                visited_urls.add(url)
            
            time.sleep(0.5) 
            
    print(f"[SUCCESS] Scrape finished. Collected {len(scraped_data)} articles.")
    return scraped_data

if __name__ == "__main__":
    data = scrape_all_articles()
    if data:
        print(list(data.values())[0])
