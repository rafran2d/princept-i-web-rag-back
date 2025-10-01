from pydantic import BaseModel
from typing import Dict,Any
from .EmbeddingShcema import EmbeddingCreate
from typing import Optional
import uuid

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
    meta_data : Dict[str,Any]
    embedding : Optional[EmbeddingCreate] = None
    class Config:
        from_attributes = True
