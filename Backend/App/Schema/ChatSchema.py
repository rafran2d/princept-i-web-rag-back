from pydantic import BaseModel
from .ChatMessageSchema import MessageInput
from .DocumentSchema import DocumentRead
from .ChatMessageSchema import MessageOutput
from typing import (Optional,List)
import uuid
import datetime


class ChatInput(BaseModel):
    id : uuid.UUID
    user_id : uuid.UUID
    title : Optional[str] = None
    message : Optional[MessageInput] = None

class ChatOutput(BaseModel):
    id : uuid.UUID
    user_id : uuid.UUID
    title : Optional[str] = None
    created_at : datetime.datetime
    updated_at : datetime.datetime
    documents : Optional[List[DocumentRead]] = None
    messages : Optional[List[MessageOutput]] = None
    class Config:
        from_attributes = True

