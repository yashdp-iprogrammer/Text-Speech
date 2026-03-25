# src/services/auth_service.py
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import uuid4
from src.repositories.auth_repo import AuthRepo
from src.Database.models import User
from src.utils.hash_util import PasswordHandler
# from src.security.dependencies import invalidated_tokens
# from src.utils.logger import logger
from src.schema.user_schema import UserCreate
from src.security.o_auth import auth_dependency



class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.auth_repo = AuthRepo(session)
        self.auth_handler = auth_dependency
        self.hash_handler = PasswordHandler()
        # self.invalidated_tokens = invalidated_tokens


    # -------------------- LOGIN --------------------
    async def login(self, form_data: OAuth2PasswordRequestForm) -> dict:
        # Fetch user by email
        print("user email", form_data.email)
        user = await self.auth_repo.get_user_by_email(form_data.email)
        if not user or not self.hash_handler.verify_password(form_data.password, user.password):
            # logger.warning(f"❌ Login failed for {form_data.username}")
            raise HTTPException(status_code=401, detail="Incorrect username or password")

        # Generate tokens
        access_token_expires = timedelta(minutes=self.auth_handler.expiry_minutes)
        print("user_id", user.id)
        access_token = self.auth_handler.create_access_token(
            data={"sub": str(user.name), "id": str(user.id), "email": str(user.email)},  # Ensure sub is string
            expires_delta=access_token_expires
        )

        refresh_token_expires = timedelta(days=7)
        refresh_token = self.auth_handler.create_access_token(
            data={"sub": str(user.name), "id": str(user.id), "email": str(user.email)},  # Ensure sub is string
            expires_delta=refresh_token_expires
        )

        # logger.info(f"✅ Login successful for {form_data.username}")
        return {
            "message": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }


    # -------------------- REFRESH --------------------
    async def refresh_access_token(self, refresh_token: str) -> dict:
        try:
            payload = self.auth_handler.decode_token(refresh_token)
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid refresh token")

            access_token_expires = timedelta(minutes=self.auth_handler.expiry_minutes)
            new_access_token = self.auth_handler.create_access_token(
                data={"sub": user_id}, expires_delta=access_token_expires
            )
            return {
                "access_token": new_access_token,
                "token_type": "bearer"
            }
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid or expired refresh token")


