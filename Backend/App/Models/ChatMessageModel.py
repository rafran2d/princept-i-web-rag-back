from ..database import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship  
from sqlalchemy.dialects.postgresql import JSONB

import uuid
import datetime

class ChatMessageModel(Base):
    __tablename__= "chat_messages"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    chat_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chats.id"), nullable=False)
    role: Mapped[str] = mapped_column(nullable=False)  
    content: Mapped[str] = mapped_column(nullable=False)
    sources: Mapped[dict] = mapped_column(JSONB, nullable=True)  
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow)


    def __repr__(self) -> str:
        return f"ChatMessage(id={self.id}, chat_id={self.chat_id}, sender={self.role}, created_at={self.created_at})"
