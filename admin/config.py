# Create dummy secrey key so we can use sessions
SECRET_KEY = 'mRo48tU4ebP6jIshqaoNf2HAnesrCGHm'

# Create in-memory database
SQLALCHEMY_DATABASE_URI = "postgresql:///newappv2?client_encoding=utf8"
SQLALCHEMY_ECHO = False

# Flask-Security config
SECURITY_URL_PREFIX = "/admin"
SECURITY_PASSWORD_SALT = 'None'
SECURITY_PASSWORD_HASH = "bcrypt"

# Flask-Security URLs, overridden because they don't put a / at the end
SECURITY_LOGIN_URL = "/login/"
SECURITY_LOGOUT_URL = "/logout/"
SECURITY_REGISTER_URL = "/login/"

SECURITY_POST_LOGIN_VIEW = "/admin/"
SECURITY_POST_LOGOUT_VIEW = "/admin/"
SECURITY_POST_REGISTER_VIEW = "/admin/"

# Flask-Security features
SECURITY_REGISTERABLE = False
SECURITY_SEND_REGISTER_EMAIL = False
SQLALCHEMY_TRACK_MODIFICATIONS = False
