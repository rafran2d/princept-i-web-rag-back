from App.Models.ChatMessageModel import ChatMessageModel as MessageModel
from App.Schema.ChatMessageSchema import (MessageInput,MessageOutput)
from App.Exception.ChatMessageException import (MessageCreateError,MessageReadError)
from App.database import AsyncSessionLocal
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
import uuid


async def Create_Message(input : MessageInput) -> MessageOutput:
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                message_obj = MessageModel(
                    chat_id =  input.chat_id,
                    role = input.role,
                    content = input.content,
                    sources = input.sources
                )
                session.add(message_obj)
                
                await session.flush()

        return MessageOutput.from_orm(message_obj)
    
    except SQLAlchemyError as e :
        
        raise MessageCreateError(f"Failed to save the message. Cause{e}")
        
async def Read_Message(chat_id: uuid.UUID) -> list[MessageOutput]:
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                stmt = select(MessageModel).where(MessageModel.chat_id == chat_id)
                response = await session.execute(stmt)
                message_objs = response.scalars().all()
                
                return [MessageOutput.from_orm(obj) for obj in message_objs]

    except SQLAlchemyError as e:
        raise MessageReadError(f"Failed to list all messages from {chat_id}. Cause: {e}")
