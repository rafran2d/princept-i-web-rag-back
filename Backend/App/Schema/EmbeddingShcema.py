from pydantic import BaseModel
import uuid


class EmbeddingCreate(BaseModel):
    document_chunk_id : uuid.UUID
    vector : list[float]

    class Config:
        from_attributes = True

class EmbeddingRead(BaseModel):
    id : uuid.UUID
    document_chunk_id : uuid.UUID
    vector : list[float]

    class Config:
        orm_mode = True