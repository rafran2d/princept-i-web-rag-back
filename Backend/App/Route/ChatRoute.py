from fastapi import APIRouter, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect
from App.Controller.DocumentChunkController import chunking_management as chunk_step
from App.Controller.DocumentController import upload_documents as document_step
from App.Exception.DocumentException import (DocumentNumberError,NumberPageError)
from App.Schema.DocumentSchema import DocumentRead
from App.Schema.DocumentChunkSchema import ChunkRead
from App.Schema.ChatMessageSchema import MessageInput
from App.Schema.ChatSchema import statusenum
from App.Service.Document_service import (set_ready_document,if_exist as exist_doc)
from App.Service.ChatService import (create_chat_prototype,read_status_chat,increment_num_message)
from App.Service.MessageService import Create_Message
from App.Service.ModelRespons import generating_response
from App.Controller.ChatController import chat_managing
from App.Controller.EmbeddingController import batch_embedding_process 
from typing import List,Dict,Any
import traceback
import uuid
import json

chat_route = APIRouter(
    prefix = "/chat",
    tags=['chat']
)


@chat_route.post("{chat_id}/documents", response_model=List[DocumentRead])
async def document_ingestion(chat_id: uuid.UUID, files: List[UploadFile] = File(...)) -> Dict[str, Any]:
    try:
        await create_chat_prototype(chat_id)
        documents_output: List[DocumentRead] = await document_step(chat_id, files)
        
        if len(documents_output) > 3:
            raise DocumentNumberError("Only 3 documents can be used")
        
        for document in documents_output:
            chunk_list: List[ChunkRead] = await chunk_step(document)
            await batch_embedding_process(chunk_list)
            await set_ready_document(document.id)

        return {
            "status_code": 200,
            "data": documents_output,
            "message": "Documents upload completed"
        }

    except DocumentNumberError as e:
        print(e)
        raise HTTPException(status_code=400, detail=str(e))

    except NumberPageError as e:
        print(e)
        raise HTTPException(status_code=400, detail="Document's page number is more than 150 pages")

    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")


@chat_route.websocket("/{chat_id}/messages")
async def messages_managing(websocket: WebSocket, chat_id: uuid.UUID, user_id: uuid.UUID):
    await websocket.accept()

    try:
        if  await read_status_chat(chat_id) == statusenum.Usable:
            data = await websocket.receive_text()
            message_dict = {
                "chat_id": chat_id,
                "role": "User",
                "content": data
            }
            message_json = MessageInput(**message_dict)
            await Create_Message(message_json)
            await chat_managing(chat_id, user_id, data)

            if exist_doc(chat_id):
                response, sources = await generating_response(data, chat_id)
                response_dict = {
                    "chat_id": chat_id,
                    "role": "LLM",
                    "content": response,
                    "sources": sources
                }
                response_json = MessageInput(**response_dict)
                await Create_Message(response_json)
                await websocket.send_text(json.dumps({
                    "type": "message",
                    "content": response
                }))
            else:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "content": "no file uploaded yet"
                }))

            await increment_num_message(chat_id)

        else:
            await websocket.send_text(json.dumps({
                "type": "error",
                "content": "The client has reached the 30 messages limit"
            }))
            await websocket.close()

    except WebSocketDisconnect:
        print("disconected")

    