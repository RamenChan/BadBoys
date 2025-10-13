from email_validator import validate_email, EmailNotValidError

def email_validator(email):
    try:
        validate_email(email)  
        return 1  
    except EmailNotValidError:
        return 0  
