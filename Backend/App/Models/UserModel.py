from ..database import Base
from .ChatModel import ChatModel
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
import datetime

class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[str] = mapped_column(default="user")
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow)

    # Relationships
    chat: Mapped[list[ChatModel]] = relationship("ChatModel", backref="owner", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"User(id={self.id}, email={self.email}, display_name={self.display_name}, role={self.role}, created_at={self.created_at})"
