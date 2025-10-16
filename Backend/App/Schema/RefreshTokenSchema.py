from pydantic import BaseModel
from datetime import datetime
import uuid

class RefreshTokenInput(BaseModel):
    user_id: uuid.UUID
    token: str

class RefreshTokenOutput(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    hashed_token: str
    expires_at: datetime
    revoked: bool
    created_at: datetime
    model_config = {
        "from_attributes": True
    }

    