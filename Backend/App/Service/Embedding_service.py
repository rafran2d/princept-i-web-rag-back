from App.database import AsyncSessionLocal 
from App.Models.EmbedingModel import EmbeddingModel
from App.Schema.DocumentChunkSchema import ChunkRead
from App.Exception.EmbeddingException import ReadEmbeddingError
from App.Schema.EmbeddingShcema import EmbeddingCreate,EmbeddingRead
from App.Exception.IngestionException import (
    SaveEmbeddingError
)
from sqlalchemy.exc import SQLAlchemyError
from openai import (
    AsyncOpenAI,
    APIError,
    APIConnectionError,
    APITimeoutError,
    RateLimitError

)
from sqlalchemy import text
import uuid
import tiktoken
import os
from dotenv import load_dotenv
import asyncio
load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("API_KEY"))

def get_token_number(chunk : ChunkRead,encod = "cl100k_base") -> int :
    """
    Get the number of tokens in a document chunk.

    Args:
        chunk (ChunkRead): The document chunk to count tokens for.
        encod (str): Encoding type, default is "cl100k_base".

    Returns:
        int: Number of tokens in the chunk.
    """
    encoding = tiktoken.get_encoding(encod)
    return len(encoding.encode(chunk.chunk_content))


async def process_batch(batch: list[ChunkRead], semaphore = asyncio.Semaphore(5) ) -> list[EmbeddingCreate] | None :
    """
    Generate embeddings for a batch of document chunks using OpenAI API.

    Args:
        batch (list[ChunkRead]): List of document chunks to embed.
        semaphore (asyncio.Semaphore): Semaphore to limit parallel API calls.

    Returns:
        list[EmbeddingCreate] | None: List of embeddings for each chunk in the batch.
    """
    async with semaphore :#limit the numbre of task that can be run in parallel
        try :
            response = await client.embeddings.create(
                model="text-embedding-3-small",
                input=[chunk.chunk_content for chunk in batch]
            )
            # for chunk in batch:
            #     chunk.status = Statuschunk.success  # state tracking
            return [
                EmbeddingCreate(document_chunk_id=chunk.id, vector=item.embedding)
                for chunk, item in zip(batch, response.data)
            ]
        except (APIError, APITimeoutError, APIConnectionError, RateLimitError) :
            pass
            # for chunk in batch:
            #     chunk.status = Statuschunk.failed  # state tracking
        except Exception :
            raise Exception

async def batch_embedding_openai(chunks: list[ChunkRead], token_limit=8190) :
    """
    Split chunks into batches respecting a token limit and generate embeddings in parallel.

    Args:
        chunks (list[ChunkRead]): List of document chunks to embed.
        token_limit (int): Maximum number of tokens per batch.

    Returns:
        list[EmbeddingCreate]: Flattened list of embeddings for all chunks.
    """
    try :
        batches = [] #list of all batches
        batch = [] #batch of teh future chunks
        token_count = 0 #number of token of each chunks 
        token_list = [get_token_number(chunk) for chunk in chunks]

        for chunk, token in zip(chunks, token_list) :
            if token_count + token <= token_limit :
                batch.append(chunk)
                token_count += token
            else :
                batches.append(batch)
                batch = [chunk]
                token_count = token
        if batch :
            batches.append(batch)

        # Run task in parallel with gather
        tasks = [process_batch(batch) for batch in batches]
        results = await asyncio.gather(*tasks)

        # flatten
        embeddingcreate_list = [e for result in results for e in result]#take each EmbeddingCreate in each list in the results one by one

        return embeddingcreate_list
    
    except Exception as e :
        raise


async def create_embedding(embeddings: list[EmbeddingCreate]) -> list[EmbeddingRead] : 
    """
    Save a list of embeddings to the database and return them as Pydantic models.

    Args:
        embeddings (list[EmbeddingCreate]): List of embeddings to save.

    Returns:
        list[EmbeddingRead]: List of saved embeddings as Pydantic models.

    Raises:
        SaveEmbeddingError: If saving to the database fails.
    """
    embedding_objects = [
        EmbeddingModel(
            document_chunk_id=embedding.document_chunk_id,
            vector=embedding.vector
        ) for embedding in embeddings
    ]

    try :
        async with AsyncSessionLocal() as session : #start communication with the db
            async with session.begin() : #start the conversation

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
    Retrieve the closest embeddings for a given vector in a specific chat.

    Args:
        vector (list[float]): The query vector.
        chat_id (uuid.UUID): The ID of the chat to filter embeddings.

    Returns:
        list[EmbeddingRead]: List of embeddings as Pydantic models.

    Raises:
        ReadEmbeddingError: If reading embeddings from the database fails.
    """
    try :
        async with AsyncSessionLocal() as session : #start communication with the db
            async with session.begin() : #start the conversation
                # SQL query using raw SQL for vector similarity
                stmt = text("""
                    SELECT e.*
                    FROM embeddings e
                    JOIN document_chunks dc ON e.document_chunk_id = dc.id
                    JOIN documents d ON dc.document_id = d.id
                    JOIN chats c ON d.chat_id = c.id
                    WHERE c.id = :chat_id
                    ORDER BY e.vector <=> (:vector)::vector
                    LIMIT 100
                """)

                # Convert Python list into SQL-compatible pgvector format
                vector_str = f"[{','.join(str(x) for x in vector)}]"

                response = await session.execute(
                    stmt,
                    {
                        "chat_id": str(chat_id),
                        "vector": vector_str  # Pass string instead of list
                    }
                )

                # Get all results as RowMapping objects
                embeddings = response.mappings().all()

                # Convert RowMapping to dict and parse vector as list[float]
                embeddings_list = []
                for emb in embeddings :
                    emb_dict = dict(emb)  # convert RowMapping to mutable dict
                    if isinstance(emb_dict["vector"], str) : 
                        emb_dict["vector"] = [float(x) for x in emb_dict["vector"].strip("[]").split(",")]
                    embeddings_list.append(emb_dict)

        # Return Pydantic models
        return [EmbeddingRead(**embedding) for embedding in embeddings_list]

    except Exception as e :
        raise ReadEmbeddingError(f"Failed to read embeddings: {e}")
