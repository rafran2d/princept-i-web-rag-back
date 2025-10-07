from App.Models.ChatModel import ChatModel
from App.Models.UserModel import UserModel 
from App.Schema.ChatSchema import (ChatOutput,ChatInput,statusenum)
from App.database import AsyncSessionLocal
from App.Exception.ChatException import (
    SaveChatError,
    UpdateTiltleChatError,
    DeleteChatError,
    CreateTitleError,
    ReadChatError,
    IncrementError
)
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
from sqlalchemy import select
from openai import AsyncOpenAI
from dotenv import load_dotenv
import uuid
import os

load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("API_KEY"))

#--------- crud ------------

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

async def update_title_chat(chat_id : uuid.UUID, title: str):
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                stmt = select(ChatModel).where(ChatModel.id == chat_id)
                result = await session.execute(stmt)
                chat_obj = result.scalars().first()
                if not chat_obj:
                    raise UpdateTiltleChatError(f"Chat:{chat_id} not found")
                chat_obj.title = title
                await session.commit()
    except (UpdateTiltleChatError, SQLAlchemyError):
        raise


async def delete_chat(chat_id : uuid.UUID):
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                stmt = select(ChatModel).where(ChatModel.id == chat_id)
                result = await session.execute(stmt)
                chat_obj = result.scalars().first()
                if not chat_obj:
                    raise DeleteChatError(f"Chat:{chat_id} not found")
                await session.delete(chat_obj)
                await session.commit()
    except (DeleteChatError, SQLAlchemyError):
        raise

async def read_status_chat(chat_id : uuid.UUID) -> str:
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                stmt = select(ChatModel.status).where(ChatModel.id == chat_id)
                response = await session.execute(stmt)
                status =  response.scalars().first()
        return status
    except Exception as e:
        raise ReadChatError(f"Failed to read chat{chat_id}. Cause :{e}")


async def read_chat(chat_id : uuid.UUID)-> ChatOutput:
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                stmt = select(ChatModel).where(ChatModel.id == chat_id)
                response = await session.execute(stmt)
                chat_obj =  response.scalars().first()
        return ChatOutput.from_orm(chat_obj)
    except Exception as e:
        raise ReadChatError(f"Failed to read chat{chat_id}. Cause :{e}")
    
async def read_chat_list() -> list[ChatOutput]:
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                stmt = select(ChatModel).order_by(ChatModel.created_at).limit(100)
                response = await session.execute(stmt)
                chat_list = response.scalars().all()
        
        return [ChatOutput.from_orm(chat) for chat in chat_list]
    
    except Exception as e:
        raise ReadChatError(f"Failed to read chats. Cause: {e}")
#----------- other features ----------

async def increment_num_message(chat_id : uuid.UUID):
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                stmt = select(ChatModel).where(ChatModel.id == chat_id)
                response = await session.execute(stmt)
                chat_obj =  response.scalars().first()
                chat_obj.num_messages += 1
                if chat_obj.num_messages >= 30:
                    chat_obj.status = statusenum.Unusable
                await session.commit()
    except Exception as e:
        raise  IncrementError from e

async def create_title(message_content : str) -> str:
    try:
        prompt= f"Create a clear title for a chat from the message between brackets : ({message_content})"
        response = await client.responses.create(
            model='gpt-5',
            input = prompt
        )

        return response.output_text
    except Exception as e :
         raise CreateTitleError("Failed to create title for the chat")

async def if_exist(chat_id : uuid.UUID) -> bool:
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                stmt = select(ChatModel).where(ChatModel.id == chat_id)
                response = await session.execute(stmt)
                chat_obj = response.scalars().first()
        return  chat_obj is not None
    except Exception as e:
        raise e

#------- prototype function ----------

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
