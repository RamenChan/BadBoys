import requests
from db_connection import client
from core import now_ts
from system_utilities import ResultCode, system_handshake
import pytz




def get_data_by_api():
    try:
                
        db = client["services"]
        collection = db["api-hacker-news"]

        r = requests.get(f"https://hacker-news.firebaseio.com/v0/topstories.json")
        ids = r.json()[:20]

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
        result = collection.insert_one(doc) 
        return system_handshake(ResultCode.SUCCESS)
    
    except Exception as e:
        return system_handshake(ResultCode.ERROR, error_message=str(e), function_name= "services/api/get_data_by_api")
    

def get_stories():
    try:
        db = client["services"]
        collection = db["api-hacker-news"]

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

    
    
print(get_data_by_api())
