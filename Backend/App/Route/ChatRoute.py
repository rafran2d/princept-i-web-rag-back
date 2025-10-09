from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from App.Controller.DocumentChunkController import chunking_management as chunk_step
from App.Controller.DocumentController import upload_documents as document_step
from App.Exception.DocumentException import DocumentNumberError,NumberPageError
from App.Schema.ChatRouteSchema import QuestionInput,IngestionOutput,LoadConversationOutput,MessageManagementOutput
from App.Service.LLMOperationSerivice import generating_response
from App.Schema.DocumentSchema import DocumentRead
from App.Schema.DocumentChunkSchema import ChunkRead
from App.Schema.ChatMessageSchema import MessageOutput,MessageInput,SenderEnum
from App.Schema.ChatSchema import statusenum
from App.Service.Document_service import set_ready_document
from App.Service.ChatService import create_chat_prototype, read_chat_list,read_status_chat,increment_num_message
from App.Service.MessageService import Read_Message,Create_Message
from App.Controller.EmbeddingController import batch_embedding_process
from typing import List,Optional
from pydantic import ValidationError
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


@chat_route.post("/{chat_id}/messages",response_model= MessageManagementOutput|dict)
async def message_managing(chat_id : uuid.UUID,payload : QuestionInput):
    """
    This function manages the information exchange
    """
    question = payload.message
    try :
        if await read_status_chat(chat_id) == statusenum.Usable:
            
            await increment_num_message(chat_id)#Increment the chat's message number
            question_input = MessageInput(
                chat_id=chat_id,
                role = SenderEnum.user,
                content = question,
            )

            await Create_Message(question_input)#save the message in the db
            response,sources = await generating_response(question,chat_id)#send the message to the llm for it to answer

            message_input = MessageInput(
                chat_id = chat_id,
                role = SenderEnum.LLM,
                content = response,
                sources = sources
            )

            message_output = await Create_Message(message_input)# save the llm's answer in the db

            return MessageManagementOutput(
                status_code = 200,
                response= message_output,
                message= "Anwswer generated successfuly"
            )
        else:
            return {
                "error" : "The chat is no longer usable"
            }
        
    except ValidationError as e :       
        raise HTTPException(status_code= 403, detail=f"The Chat is not longer usable : {e}")

        
    except Exception as e :
        raise HTTPException(status_code= 403, detail=f"The Chat is not longer usable{e}")



@chat_route.post("/{chat_id}/documents", response_model=IngestionOutput)
async def document_ingestion(chat_id: uuid.UUID, files: List[UploadFile] = File(...),document_limit = 3)  :
    """
    This function handles all the necessary processes for a document to get embeddings saved in the database.
    """
    try:
        await create_chat_prototype(chat_id)
        documents_output: List[DocumentRead] = await document_step(chat_id, files)  # Add metadata and store each doc into the db

        if len(documents_output) > document_limit:#The list should not contain more than 3 documents 
            raise DocumentNumberError(f"Only {document_limit} documents can be used")

        for document in documents_output:
            chunk_list: List[ChunkRead] = await chunk_step(document)  # Split the documents into chunks and store them in the db
            await batch_embedding_process(chunk_list)  # Generate embeddings for each chunk and store them also
            await set_ready_document(document.id)  # Change the document's status

        return IngestionOutput(
            status_code=200,
            data=documents_output,
            message="Documents uploaded successfully"
        )

    except DocumentNumberError as e:
        print(e)
        raise HTTPException(status_code=400, detail=str(e))

    except NumberPageError as e:
        print(e)
        raise HTTPException(status_code=400, detail="Document's page number exceeds 150 pages")

    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

