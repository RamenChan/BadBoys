from db_connection import client
from datetime import datetime
import traceback


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


def system_handshake(resultCode, message = ''):
    
    if resultCode == 1:
        return {"status": True, "code": 1, "message": message or "Olumlu Durum"}
    elif resultCode == 0:
        return {"status": True, "code": 0, "message": message or "Olumsuz Durum"}
    elif resultCode == 2:
        return {"status": True, "code": 2, "message": message or "Beklenenden farklı bir veri çıktısı alındı."}
    else:
        return {"status": False, "code": -99, "message": message or "Beklenmedik Bir Hata Oluştu!"}
