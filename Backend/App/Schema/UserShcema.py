from pydantic import BaseModel,EmailStr
from enum import Enum
import uuid
import datetime

class RoleEnum(str,Enum):
    admin="admin"
    user='user'

class UserInput(BaseModel):
    email : EmailStr
    display_name : str
    password : str
    role : RoleEnum = RoleEnum.user

class UserOutput(BaseModel):
    id : uuid.UUID
    email : EmailStr
    display_name : str
    role : RoleEnum
    created_at : datetime.datetime

    class Config:
        from_attributes = True