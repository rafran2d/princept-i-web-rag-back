from pydantic import BaseModel
from .DocumentChunkSchema import ChunkCreate
from typing import Dict,Any
from enum import Enum
import uuid
import datetime

class StatusEnum(str,Enum):
    uploaded = "uploaded"
    chunked = "chunked"
    ready = "ready"
    failed = "failed"



class DocumentCreate(BaseModel):
    chat_id : uuid.UUID 
    text : str
    meta_data : Dict[str,Any]
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
    chunks : list[ChunkCreate] | None = None
    model_config = {
        "extra": "allow",
        "from_attributes": True,
        "validate_assignment": True
    }


