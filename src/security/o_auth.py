from datetime import datetime, timedelta, timezone
from typing import Optional, Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose.exceptions import JWTError
from passlib.context import CryptContext
import os


# =========================
# OAuth2 Scheme
# =========================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


# =========================
# Config
# =========================
SECRET_KEY = os.getenv("LOGIN_SECRET_KEY", "secret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))


# =========================
# Password Hashing
# =========================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthDependency:
    def __init__(
        self,
        secret_key: str = SECRET_KEY,
        algorithm: str = ALGORITHM,
        expiry_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES,
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expiry_minutes = expiry_minutes

    # # =========================
    # # PASSWORD UTILS
    # # =========================
    # def verify_password(self, plain_password: str, hashed_password: str) -> bool:
    #     return pwd_context.verify(plain_password, hashed_password)

    # def get_password_hash(self, password: str) -> str:
    #     return pwd_context.hash(password)

    # =========================
    # TOKEN CREATION
    # =========================
    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        to_encode = data.copy()

        expire = datetime.now(timezone.utc) + (
            expires_delta or timedelta(minutes=self.expiry_minutes)
        )

        to_encode.update({"exp": expire})

        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    # =========================
    # TOKEN DECODE
    # =========================
    def decode_token(self, token: str) -> Optional[dict]:
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except JWTError:
            return None

    # =========================
    # CURRENT USER (LIGHT VERSION)
    # =========================
    def get_current_user(
        self,
        token: Annotated[str, Depends(oauth2_scheme)],
    ) -> dict:
        payload = self.decode_token(token)

        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        username = payload.get("sub")
        user_id = payload.get("id")
        email = payload.get("email")

        if not username or not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )

        return {
            "username": username,
            "user_id": user_id,
            "email": email,
        }


# =========================
# Singleton Instance
# =========================
auth_dependency = AuthDependency()