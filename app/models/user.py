from datetime import datetime, UTC
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class UserBase(SQLModel):
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    full_name: Optional[str] = None
    is_active: bool = True

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    
    analyses: List["Analysis"] = Relationship(back_populates="user")

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    created_at: datetime
