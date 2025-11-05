from App.Service.ChatService import (
    if_exist,
    create_chat
)
from App.Schema.ChatSchema import ChatInput
import uuid


async def document_managing(user_id : uuid.UUID, chat_id : uuid.UUID) :
    """
    Ensure that a chat exists for the given user and chat ID. 
    Creates a new chat if it does not exist.

    Args:
        user_id (uuid.UUID): The ID of the user associated with the chat.
        chat_id (uuid.UUID): The ID of the chat to check or create.

    Raises:
        Exception: Propagates any exception raised during chat creation.
    """
    try :
        if not await if_exist(chat_id) :
            chat_dict ={
                "id":chat_id,
                "user_id":user_id,
            }         
            chatinput  = ChatInput(**chat_dict)
            await create_chat(chatinput)
    except Exception as e :
        raise e
