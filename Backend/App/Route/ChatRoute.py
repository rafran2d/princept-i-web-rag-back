from App.Controller.DocumentChunkController import chunking_management as chunk_step
from App.Controller.DocumentController import upload_documents as document_step,if_already_uploaded
from App.Exception.EmbeddingException import EmbeddingStepError
from App.Exception.ChunkException import ChunkStepError
from App.Exception.ChatException import UnvailableChatError
from App.Exception.DocumentException import DocumentNumberError, NumberPageError,DocumentDeleteError
from App.Schema.ChatRouteSchema import QuestionInput, IngestionOutput, LoadConversationOutput, MessageManagementOutput
from App.Service.LLMOperationSerivice import generating_response,create_title_chat
from App.Schema.DocumentSchema import DocumentRead , StatusEnum as documentstatus
from App.Schema.DocumentChunkSchema import ChunkRead
from App.Schema.ChatMessageSchema import MessageOutput, MessageInput, SenderEnum
from App.Schema.ChatSchema import statusenum,ChatInput,ChatOutput
from App.Service.Document_service import read_document,delete_all_document,delete_documents_except
from App.Service.ChatService import create_chat, read_chat_list, read_status_chat, increment_num_message,if_exist
from App.Service.States.DocumentContext import DocumentContext
from App.Service.States.FailedState import FailedState
from App.Service.MessageService import Read_Message, Create_Message
from App.Controller.EmbeddingController import batch_embedding_process
from fastapi import APIRouter, HTTPException, UploadFile, File, Query,Request
from fastapi.responses import JSONResponse
from typing import List, Optional
from pydantic import ValidationError
from datetime import datetime
import traceback
import uuid

chat_route = APIRouter(
    prefix="/chat",
    tags=['chat']
)


@chat_route.get("/", response_model=List[ChatOutput])
async def list_chats(offset: Optional[datetime] = Query(None, description="Timestamp for pagination offset")):
    """
    List all chats for the authenticated user.

    Parameters:
    - offset (datetime, optional): Pagination offset for listing chats.

    Returns:
    - List[ChatOutput]: List of all chats with their metadata.

    Raises:
    - HTTPException 500: If any unexpected error occurs while fetching chat list.
    """
    try:
        chats = await read_chat_list(offset)
        return chats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(type(e)) + ": " + str(e))



@chat_route.get("/{chat_id}/messages", response_model=LoadConversationOutput)
async def load_conversation(chat_id: uuid.UUID) -> LoadConversationOutput :
    """
    Load all messages from a specific chat and list all chats in the database.

    Steps:
    1. Retrieve all messages for the chat identified by chat_id.
    2. Retrieve all chats with optional pagination using offset.

    Parameters:
    - chat_id (uuid.UUID): Unique identifier of the chat to load messages from.
    - offset (datetime, optional): Pagination offset for listing chats.

    Returns:
    - LoadConversationOutput: Contains all messages for the chat, list of all chats, status code, and message.

    Raises:
    - HTTPException 500: If any unexpected error occurs while fetching messages or chat list.
    """
    try :
        Messages: list[MessageOutput] = await Read_Message(chat_id)
        return LoadConversationOutput(
            status_code=200,
            data=Messages,
            message="Conversation loaded successfully"
        )
    except Exception as e :
        raise HTTPException(status_code=500,detail=str(type(e))+": "+ str(e))
    
@chat_route.get('/{chat_id}/documents',response_model=List[DocumentRead])
async def load_docs(chat_id : uuid.UUID):
    """
    Load all mentionned chat's documnets

    Parameters:
    - chat_id

    Returns:
    - JSONResponse: contains status_code,datas (the documents)

    Raises:
    - HTTPException 500: Internal servor error
    """

    try:
        docs = await read_document(chat_id)
        
        return docs
    
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(type(e))+": "+ str(e))




