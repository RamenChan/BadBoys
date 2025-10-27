from db_connection import client
from datetime import datetime
import traceback

"""
def log_error(error_message, function_name="unknown"):

    try:
        db = client["BadBoys"]
        db["logger"].insert_one({
            "function": function_name,
            "error": error_message,
            "traceback": traceback.format_exc(),
            "created_at": datetime.utcnow()
        })
    except Exception as e:
        print("Logger hatası:", e)
        """