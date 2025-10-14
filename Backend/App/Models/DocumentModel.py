from ..database import Base
from .DocumentChunkModel import DocumentChunkModel
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from App.Schema.DocumentSchema import StatusEnum
import uuid
import datetime

class DocumentModel(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    chat_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chats.id"), nullable=False)
    title: Mapped[str] = mapped_column(nullable=True)
    text: Mapped[str] = mapped_column(nullable=True)
    status : Mapped[StatusEnum] = mapped_column(default = StatusEnum.pending)
    meta_data: Mapped[dict] = mapped_column(JSONB, nullable=True)
    hash_key: Mapped[bytes] = mapped_column(nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow)

    # Relationships
    chunk: Mapped[list[DocumentChunkModel]] = relationship("DocumentChunkModel", backref="document", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"Document(id={self.id}, chat_id={self.chat_id}, title={self.title}, created_at={self.created_at})"