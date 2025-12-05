# jwt_utils.py
import jwt
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


def create_access_token(user, minutes=30):
    now = datetime.utcnow()
    payload = {
        "user_id": user.id,
        "email": getattr(user, "email", ""),
        "is_staff": getattr(user, "is_staff", False),
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=minutes),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    # PyJWT >= 2 returns str already
    return token


def decode_access_token(token: str):
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"],
        )
    except jwt.ExpiredSignatureError:
        return None, "Token expired"
    except jwt.InvalidTokenError:
        return None, "Invalid token"

    user_id = payload.get("user_id")
    if not user_id:
        return None, "Invalid payload"

    try:
        user = User.objects.get(id=user_id, is_active=True)
    except User.DoesNotExist:
        return None, "User not found"

    return user, None
