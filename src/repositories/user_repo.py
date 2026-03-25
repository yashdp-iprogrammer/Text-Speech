from sqlmodel import Session, select
from src.Database.models import User


class UserRepository:

    def __init__(self, session: Session):
        self.session = session

    async def get_user_by_email(self, email: str) -> User | None:
        # logger.info(f"In Auth Repository checking user for email {email}")
        try:
            statement = select(User).where(User.email == email, User.is_disabled == False)

            result = await self.session.exec(statement)
            user = result.one_or_none()

            # if user:
            #     # logger.info(f"User found for email: {email}")
            # else:
                # logger.warning(f"No user found for email: {email}")

            return user

        except Exception as e:
            # logger.exception(f"Failed to check user: {e}")
            return None

    async def create(self, user: User):
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user