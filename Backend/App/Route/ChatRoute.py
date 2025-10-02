from fastapi import APIRouter, HTTPException, UploadFile, File
from App.Controller.DocumentChunkController import chunking_management as chunk_step
from App.Controller.DocumentController import upload_documents as document_step
from App.Schema.DocumentSchema import DocumentRead
from App.Schema.DocumentChunkSchema import ChunkRead
from App.Service.Document_service import (set_ready_document,set_document_failed)
from App.Controller.EmbeddingController import batch_embedding_process 
from typing import List,Dict,Any
import uuid


chat_route = APIRouter(
    prefix = "/chat",
    tags=['chat']
)

@chat_route.post("{chat_id}")

@chat_route.post("{chat_id}/documents",response_model=DocumentRead)
async def documemt_ingestion(chat_id : uuid.UUID, files : List[UploadFile] = File(...)) -> Dict[str,Any]:
    try:
        documents_output : List[DocumentRead] = await document_step(chat_id)
        for document in documents_output:
            chunk_list : List[ChunkRead] = await chunk_step(document)
            batch_embedding_process(chunk_list)
            set_ready_document(document.id)
        return {
            "status_code" : 200,
            "data" : documents_output,
            "message" : "Documents upload completed"
        }
    except Exception as e:
        raise HTTPException(status_code = 500, detail=f"Erreur serveur:{str(e)}") from e
    