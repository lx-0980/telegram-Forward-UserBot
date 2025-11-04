from os import getenv

class Config(object):
    APP_ID = int(getenv("APP_ID", "21288218"))
    API_HASH = getenv("API_HASH", "dd47d5c4fbc31534aa764ef9918b3acd")
    TG_USER_SESSION = getenv("TG_USER_SESSION", "")
    ADMINS = [x.strip("@ ") for x in str(getenv("ADMINS", "") or "").split(",") if x.strip("@ ")]
    
