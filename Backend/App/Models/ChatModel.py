from ..database import Base
from .ChatMessageModel import ChatMessageModel
from .DocumentModel import DocumentModel
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
import datetime

class ChatModel(Base):
    __tablename__ = "chats"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    message: Mapped[list[ChatMessageModel]] = relationship("ChatMessageModel", backref="chat", cascade="all, delete-orphan")
    document: Mapped[list[DocumentModel]] = relationship("DocumentModel", backref="chat", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"Chat(id={self.id}, user_id={self.user_id}, title={self.title}, created_at={self.created_at}, updated_at={self.updated_at})"
