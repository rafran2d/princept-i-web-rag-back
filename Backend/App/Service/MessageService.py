from App.Models.ChatMessageModel import ChatMessageModel as MessageModel
from App.Schema.ChatMessageSchema import (MessageInput,MessageOutput)
from App.Exception.ChatMessageException import (MessageCreateError,MessageReadError)
from App.database import AsyncSessionLocal
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
import uuid


async def Create_Message(input : MessageInput) -> MessageOutput :
    """
    Save a chat message into the database.

    Args:
        input (MessageInput): Pydantic model containing chat_id, role, content, and sources.

    Returns:
        MessageOutput: Pydantic model representing the saved message.

    Raises:
        MessageCreateError: If the message cannot be saved due to a database error.
    """
    try:
        async with AsyncSessionLocal() as session : #start communication with the db    
            async with session.begin() : #start the conversation

                message_obj = MessageModel(
                    chat_id =  input.chat_id,
                    role = input.role,
                    content = input.content,
                    sources = input.sources
                )
                session.add(message_obj)
                
                await session.flush() #send the modification without commiting yet

        return MessageOutput.from_orm(message_obj)
    
    except SQLAlchemyError as e :
        
        raise MessageCreateError(f"Failed to save the message. Cause{e}")
        
async def Read_Message(chat_id: uuid.UUID) -> list[MessageOutput] :
    """
    Retrieve all messages for a specific chat.

    Args:
        chat_id (uuid.UUID): The ID of the chat to retrieve messages for.

    Returns:
        list[MessageOutput]: A list of Pydantic models representing the messages.

    Raises:
        MessageReadError: If the messages cannot be retrieved due to a database error.
    """
    try: 
        async with AsyncSessionLocal() as session: #start communication with the db 
            async with session.begin() : #start the conversation

                stmt = select(MessageModel).where(MessageModel.chat_id == chat_id)
                response = await session.execute(stmt)
                message_objs = response.scalars().all()#get all the datas as a list of python objects
                
                return [MessageOutput.from_orm(obj) for obj in message_objs]

    except SQLAlchemyError as e :
        raise MessageReadError(f"Failed to list all messages from {chat_id}. Cause: {e}")
