from email_validator import validate_email, EmailNotValidError
import re

def email_validator(email):
    try:
        validate_email(email)  
        return 1  
    except EmailNotValidError:
        return 0  
    

def password_validator(password):

    reg = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$#%-])[A-Za-z\d@$#%-]{6,20}$"
    pat = re.compile(reg)
    mat = re.search(pat, password)

    if mat:
        return 1
    else:
        return 0

