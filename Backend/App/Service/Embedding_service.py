from App.database import AsyncSessionLocal 
from App.Models.EmbedingModel import EmbeddingModel
from App.Schema.DocumentChunkSchema import ChunkRead
from App.Exception.EmbeddingException import ReadEmbeddingError
from App.Schema.EmbeddingShcema import (EmbeddingCreate,EmbeddingRead)
from App.Exception.IngestionException import (
    EmbeddingError,
    SaveEmbeddingError
)
from sqlalchemy.exc import SQLAlchemyError
from openai import AsyncOpenAI
from sqlalchemy import text
import uuid
import tiktoken
import os
from dotenv import load_dotenv
load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("API_KEY"))

def get_token_number(chunk : ChunkRead,encod = "cl100k_base") -> int :
    """
    Get the token number of each chunk
    """
    encoding = tiktoken.get_encoding(encod)
    return len(encoding.encode(chunk.chunk_content))


async def batch_embedding_openai(chunks: list[ChunkRead], token_limit=8190) -> list[EmbeddingCreate] :
    """
    Generate embeddings for a list of chunks using batch processing.
    Returns a list of EmbeddingCreate objects.
    """
    try:
        # Calculate tokens in parallel
        token_list = [get_token_number(chunk) for chunk in chunks]

        embeddingcreate_list = []
        chunk_batch = []
        token_count = 0

        for chunk, token in zip(chunks, token_list) :
            if token_count + token <= token_limit :
                chunk_batch.append(chunk)
                token_count += token
            else:
                # Send the current batch
                response = await client.embeddings.create(
                    model="text-embedding-3-small",
                    input=[c.chunk_content for c in chunk_batch]  # <-- input must be text
                )
                # Match each embedding with its corresponding chunk
                for c, item in zip(chunk_batch, response.data) :
                    embeddingcreate_list.append(
                        EmbeddingCreate(
                            document_chunk_id=c.id,
                            vector=item.embedding
                        )
                    )
                # Reset with the chunk that caused the overflow
                chunk_batch = [chunk]
                token_count = token

        # Flush the last batch
        if chunk_batch :
            response = await client.embeddings.create(
                model="text-embedding-3-small",
                input=[c.chunk_content for c in chunk_batch]
            )
            for c, item in zip(chunk_batch, response.data):
                embeddingcreate_list.append(
                    EmbeddingCreate(
                        document_chunk_id=c.id,
                        vector=item.embedding
                    )
                )

        return embeddingcreate_list

    except Exception as e:
        raise EmbeddingError(f"Exception encountered during embedding generation: {e}")



async def create_embedding(embeddings: list[EmbeddingCreate]) -> list[EmbeddingRead]: 
    """
    Save a list of embeddings in the database and return them as Pydantic models.
    """
    embedding_objects = [
        EmbeddingModel(
            document_chunk_id=embedding.document_chunk_id,
            vector=embedding.vector
        ) for embedding in embeddings
    ]

    try :
        async with AsyncSessionLocal() as session:
            async with session.begin():
                session.add_all(embedding_objects)
                await session.flush()  # flush to get IDs if needed

                # Convert ORM objects to Pydantic
                return [EmbeddingRead.from_orm(obj) for obj in embedding_objects]
            
    except SQLAlchemyError as e :
        raise SaveEmbeddingError(
            f"Failed to save {len(embeddings)} chunk embeddings. Original error: {e}"
        )




async def read_embedding(vector: list[float], chat_id: uuid.UUID) -> list[EmbeddingRead] :
    """
    Simple CRUD function.
    """
    try :
        async with AsyncSessionLocal() as session:
            async with session.begin() :
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

    except Exception as e : 
        raise ReadEmbeddingError(f"Failed to retrieve data from the db: {e}")