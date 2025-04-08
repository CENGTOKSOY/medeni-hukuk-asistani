from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    fullname: str

class UserInDB(UserBase):
    hashed_password: str
    disabled: bool = False
    fullname: Optional[str] = None
    created_at: Optional[datetime] = None