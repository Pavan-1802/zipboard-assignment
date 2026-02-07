import json
import os
import time
import pandas as pd
from huggingface_hub import InferenceClient

from scraper import scrape_all_articles

HF_TOKEN = "SAMPLE_HF_TOKEN"  
STATE_FILE = "articles_state.json"
EXCEL_FILE = "Articles.xlsx"

MODEL_REPO = "Qwen/Qwen2.5-7B-Instruct"

client = InferenceClient(api_key=HF_TOKEN)

def load_state():
    """
    Loads previous scrape data from the state JSON file.

    Returns:
        dict: The loaded state data or an empty dictionary if the file does not exist.
    """
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            print("[SUCCESS] Loaded previous state from JSON.")
            return json.load(f)
    print("[WARNING] No JSON found. Starting fresh.")
    return {}

def save_state(data):
    """
    Saves current scrape data to the state JSON file.

    Args:
        data (dict): The data to be saved to the JSON file.
    """
    with open(STATE_FILE, 'w') as f:
        json.dump(data, f, indent=4)
    print("[SUCCESS] JSON state updated.")

def generate_with_retry(prompt, retries=3):
    """
    Attempts to call the Inference API with a retry mechanism for rate limits.

    Args:
        prompt (str): The prompt to send to the AI model.
        retries (int): Number of retry attempts. Defaults to 3.

    Returns:
        str: The AI model's response or an error message if all attempts fail.
    """
    for attempt in range(retries):
        try:
            messages = [
                {"role": "system", "content": "You are a helpful documentation assistant. Keep answers short."},
                {"role": "user", "content": prompt}
            ]

            response = client.chat_completion(
                model=MODEL_REPO,
                messages=messages,
                max_tokens=100,
                temperature=0.5
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "503" in error_msg:
                wait_time = (attempt + 1) * 20
                print(f"[WARNING] API busy (429/503). Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            else:
                print(f"[ERROR] API Error: {e}")
                return "Analysis Failed"
    
    return "Rate Limit Exceeded"

def get_ai_gap_analysis(title, category):
    """
    Generates a documentation gap analysis for an article using the Inference API.

    Args:
        title (str): The title of the article.
        category (str): The category of the article.

    Returns:
        str: The results of the AI analysis.
    """
    print(f"[SUCCESS] AI analyzing: {title[:40]}...")
    
    prompt = f"""
    You are a senior technical documentation strategist.

    Analyze the following help article:
    - Title: "{title}"
    - Category: "{category}"

    Your task:
    Identify **one high-impact documentation gap** or **missing advanced topic** that an experienced or power user would reasonably expect but would not find covered by this article.

    Requirements:
        - The gap must be specific, non-obvious, and advanced (avoid beginner or generic topics).
        - It should clearly relate to the article’s subject and category.
        - Focus on practical depth, edge cases, advanced workflows, limitations, integrations, or scalability concerns.

    Output format:
        - A single sentence.
        - Clearly state *what is missing* and *why it matters* to advanced users.
    """
    
    return generate_with_retry(prompt)

def main():
    """
    Main execution function that orchestrates the scraping, comparison, and AI analysis process via Inference API.
    """
    prev_state = load_state()
    
    if not isinstance(prev_state, dict):
        prev_state = {}

    current_data = scrape_all_articles()
    
    updates_needed = False
    
    print("[SUCCESS] Comparing new data vs old state...")
    
    for url, article in current_data.items():
        is_new = url not in prev_state
        is_modified = False
        
        if not is_new:
            if prev_state[url].get('Last Updated') != article.get('Last Updated'):
                is_modified = True

        if is_new or is_modified:
            status = "NEW" if is_new else "UPDATED"
            print(f"   [{status}] {article['Article Title']}")
            
            gap_analysis = get_ai_gap_analysis(article['Article Title'], article['Category'])
            article['Gaps Identified'] = gap_analysis
            
            updates_needed = True
            
            time.sleep(2)
        else:
            article['Gaps Identified'] = prev_state[url].get('Gaps Identified', "")

    if updates_needed or len(prev_state) == 0:
        print("[SUCCESS] Saving updates...")
        save_state(current_data)
        
        df = pd.DataFrame(list(current_data.values()))
        cols = ["Article ID", "Article Title", "Category", "URL", "Last Updated", 
                "Content Type", "Keywords", "Word Count", "Has Screenshots", "Gaps Identified"]
        existing_cols = [c for c in cols if c in df.columns]
        df = df[existing_cols]
        
        df.to_excel(EXCEL_FILE, index=False)
        print(f"[SUCCESS] {EXCEL_FILE} updated.")
    else:
        print("[SUCCESS] No changes detected.")

if __name__ == "__main__":
    main()