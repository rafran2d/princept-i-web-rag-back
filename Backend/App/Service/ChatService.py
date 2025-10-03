from App.Models.ChatModel import ChatModel
from App.Models.UserModel import UserModel 
from App.Schema.ChatSchema import (ChatOutput,ChatInput)
from App.database import AsyncSessionLocal
from App.Exception.ChatException import (
    SaveChatError,
    UpdateTiltleChatError,
    DeleteChatError
)
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
from sqlalchemy import select
import uuid

async def create_chat_prototype(chat_id : uuid.UUID) -> ChatOutput : 
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                stmt = select(UserModel)
                response = await session.execute(stmt)
                user = response.scalars().first()
                new_chat = ChatModel(
                    id = chat_id,
                    user_id=user.id,
                    title="first chat"
                )
                session.add(new_chat)
                await session.flush()
                chat_created = ChatOutput.model_validate(new_chat)
                return chat_created
    except (SQLAlchemyError, TypeError, SyntaxError, ValidationError) as e:
        raise SaveChatError(f"Failed to create chat. original error:{e}") from e   

async def create_chat(chat : ChatInput) -> ChatOutput:
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                new_chat = ChatModel(
                    id = chat.id,
                    user_id=chat.user_id,
                    title=chat.title
                )
                session.add(new_chat)
                await session.flush()
                chat_created = ChatOutput.model_validate(new_chat)
                return chat_created
    except (SQLAlchemyError, TypeError, SyntaxError, ValidationError) as e:
        raise SaveChatError(f"Failed to create chat. original error:{e}") from e

async def update_title_chat(chat_input: ChatOutput, title: str):
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                stmt = select(ChatModel).where(ChatModel.id == chat_input.id)
                result = await session.execute(stmt)
                chat_obj = result.scalars().first()
                if not chat_obj:
                    raise UpdateTiltleChatError(f"Chat:{chat_input.id} not found")
                chat_obj.title = title
                await session.commit()
    except (UpdateTiltleChatError, SQLAlchemyError):
        raise

async def delete_chat(chat_input: ChatOutput):
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                stmt = select(ChatModel).where(ChatModel.id == chat_input.id)
                result = await session.execute(stmt)
                chat_obj = result.scalars().first()
                if not chat_obj:
                    raise DeleteChatError(f"Chat:{chat_input.id} not found")
                await session.delete(chat_obj)
                await session.commit()
    except (DeleteChatError, SQLAlchemyError):
        raise
