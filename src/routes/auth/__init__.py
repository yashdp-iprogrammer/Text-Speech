from typing import Annotated
from fastapi import APIRouter, Depends, Body
from src.services.auth_service import AuthService
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from src.schema.user_schema import Login, UserCreate
from src.Database import db
from src.security.o_auth import auth_dependency



router = APIRouter(tags=["Auth"])

# Dependency injection
def get_auth_service(session: AsyncSession = Depends(db.get_session)) -> AuthService:
    return AuthService(session)

auth_session = Annotated[AuthService, Depends(get_auth_service)]

# -------------------- ROUTES --------------------
@router.post("/login")
async def login(
    service: auth_session,
    data: Login = Body(...)
    # form_data: OAuth2PasswordRequestForm = Depends()

):
    # Convert to a simple object to mimic OAuth2PasswordRequestForm
    class FormData:
        def __init__(self, email, password):
            self.email = email
            self.password = password

    form_data = FormData(data.email, data.password)
    return await service.login(form_data)



@router.get("/get-current-user")
async def get_current_user(
    current_user = Depends(auth_dependency.get_current_user)
):
    return current_user