from pydantic import BaseModel
from .ChatMessageSchema import MessageCreate
from .DocumentSchema import DocumentRead
import uuid
import datetime


class ChatCreate(BaseModel):
    user_id : uuid.UUID
    title : str | None = None
    message : MessageCreate

class ChatRead(BaseModel):
    id : uuid.UUID
    user_id : uuid.UUID
    title : str
    created_at : datetime.datetime
    updated_at : datetime.datetime
    document : list[DocumentRead]

class Config:
    from_attributes = True