from db_connection import client
from datetime import datetime
import traceback
from enum import IntEnum


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


class ResultCode(IntEnum): 
    SUCCESS = 1 
    FAIL = -1
    INFO = 0 
    WARNING = 2 
    ERROR = -99
     

def system_handshake(resultCode: ResultCode, message='', data=None, error_message= None, function_name=None): 

    default_messages = { 
        ResultCode.SUCCESS: "Olumlu Durum",
        ResultCode.FAIL: "Negatif Durum", 
        ResultCode.INFO: "Olumsuz Durum", 
        ResultCode.WARNING: "Beklenenden farklı bir veri çıktısı alındı.", 
        ResultCode.ERROR: "Beklenmedik Bir Hata Oluştu!" } 
    
    if resultCode == ResultCode.ERROR and error_message is not None:
        try:
            log_error(error_message or default_messages[ResultCode.ERROR], function_name=function_name)
        except Exception as log_exc:
            print("Logger hatası:", log_exc)


    return { 
        "status": resultCode != ResultCode.ERROR, 
        "code": resultCode, 
        "message": message or default_messages.get(resultCode, "Tanımsız durum") ,
        "data": data
        }