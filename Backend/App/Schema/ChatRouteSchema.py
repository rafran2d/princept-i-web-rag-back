from App.Schema.ChatMessageSchema import MessageOutput
from App.Schema.ChatSchema import ChatOutput
from pydantic import BaseModel
from .DocumentSchema import DocumentRead
from typing import List

class IngestionOutput(BaseModel):
    status_code: int
    data: List[DocumentRead]
    message: str

class LoadConversationOutput(BaseModel):
    status_code : int
    all_messages : List[MessageOutput]
    all_chat : List[ChatOutput]
    message : str