from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from App.Controller.DocumentChunkController import chunking_management as chunk_step
from App.Controller.DocumentController import upload_documents as document_step
from App.Exception.DocumentException import DocumentNumberError,NumberPageError
from App.Schema.ChatRouteSchema import IngestionOutput,LoadConversationOutput
from App.Schema.DocumentSchema import DocumentRead
from App.Schema.DocumentChunkSchema import ChunkRead
from App.Schema.ChatMessageSchema import MessageInput,MessageOutput
from App.Schema.ChatSchema import statusenum
from App.Service.Document_service import set_ready_document
from App.Service.ChatService import create_chat_prototype, read_chat_list
from App.Service.MessageService import Read_Message
from App.Controller.EmbeddingController import batch_embedding_process
from typing import List,Optional
from datetime import datetime
import traceback
import uuid

chat_route = APIRouter(
    prefix = "/chat",
    tags=['chat']
)

@chat_route.get("/{chat_id}/messages", response_model=LoadConversationOutput)
async def load_conversation(chat_id : uuid.UUID,offset : Optional[datetime] = Query(None,desciption ="Getter to the offset as a Query params")) -> LoadConversationOutput : 
    """
        This function returns two lists : messages list from the chat wiht the chat_id above and list of all the all the chat stored in the database.
    """
    try :
        Messages : list[MessageOutput] = await Read_Message(chat_id)#list of all the messages
        chats = await read_chat_list(offset)#lst of all chats using pagination
        return LoadConversationOutput(
            status_code=200,
            all_messages= Messages,
            all_chat=chats,
            message="Conversation loaded successfuly"
        )
    except Exception as e : 
        raise HTTPException(status_code=500, detail=str(e))




@chat_route.post("/{chat_id}/documents", response_model=IngestionOutput)
async def document_ingestion(chat_id: uuid.UUID, files: List[UploadFile] = File(...)) -> IngestionOutput :
    try :
        await create_chat_prototype(chat_id)
        documents_output: List[DocumentRead] = await document_step(chat_id, files)

        if len(documents_output) > 3 :
            raise DocumentNumberError("Only 3 documents can be used")

        for document in documents_output :
            chunk_list: List[ChunkRead] = await chunk_step(document)
            await batch_embedding_process(chunk_list)
            await set_ready_document(document.id)

        return IngestionOutput(
            status_code= 200,
            data = documents_output,
            message = "Documents uploaded successfuly"
        )

    except DocumentNumberError as e : 
        print(e)
        raise HTTPException(status_code=400, detail=str(e))

    except NumberPageError as e :
        print(e)
        raise HTTPException(status_code=400, detail="Document's page number is more than 150 pages")

    except Exception as e :
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")



