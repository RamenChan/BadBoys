import requests
from bs4 import BeautifulSoup
from db_connection import client
from core import now_ts
from system_utilities import ResultCode, system_handshake
from config import Config




def get_data_by_api():
    try:
                
        db = client["services"]
        collection = db["api-hacker-news"]

        url = f"{Config.HACKER_NEWS_API_URL}/topstories.json"
        r = requests.get(url)
        ids = r.json()[:Config.MAX_STORIES_FETCH]

        stories = []
        for story_id in ids:
            item = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json").json()
            if item:
                item["source"] = "api"
                stories.append(item)

        doc = {
            "fetched_at": now_ts(),
            "stories": stories
        }
        collection.insert_one(doc) 
        return system_handshake(ResultCode.SUCCESS)
    
    except Exception as e:
        return system_handshake(ResultCode.ERROR, error_message=str(e), function_name= "services/api/get_data_by_api")
    
def get_data_by_html():
    try:
        url = Config.HACKER_NEWS_HTML_URL
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        titles = soup.select(".athing")
        subtexts = soup.select(".subtext")

        stories = []

        for i in range(min(Config.MAX_STORIES_FETCH, len(titles))):

            title_row = titles[i]
            story_id = title_row.get("id")
            title = title_row.select_one(".titleline > a").get_text(strip=True)
            link = title_row.select_one(".titleline > a")["href"]

            sub = subtexts[i]
            score_tag = sub.select_one(".score")
            score = score_tag.get_text(strip=True) if score_tag else None

            user_tag = sub.select_one(".hnuser")
            user = user_tag.get_text(strip=True) if user_tag else None

            stories.append({
                "id": story_id,
                "title": title,
                "url": link,
                "score": score,
                "by": user,
                "source": "html"
            })

        db = client["services"]
        collection = db["html-hacker-news"]

        document = {
            "fetched_at": now_ts(),
            "stories": stories
        }

        collection.insert_one(document)

        return system_handshake(ResultCode.SUCCESS)

    except Exception as e:
        return system_handshake(ResultCode.ERROR,error_message=str(e),function_name="services/html/get_data_by_html")

def get_stories(name):
    try:
        db = client["services"]
        collection = db["api-hacker-news"] if name == 'api' else db["html-hacker-news"]

        latest_cursor = collection.find().sort("_id", -1).limit(1)
        latest_list = list(latest_cursor)

        if len(latest_list) == 0:
            return system_handshake(
                ResultCode.ERROR,
                error_message='Gösterimi Yapılacak Data Bulunamadı.',
                function_name="services/api/get_stories"
            )

        story = dict(latest_list[0])
        story.pop("_id", None) 

        return system_handshake(ResultCode.SUCCESS, data=story)

    except Exception as e:
        return system_handshake(ResultCode.ERROR,error_message=str(e),function_name="services/api/get_stories")
