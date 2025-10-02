from App.database import AsyncSessionLocal 
from App.Models.EmbedingModel import EmbeddingModel
from App.Schema.DocumentChunkSchema import ChunkRead
from App.Schema.EmbeddingShcema import (EmbeddingCreate,EmbeddingRead)
from App.Exception.IngestionException import (
    EmbeddingError,
    SaveEmbeddingError
)
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv
load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("API_KEY"))


async def chunk_embedding(chunk : ChunkRead) -> ChunkRead:
    try:
        json_response = await client.embeddings.create(model="text-embedding-3-small",input=chunk.chunk_content)
        vector = json_response.data[0].embedding
        embedding_dict = {
            "document_chunk_id" : chunk.id,
            "vector" : vector
        }
        embedding_create = EmbeddingCreate(**embedding_dict)
        chunk.embedding = embedding_create
    except ValidationError as e:
        raise EmbeddingError(f"Failed to embedd the following chunk {chunk.id}") from e

async def create_embedding(chunk_input : ChunkRead) -> EmbeddingRead:
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                new_embedding = EmbeddingModel(
                    document_chunk_id = chunk_input.id,
                    vector = chunk_input.embedding
                )
                session.add(new_embedding)
                await session.flush()
                embedding_obj = {
                    "id" : new_embedding.id,
                    "document_chunk_id" : chunk_input.id,
                    "vector" : chunk_input.embedding
                }
                embedding_output = EmbeddingRead(**embedding_output)
                return embedding_output
    except SQLAlchemyError as e:
        raise SaveEmbeddingError(f"Failed to save the following chunk's embedding{chunk_input.id}")
