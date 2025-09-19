from ..database import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector
import uuid

class EmbeddingModel(Base):
    __tablename__ = "embeddings"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    document_chunk_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("document_chunks.id"), nullable=False)
    vector: Mapped[list[float]] = mapped_column(Vector(1536))

    def __repr__(self) -> str:
        return f"Embeddings(id={self.id}, document_chunk_id={self.document_chunk_id})"