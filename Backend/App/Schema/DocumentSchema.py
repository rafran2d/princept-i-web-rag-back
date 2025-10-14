from pydantic import BaseModel
from .DocumentChunkSchema import ChunkRead
from typing import Dict,Any
from enum import Enum
import uuid
import datetime

class StatusEnum(str,Enum):
    pending = "pending"
    charged = "charged"
    chunked = "chunked"
    ready = "ready"
    failed = "failed"



class DocumentCreate(BaseModel):
    chat_id : uuid.UUID 
    text : str
    meta_data : Dict[str,Any]
    hash_key : bytes
    model_config = {
        "extra": "allow",
        "from_attributes": True,
        "validate_assignment": True
    }

class DocumentRead2(BaseModel):
    id : uuid.UUID
    chat_id : uuid.UUID
    title : str
    text : str
    meta_data : Dict[str,Any]
    hash_key : bytes
    model_config = {
        "extra": "allow",
        "from_attributes": True,
        "validate_assignment": True
    }

class DocumentRead(BaseModel):
    id : uuid.UUID
    chat_id : uuid.UUID
    title : str
    text : str
    meta_data : Dict[str,Any]
    created_at : datetime.datetime
    status : StatusEnum
    chunks : list[ChunkRead] | None = None
    model_config = {
        "extra": "allow",
        "from_attributes": True,
        "validate_assignment": True
    }


