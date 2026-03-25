from src.Database.models import User
from src.repositories.user_repo import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.user_repo import UserRepository
from src.utils.hash_util import hash_util
from src.schema.user_schema import UserCreate
from uuid import uuid4


class UserService:

    def __init__(self, session: AsyncSession):
        self.user_repo = UserRepository(session)

    async def register_user(self, user: UserCreate) -> User:
        existing_user = await self.user_repo.get_user_by_email(user.email)

        if existing_user:
            raise ValueError("Email already registered")

        hashed_password = hash_util.get_password_hash(user.password)

        user = User(
            id=uuid4(),
            name=user.name,
            email=user.email,
            password=hashed_password
        )

        return await self.user_repo.create(user)

    