import secrets
import string

ALLOWED_TYPES = string.ascii_uppercase + string.digits
PASSCODE_LENGTH = 6

def create_passcode() -> str:
    chars = [secrets.choice(ALLOWED_TYPES) 
             for i in range(PASSCODE_LENGTH)]
    passcode = ''.join(chars)
    return passcode