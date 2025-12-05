import secrets
import string

ALLOWED_TYPES = string.ascii_uppercase + string.digits
PASSCODE_LENGTH = 6

def create_passcode():
    """Creates an ASCII and digit passcode.

    Passcode implementation inspired by the following stack overflow answer: https://stackoverflow.com/a/39596292
    Creates a 1 in 2,176,782,336 code.
    """
    chars = [secrets.choice(ALLOWED_TYPES) 
             for i in range(PASSCODE_LENGTH)]
    passcode = ''.join(chars)
    return passcode