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

    reg = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$#%-])[A-Za-z\d@$#%-]{6,20}$"
    pat = re.compile(reg)
    mat = re.search(pat, password)

    if mat:
        return system_handshake(ResultCode.SUCCESS)
    else:
        return system_handshake(ResultCode.FAIL)

