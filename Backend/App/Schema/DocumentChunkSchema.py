from pydantic import BaseModel
from typing import Dict,Any
from enum import Enum
import uuid

class ChunkStatus(str,Enum):
    pending = "pending"
    failed = "failed"
    success = "success"

class ChunkCreate(BaseModel):
    document_id : uuid.UUID
    chunk_index : int 
    chunk_content : str
    meta_data : Dict[str,Any]

class ChunkRead(BaseModel):
    id : uuid.UUID
    document_id : uuid.UUID
    chunk_index : int 
    chunk_content : str
    state : ChunkStatus
    meta_data : Dict[str,Any]
    
    class Config:
        from_attributes = True
