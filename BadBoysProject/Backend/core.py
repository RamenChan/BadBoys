from email_validator import validate_email, EmailNotValidError
import re
from system_utilities import system_handshake, ResultCode
from datetime import datetime, timezone


def email_validator(email):
    try:
        validate_email(email)  
        return system_handshake(ResultCode.SUCCESS)
    except EmailNotValidError:
        return system_handshake(ResultCode.FAIL)


def password_validator(password):
    errors = []

    if not (len(password) <= 12):
        errors.append("Şifre en az 12 karakterden oluşmalı.")
    if not re.search(r"[a-z]", password):
        errors.append("Şifre en az bir küçük harf içermeli.")
    if not re.search(r"[A-Z]", password):
        errors.append("Şifre en az bir büyük harf içermeli.")
    if not re.search(r"\d", password):
        errors.append("Şifre en az bir rakam içermeli.")
    if not re.search(r"[@#%-]", password):
        errors.append("Şifre en az bir (@, #, %, -) karakterlerinden içermeli.")

    if errors:
        return system_handshake(ResultCode.INFO, message="Şifre doğrulama başarısız", data=errors)
    elif len(password) >= 72:
        errors.append("Şifreniz 72 karakterden fazla olamaz.")
        return system_handshake(ResultCode.INFO, message="Şifre doğrulama başarısız", data=errors)            
    else:
        return system_handshake(ResultCode.SUCCESS,message="Şifre geçerli")
    
    
def isvalid_key(key):

    MAX_KEY_LEN = 100

    dangerous_keys = ['__proto__', 'constructor', 'prototype']

    if len(key) > MAX_KEY_LEN:
        return system_handshake(ResultCode.FAIL, f"Çok uzun bir değer girildi. Girilebilecek max değer; {MAX_KEY_LEN}.")


    if not isinstance(key, str):
        return system_handshake(ResultCode.FAIL, 'Gönderilen değer str değildir.')
    
    if key.startswith('$') or '.' in key:
        return system_handshake(ResultCode.FAIL, 'Gönderilen değerler içerisinde "$" ve "." gibi değerler yakalandı.')
    
    for i in dangerous_keys:
        if i in key.lower():
            return system_handshake(ResultCode.FAIL, f'Tehlikeli anahtar adı yakalandı: {i}')

    return system_handshake(ResultCode.SUCCESS)


def validate_payload(data):

    if isinstance(data, dict):
        for key, value in data.items():
            res = isvalid_key(key)
            if res['code'] != ResultCode.SUCCESS:
                return res
            res = validate_payload(value)
            if res['code'] != ResultCode.SUCCESS:
                return res
        return system_handshake(ResultCode.SUCCESS, 'Payload anahtarları geçerli.')
    
    elif isinstance(data, list):
        for item in data:
            r = validate_payload(item)
            if r.code != ResultCode.SUCCESS:
                return r
        return system_handshake(ResultCode.SUCCESS, 'Payload anahtarları geçerli.')
    
    else: 
        return system_handshake(ResultCode.SUCCESS,'Anahtar Geçerli')

def now_ts():
    try:
        return int(datetime.now(timezone.utc).timestamp())
    except Exception as e:
        return system_handshake(ResultCode.ERROR, error_message=str(e), function_name="core/now_ts")

def now_date():
    try:
        return datetime.now(timezone.utc)
    except Exception as e:
        return system_handshake(ResultCode.ERROR, error_message=str(e), function_name="core/now_date")

def date_to_timestamp(date):
    try:
        if isinstance(date, int):
            return date
        if isinstance(date, float):
            return int(date)
        if isinstance(date, str):
            try:
                dt = datetime.fromisoformat(date.replace("Z", "+00:00"))
                return int(dt.replace(tzinfo=timezone.utc).timestamp())
            except:
                pass
            raise ValueError("Unsupported string date format")

        if isinstance(date, datetime):
            return int(date.replace(tzinfo=timezone.utc).timestamp())

        return system_handshake(ResultCode.INFO, message='Beklenmeyen Tarih Formatı Girildi')

    except Exception as e:
        return system_handshake(ResultCode.ERROR, error_message=str(e), function_name="core/date_to_timestamp")

def timestamp_to_date(ts):
    try:
        if isinstance(ts, datetime):
            return ts
        return datetime.fromtimestamp(int(ts), tz=timezone.utc)
    except Exception as e:
        return system_handshake(ResultCode.ERROR, error_message=str(e), function_name="core/timestamp_to_date")
