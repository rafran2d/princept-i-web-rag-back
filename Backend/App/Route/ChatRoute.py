from fastapi import APIRouter, HTTPException
from App.Controller.DocumentChunkController import chunking_management as chunk_step
from App.Controller.DocumentController import upload_documents as document_step
from App.Schema.DocumentSchema import DocumentRead
from App.Schema.DocumentChunkSchema import ChunkRead
from App.Service.Document_service import (set_ready_document,set_document_failed)
from App.Controller.EmbeddingController import embedding_management as embedding_step
from typing import List,Dict,Any
import uuid
import logging

chat_route = APIRouter(
    prefix = "/chat",
    tags=['chat']
)

#log the exception
logger = logging.getLogger(__name__)

@chat_route.post("{chat_id}/documents",response_model=DocumentRead)
async def documemt_ingestion(chat_id : uuid.UUID) -> Dict[str,Any]:
    try:
        documents_output : List[DocumentRead] = await document_step(chat_id)
        for document in documents_output:
            chunk_list : List[ChunkRead] = await chunk_step(document)
            for chunk in chunk_list:
                embedding_step(chunk)
            set_ready_document(document.id)
        return {
            "status_code" : 200,
            "data" : documents_output,
            "message" : "Documents upload completed"
        }
    except Exception as e:
        logger.exception("erreur")#to log the exception
        raise HTTPException(status_code = 500, detail=f"Erreur serveur:{str(e)}") from e