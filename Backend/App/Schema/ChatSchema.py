from pydantic import BaseModel
from .DocumentSchema import DocumentRead
from .ChatMessageSchema import MessageOutput
from typing import (Optional,List)
from enum import Enum
import uuid
import datetime

class statusenum(str,Enum):
    Usable = 'Usable'
    Unusable = "Unusable"

class ChatInput(BaseModel):
    id : uuid.UUID
    user_id : uuid.UUID
    title : Optional[str] = None

class ChatOutput(BaseModel):
    id : uuid.UUID
    user_id : uuid.UUID
    title : Optional[str] = None
    num_messages : int 
    status : statusenum
    created_at : datetime.datetime
    updated_at : datetime.datetime
    document : Optional[List[DocumentRead]] = None
    message : Optional[List[MessageOutput]] = None
    class Config:
        from_attributes = True