@chat_route.post("/{chat_id}/messages", response_model=MessageManagementOutput | dict)
async def message_managing(chat_id: uuid.UUID, payload: QuestionInput) :
    """
    Handle the exchange of messages for a chat.

    Steps:
    1. Check if the chat is usable.
    2. Increment the chat's message count.
    3. Save the user's message to the database.
    4. Generate a response from the LLM.
    5. Save the LLM's response along with sources in the database.

    Parameters:
    - chat_id (uuid.UUID): Unique identifier of the chat.
    - payload (QuestionInput): The user's question message.

    Returns:
    - MessageManagementOutput: Contains the LLM's response, status code, and message.

    Raises:
    - HTTPException 403: If the chat is not usable or validation fails.
    """
    question = payload.message
    try :
        await create_title_chat(payload.message,chat_id)
        if await read_status_chat(chat_id) == statusenum.Usable :
            
            documents = await read_document(chat_id)

            if not documents :
                raise UnvailableChatError(f"The chat: {chat_id} has no document yet")

            for doc in documents :
                if doc.status !=  documentstatus.ready :
                    raise UnvailableChatError(f"All the chat: {chat_id} 's documents are not ready to work with yet")
                
            await increment_num_message(chat_id)
            question_input = MessageInput(
                chat_id=chat_id,
                role=SenderEnum.user,
                content=question,
            )

            await Create_Message(question_input)
            response, sources = await generating_response(question, chat_id)

            message_input = MessageInput(
                chat_id=chat_id,
                role=SenderEnum.LLM,
                content=response,
                sources=sources
            )

            message_output = await Create_Message(message_input)

            return MessageManagementOutput(
                status_code=200,
                response=message_output.content,
                message="Answer generated successfully"
            )
        else :
            return MessageManagementOutput(
                status_code=200,
                message="The chat is not usable yet"
            )

    except UnvailableChatError as e:
        print(type(e))
        print(e)
        raise HTTPException(status_code=503,detail=str(type(e))+": "+ str(e))
    
    except ValidationError as e :
        print(type(e))
        print(e)
        raise HTTPException(status_code=403,detail=str(type(e))+": "+ str(e))
    
    except Exception as e :
        print(type(e))
        print(e)
        raise HTTPException(status_code=500, detail=str(type(e))+": "+ str(e))



@chat_route.post("/{chat_id}/documents", response_model=IngestionOutput)
async def document_ingestion(chat_id: uuid.UUID, request: Request, files: List[UploadFile] = File(...)):
    """
    Handle document ingestion and embedding for a chat.

    Steps:
    1. Validate the number of uploaded documents does not exceed document_limit.
    2. Create a chat prototype if it doesn't exist.
    3. Manage documents.(check if any of the file is already store in the db so no need to upload it again)
    4. Upload documents and store metadata in the database.
    5. Split each document into chunks and store them in the database.
    6. Generate embeddings for each chunk and store them in the database.

    Parameters:
    - chat_id (uuid.UUID): Unique identifier of the chat.
    - files (List[UploadFile]): List of documents to upload.

    Returns:
    - IngestionOutput: Contains status code, uploaded documents data, and a success message.

    Raises:
    - HTTPException 400: If the number of documents exceeds the limit or page number exceeds 150.
    - HTTPException 500: If any unexpected server error occurs during ingestion.
    """
    document_limit: int = 3

    try:

        if len(files) > document_limit:
            raise DocumentNumberError(f"Only {document_limit} documents can be used")
        
        if not await if_exist(chat_id):
            payload = request.state.payload
            chat_input = ChatInput(
                id=chat_id,
                user_id=payload["sub"]
            )
            await create_chat(chat_input)

        new_files_list, ids = await if_already_uploaded(files, chat_id)

        await delete_documents_except(chat_id, ids)
        
        if new_files_list:
            documents_output: List[DocumentRead] = await document_step(chat_id, new_files_list)
            docs_state = [DocumentContext(doc.id) for doc in documents_output]

            for document, state in zip(documents_output, docs_state):
                try:
                    if not isinstance(state.state, FailedState):
                        chunk_list: List[ChunkRead] = await chunk_step(document)
                        await state.involve()
                        await batch_embedding_process(chunk_list)
                        await state.involve()
                except (ChunkStepError, EmbeddingStepError) as e:
                    await state.fail()
                    print(f"Error processing document {document.id}: {e}")
                    raise HTTPException(status_code=400, detail=str(e))
        else:
            documents_output = await read_document(chat_id)

        return IngestionOutput(
            status_code=200,
            data=documents_output,
            message="Documents processed (some may have failed)"
        )

    except (DocumentNumberError, NumberPageError) as e:
        print(e)
        raise HTTPException(status_code=400, detail=str(type(e)) + ": " + str(e))

    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(type(e)) + ": " + str(e))


@chat_route.delete('/{chat_id}/documents')
async def Delete_chat_document(chat_id:uuid.UUID):
    try:
        await delete_all_document(chat_id)
        return JSONResponse(status_code=200,content={"message":"delete successful"})
    except DocumentDeleteError as e:
        raise HTTPException(status_code=500, detail=str(type(e))+": "+ str(e))