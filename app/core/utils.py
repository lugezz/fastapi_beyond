import logging
from datetime import UTC, datetime, timedelta

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from app.core.config import settings

logger = logging.getLogger(__name__)


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
        except ExpiredSignatureError:
            logger.warning("Password reset token has expired")
        except InvalidTokenError:
            logger.warning("Password reset token is invalid")
            return None
