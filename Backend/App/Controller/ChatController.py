from App.Service.ChatService import (
    create_title,
    update_title_chat,
    read_chat,
    if_exist,
    create_chat
)
from App.Schema.ChatSchema import ChatInput
import uuid

async def chat_managing(chat_id : uuid.UUID,user_id : uuid.UUID,message :str):
    try:
        chat_title = await  create_title(message)
        if await  if_exist(chat_id):
            chat_output = await read_chat(chat_id)
            if chat_output.title == None:
                await update_title_chat(chat_id,chat_title)
        else:
            chat_dict ={
                "id":chat_id,
                "user_id":user_id,
                "title":chat_title
            }
            chatinput  = ChatInput(**chat_dict)
            await create_chat(chatinput)

    except Exception as e:
        raise e

async def document_managing(user_id : uuid.UUID,chat_id : uuid.UUID):
    try:
        if not await if_exist(chat_id):
            chat_dict ={
                "id":chat_id,
                "user_id":user_id,
            }         
            chatinput  = ChatInput(**chat_dict)
            await create_chat(chatinput)
    except Exception as e:
        raise e