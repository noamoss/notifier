from itsdangerous import URLSafeSerializer
from _config import SECRET_KEY, SECURITY_PASSWORD_SALT

def generate_confirmation_token(email):
    serializer = URLSafeSerializer(SECRET_KEY)
    return serializer.dumps(email, salt=SECURITY_PASSWORD_SALT)

def confirmed_token(token, expiration = 36000):
    serialzer = URLSafeSerializer(SECRET_KEY)
    try:
        email = serialzer.loads(
            token,
            salt = SECURITY_PASSWORD_SALT,
            max_age = expiration
        )
    except:
        return False
    return email