from App.Models.ChatModel import ChatModel
from App.Schema.ChatSchema import ChatOutput,ChatInput,statusenum
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
from sqlalchemy.orm import selectinload
from pydantic import ValidationError
from sqlalchemy import select
from openai import AsyncOpenAI
from dotenv import load_dotenv
from datetime import datetime
from typing import Optional
import uuid
import os

load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("API_KEY"))


async def create_chat(chat : ChatInput) -> ChatOutput :
    """
    Creates a new chat entry in the database.
    Args:
        chat (ChatInput): Chat input data containing id, user_id, and title.
    Returns:
        ChatOutput: The created chat object.
    Raises:
        SaveChatError: If there is an error during chat creation.
    """
    try :
        async with AsyncSessionLocal() as session : #start communication with the db
            async with session.begin() : #start the conversation
                new_chat = ChatModel(
                    id = chat.id,
                    user_id=chat.user_id
                )
                session.add(new_chat)
                await session.flush()#get the id without commiting yet
                await session.refresh(new_chat)
                
                chat_created = ChatOutput(
                    id=new_chat.id,
                    user_id=new_chat.user_id,
                    title=new_chat.title,
                    num_messages=new_chat.num_messages,
                    status=new_chat.status,
                    created_at=new_chat.created_at,
                    updated_at=new_chat.updated_at,
                    document=None,
                    message=None
                )
                return chat_created 
    except (SQLAlchemyError, TypeError, SyntaxError, ValidationError) as e :
        raise SaveChatError(f"Failed to create chat. Original error: {e}") from e

async def update_title_chat(chat_id : uuid.UUID, title: str) :
    """
    Updates the title of an existing chat.

    Args:
        chat_id (uuid.UUID): The unique ID of the chat.
        title (str): The new title for the chat.

    Raises:
        UpdateTiltleChatError: If the chat does not exist or update fails.
    """
    try :
        async with AsyncSessionLocal() as session : 
            async with session.begin() : #start the conversation
                stmt = select(ChatModel).where(ChatModel.id == chat_id)# orm querying
                result = await session.execute(stmt)
                chat_obj = result.scalars().first() #transfrom teh first line of data as a python object
                if not chat_obj :
                    raise UpdateTiltleChatError(f"Chat: {chat_id} not found")
                chat_obj.title = title #change teh title value

    except UpdateTiltleChatError:
        raise

    except Exception as e :
        raise UpdateTiltleChatError("Error encountered during the update title process")


async def delete_chat(chat_id : uuid.UUID) :
    """
    Deletes a chat from the database.

    Args:
        chat_id (uuid.UUID): The unique ID of the chat to delete.

    Raises:
        DeleteChatError: If the chat does not exist or deletion fails.
        SQLAlchemyError: If there is a database error.
    """
    try :
        async with AsyncSessionLocal() as session : #start communication with the db
            async with session.begin() : #start the conversation
                stmt = select(ChatModel).where(ChatModel.id == chat_id)
                result = await session.execute(stmt)
                chat_obj = result.scalars().first()
                if not chat_obj :
                    raise DeleteChatError(f"Chat: {chat_id} not found")
                await session.delete(chat_obj)
    except (DeleteChatError, SQLAlchemyError) :
        raise


async def read_status_chat(chat_id : uuid.UUID) -> str :
    """
    Reads the status of a chat.

    Args:
        chat_id (uuid.UUID): The unique ID of the chat.

    Returns:
        str: The status of the chat.

    Raises:
        ReadChatError: If reading the chat status fails.
    """
    try:
        async with AsyncSessionLocal() as session : #start communication with the db
            async with session.begin() : #start the conversation
                stmt = select(ChatModel.status).where(ChatModel.id == chat_id)
                response = await session.execute(stmt)
                status = response.scalars().first()
        return status
    except Exception as e :
        raise ReadChatError(f"Failed to read chat {chat_id}. Cause: {e}")



