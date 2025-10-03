from pydantic import BaseModel
from enum import Enum
from typing import Optional,Any,Dict
import uuid
import datetime 



class SenderEnum(str,Enum):
    LLM = "LLM"
    user = "User"

class MessageInput(BaseModel):
    chat_id : uuid.UUID
    role : SenderEnum = SenderEnum.user
    content : str
    sources : Optional[Dict[str,Any]] = None

class MessageOutput(BaseModel):
    id : uuid.UUID
    chat_id : uuid.UUID
    role : SenderEnum
    content : str
    sources : Optional[Dict[str,Any]] = None
    created_at : datetime.datetime

    class Config:
        from_attributes = True