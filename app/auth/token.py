import jwt

from datetime import timedelta, datetime
from typing import Optional, Dict, Any
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

from app.dto.auth_dto import UserInfoInJWT
from app.core.config import CONFIG
from app.utils.conversion import get_current_utc_time


class TokenManager:

    secret_key = CONFIG.SECRET_KEY
    algorithm = "HS256"
    token_expiration = timedelta(hours=24)  # Default 24 hour expiration

    @classmethod
    def generate_token(self, data: UserInfoInJWT, expires_delta: Optional[timedelta] = None) -> str:
        """
        Generate a JWT token with the given data and expiration time

        Args:
            data: Dictionary containing data to encode in the token
            expires_delta: Optional custom expiration time, defaults to 24 hours

        Returns:
            str: Generated JWT token
        """
        to_encode = dict(data).copy()
        expire = get_current_utc_time() + (expires_delta or self.token_expiration)
        to_encode.update({"exp": expire})

        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    @classmethod
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode a JWT token

        Args:
            token: JWT token string to verify

        Returns:
            Dict[str, Any]: Decoded token payload

        Raises:
            InvalidTokenError: If token is invalid
            ExpiredSignatureError: If token has expired
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except ExpiredSignatureError:
            raise ExpiredSignatureError("Token has expired")
        except InvalidTokenError:
            raise InvalidTokenError("Invalid token")