async def read_chat(chat_id : uuid.UUID)-> ChatOutput :
    """
    Reads a chat by its ID.
    Args:
        chat_id (uuid.UUID): The unique ID of the chat.
    Returns:
        ChatOutput: The chat object retrieved from the database.
    Raises:
        ReadChatError: If reading the chat fails.
    """
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                stmt = (
                    select(ChatModel)
                    .where(ChatModel.id == chat_id)
                    .options(
                        selectinload(ChatModel.document),
                        selectinload(ChatModel.message)
                    )
                )
                response = await session.execute(stmt)
                chat_obj = response.scalars().first()
                
                if not chat_obj:
                    raise ReadChatError(f"Chat {chat_id} not found")
                
                return ChatOutput.from_orm(chat_obj)
                
    except ReadChatError:
        raise
    except Exception as e:
        raise ReadChatError(f"Failed to read chat {chat_id}. Cause: {e}")
    

async def read_chat_list(offset : Optional[datetime], user_id:uuid.UUID,max_returns = 15) -> list[ChatOutput] :
    """
    Reads a list of chats with optional pagination.

    Args:
        offset (Optional[datetime]): The timestamp to start fetching chats from. Defaults to None.
        max_returns (int): Maximum number of chats to return. Defaults to 15.

    Returns:
        list[ChatOutput]: A list of chat objects.

    Raises:
        ReadChatError: If reading the chat list fails.
    """
    try:
        async with AsyncSessionLocal() as session : #start communication with the db
            async with session.begin() : #start the conversation
                if not offset:  # For the initial fetch
                    stmt = select(ChatModel).options(
                        selectinload(ChatModel.message),  # Charge tous les documents liés
                        selectinload(ChatModel.document)    # Charge tous les messages liés
                    ).where(ChatModel.user_id == user_id).order_by(ChatModel.updated_at.desc()).limit(max_returns)
                    response = await session.execute(stmt)
                    chat_list = response.scalars().all()
                else:  # Pagination: return the next 15 messages after the offset
                    stmt = select(ChatModel).where(ChatModel.updated_at < offset).order_by(ChatModel.updated_at.desc()).limit(max_returns)
                    response = await session.execute(stmt)
                    chat_list = response.scalars().all()
        return [ChatOutput.from_orm(chat) for chat in chat_list]
    except Exception as e :
        raise ReadChatError(f"Failed to read chats. Cause: {e}")


async def increment_num_message(chat_id : uuid.UUID, limit_messages = 30) :
    """
    Increments the number of messages in a chat. Freezes chat if limit is reached.

    Args:
        chat_id (uuid.UUID): The unique ID of the chat.
        limit_messages (int): Maximum number of messages allowed before freezing the chat. Defaults to 30.

    Raises:
        IncrementError: If incrementing the message count fails.
    """
    try:
        async with AsyncSessionLocal() as session : #start communication with the db
            async with session.begin() : #start the conversation
                stmt = select(ChatModel).where(ChatModel.id == chat_id)
                response = await session.execute(stmt)
                chat_obj = response.scalars().first()
                chat_obj.num_messages += 1 
                
                if chat_obj.num_messages >= limit_messages :  # If more than the message limit, a chat changes its status into unusable
                    chat_obj.status = statusenum.Unusable # set the chat frozen
                await session.commit()
    except Exception as e :
        raise IncrementError from e


async def create_title(message_content : str) -> str :
    """
    Generates a chat title using OpenAI based on message content.

    Args:
        message_content (str): The message content to generate a title from.

    Returns:
        str: The generated chat title.

    Raises:
        CreateTitleError: If generating the title fails.
    """
    try :
        prompt = f"Create a clear title for a chat from the message between brackets: ({message_content})"  # get the title from an OpenAI service
        response = await client.responses.create(
            model='gpt-5',
            input=prompt
        ) #use the openai service
        return response.output_text
    except Exception as e :
         raise CreateTitleError("Failed to create title for the chat")


async def if_exist(chat_id : uuid.UUID) -> bool :
    """
    Checks if a chat exists in the database.

    Args:
        chat_id (uuid.UUID): The unique ID of the chat.

    Returns:
        bool: True if chat exists, False otherwise.

    Raises:
        Exception: If database query fails.
    """
    try:
        async with AsyncSessionLocal() as session : #start communication with the db
            async with session.begin() : #start the conversation
                stmt = select(ChatModel).where(ChatModel.id == chat_id)
                response = await session.execute(stmt)
                chat_obj = response.scalars().first()
        return chat_obj is not None
    except Exception as e :
        raise e


