from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from App.database import Base
from datetime import datetime, timedelta
from dotenv import load_dotenv
import uuid
import os

load_dotenv()

REFRESH_TOKEN_EXPIRES_AT  = int(os.getenv("REFRESH_TOKEN_EXPIRES_DAYS"))


class RefreshTokenModel(Base):
    __tablename__ ="refresh_tokens"
    
    id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4,primary_key=True)
    user_id: Mapped[uuid.uuid4] = mapped_column(ForeignKey("users.id"),nullable=False) 
    hashed_token:Mapped[str] = mapped_column(nullable=False)
    revoked: Mapped[bool] = mapped_column(nullable=False,default=False)
    expires_at: Mapped[datetime] = mapped_column(
    nullable=False,
    default=lambda: datetime.now() + timedelta(days=REFRESH_TOKEN_EXPIRES_AT)
)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    def __repr__(self) -> str:
        return (
            f"<RefreshToken(id={self.id}, user_id={self.user_id}, revoked={self.revoked}, "
            f"expires_at={self.expires_at}, created_at={self.created_at})>"
        )