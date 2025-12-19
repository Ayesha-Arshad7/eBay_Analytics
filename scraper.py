from GoogleNews import GoogleNews
import pandas as pd
import requests
from fake_useragent import UserAgent
from newspaper import fulltext

company = "eBay"
all_results = []

googlenews = GoogleNews(lang='en', region='US', period='2d')
googlenews.search(company)

for page in range(1, 6):
    googlenews.get_page(page)
    all_results.extend(googlenews.results())

googlenews.clear()

df = pd.DataFrame(all_results)

ua = UserAgent()
rows = []

for _, row in df.iterrows():
    link = str(row.get("link", ""))

    if not link.startswith("http"):
        continue

    try:
        html = requests.get(link, headers={'User-Agent': ua.chrome}, timeout=7).text
        text = fulltext(html)
    except:
        text = "Could not extract text"

    rows.append([
        row.get("title", ""),
        row.get("media", ""),
        row.get("date", ""),
        row.get("desc", ""),
        link,
        text
    ])

final_df = pd.DataFrame(
    rows,
    columns=["title", "media", "date", "description", "link", "full_text"]
)

final_df.to_csv("data/ebay_news.csv", index=False)

print("✅ Data saved in data/ebay_news.csv")
