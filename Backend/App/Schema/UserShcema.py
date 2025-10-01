from pydantic import BaseModel,EmailStr
from enum import Enum
import uuid
import datetime

class RoleEnum(str,Enum):
    admin="admin"
    user='user'

class UserCreate(BaseModel):
    email : EmailStr
    display_name : str
    hashed_password : str
    role : RoleEnum = RoleEnum.user

class UserRead(BaseModel):
    id : uuid.UUID
    email : EmailStr
    display_name : str
    role : RoleEnum
    created_at : datetime.datetime

    class Config:
        from_attributes = True