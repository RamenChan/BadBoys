from email_validator import validate_email, EmailNotValidError
import re
from system_utilities import system_handshake, ResultCode

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
    if not re.search(r"[@$#%-]", password):
        errors.append("Şifre en az bir özel karakter (@, $, #, %, -) içermeli.")

    if errors:
        return system_handshake(ResultCode.INFO, message="Şifre doğrulama başarısız", data=errors)
    else:
        return system_handshake(ResultCode.SUCCESS,message="Şifre geçerli")


