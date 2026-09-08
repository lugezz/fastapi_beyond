import jwt
from datetime import UTC, datetime, timedelta

from app.core.config import settings


class TokenUtils:
    def create_url_safe_token(self, data: dict, expires_minutes: int = 30) -> str:
        payload = {
            **data,
            "exp": datetime.now(UTC) + timedelta(minutes=expires_minutes),
        }
        return jwt.encode(
            payload,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )

    def decode_url_safe_token(self, token: str) -> dict | None:
        try:
            return jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
            )
        except jwt.InvalidTokenError:
            return None
