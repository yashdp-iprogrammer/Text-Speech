from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, DateTime, func



class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(primary_key=True, index=True)

    name: str
    email: str = Field(index=True, unique=True)
    password: str
    is_disabled: bool = Field(default=False)

    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True))
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )