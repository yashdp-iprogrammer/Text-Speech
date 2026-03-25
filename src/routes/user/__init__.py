from fastapi import APIRouter, HTTPException, Depends
from src.schema.user_schema import UserCreate
from src.services.user_service import UserService
from src.Database import db
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from src.utils.hash_util import hash_util

router = APIRouter(tags=["User APIs"])

def get_user_service(session: AsyncSession = Depends(db.get_session)) -> UserService:
    return UserService(session)

user_session = Annotated[UserService, Depends(get_user_service)]


@router.post("/register")
async def register(user: UserCreate, service: user_session):
    return await service.register_user(user)