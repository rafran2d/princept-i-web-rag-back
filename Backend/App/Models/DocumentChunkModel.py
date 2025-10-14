from ..database import Base
from .EmbedingModel import EmbeddingModel
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from App.Schema.DocumentChunkSchema import ChunkStatus
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Enum as SQLEnum
import uuid

class DocumentChunkModel(Base):
    __tablename__ = "document_chunks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("documents.id"), nullable=False)
    chunk_index: Mapped[int] = mapped_column(nullable=False)
    chunk_content: Mapped[str] = mapped_column(nullable=False)
    state: Mapped[ChunkStatus] = mapped_column(
    SQLEnum(ChunkStatus, name="ChunkStatus", create_type=False),  # <- name exact
    default=ChunkStatus.pending
)
    meta_data: Mapped[dict] = mapped_column(JSONB, nullable=True)

    # Relationships
    embedding: Mapped[list[EmbeddingModel]] = relationship("EmbeddingModel", backref="chunk", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"DocumentChunk(id={self.id}, document_id={self.document_id}, chunk_index={self.chunk_index})"