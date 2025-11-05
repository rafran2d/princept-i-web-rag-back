from App.Schema.ChatMessageSchema import MessageOutput
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
    data : List[MessageOutput]
    message : str

class MessageManagementOutput(BaseModel):
    status_code : int 
    response : str|None
    message : str

class QuestionInput(BaseModel):
    message : str