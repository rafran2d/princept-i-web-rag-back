from App.database import AsyncSessionLocal 
from App.Models.EmbedingModel import EmbeddingModel
from App.Models.ChatModel import ChatModel
from App.Models.DocumentModel import DocumentModel
from App.Models.DocumentChunkModel import DocumentChunkModel
from App.Schema.DocumentChunkSchema import ChunkRead
from App.Exception.EmbeddingException import ReadEmbeddingError
from App.Schema.EmbeddingShcema import (EmbeddingCreate,EmbeddingRead)
from App.Exception.IngestionException import (
    EmbeddingError,
    SaveEmbeddingError
)
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
from openai import AsyncOpenAI
from sqlalchemy import text
import uuid
import os
from dotenv import load_dotenv
load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("API_KEY"))


async def chunk_embedding(chunk : ChunkRead) -> EmbeddingCreate:
    try:
        json_response = await client.embeddings.create(model="text-embedding-3-small",input=chunk.chunk_content)
        vector = json_response.data[0].embedding
        embedding_dict = {
            "document_chunk_id" : chunk.id,
            "vector" : vector
        }
        embedding_create = EmbeddingCreate(**embedding_dict)
        
        return embedding_create
    
    except ValidationError as e:
        raise EmbeddingError(f"Failed to embedd the following chunk {chunk.id}") from e

async def create_embedding(Embedding : EmbeddingCreate) -> EmbeddingRead:
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                new_embedding = EmbeddingModel(
                    document_chunk_id = Embedding.document_chunk_id,
                    vector = Embedding.vector
                )

                session.add(new_embedding)
                await session.flush()
                embedding_output = EmbeddingRead.from_orm(new_embedding)

                return embedding_output
            
    except SQLAlchemyError as e:
        raise SaveEmbeddingError(f"Failed to save the following chunk's embedding{Embedding.document_chunk_id}")
    
async def read_embedding(vector: list[float], chat_id: uuid.UUID) -> list[EmbeddingRead]:
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                stmt = text("""
                    SELECT e.*
                    FROM embeddings e
                    JOIN document_chunks dc ON e.document_chunk_id = dc.id
                    JOIN documents d ON dc.document_id = d.id
                    JOIN chats c ON d.chat_id = c.id
                    WHERE c.id = :chat_id
                    ORDER BY e.vector <=> :vector
                    LIMIT 100
                """)

                response = await session.execute(stmt, {"chat_id": str(chat_id), "vector": vector})
                embeddings = response.scalars().all()

        return [EmbeddingRead.from_orm(embedding) for embedding in embeddings]

    except Exception as e:
        raise ReadEmbeddingError(f"Failed to retrieve data from the db: {e}")