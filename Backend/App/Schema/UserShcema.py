from pydantic import BaseModel,EmailStr
from enum import Enum
from typing import Optional
import uuid
import datetime

class RoleEnum(str,Enum):
    admin="admin"
    user='user'

class statususer(str,Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class UserExternalInput(BaseModel):
    email:str
    password:str


class UserInput(BaseModel):
    email : EmailStr
    display_name : Optional[str] = None
    password : str
    role : Optional[RoleEnum] = RoleEnum.user

class UserExternalInputSG(BaseModel):
    email : EmailStr
    display_name : Optional[str] = None
    password : str

class UserInternalOutput(BaseModel):
    id : uuid.UUID
    email : EmailStr
    display_name : str
    role : RoleEnum
    status : statususer 
    hashed_password : str  
    created_at : datetime.datetime

    class Config:
        from_attributes = True

class UserOutput(BaseModel):
    id : uuid.UUID
    email : EmailStr
    display_name : str
    role : RoleEnum
    status : statususer   
    created_at : datetime.datetime

    class Config:
        from_attributes = True