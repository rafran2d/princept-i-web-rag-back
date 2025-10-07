from App.Service.Embedding_service import (chunk_embedding, create_embedding)
from App.Schema.EmbeddingShcema import (EmbeddingRead)
from App.Schema.DocumentChunkSchema import ChunkRead
from typing import List
from App.Exception.IngestionException import(
    SaveEmbeddingError,
    EmbeddingError
)
import asyncio

BATCH_SIZE = 10
MAX_RETRIES = 1

async def simple_embedding_process(chunk : ChunkRead) -> List[EmbeddingRead]:
    for attempt in range(1,MAX_RETRIES + 2):
        try:
            print(f"Processing chunk {chunk.chunk_index} from document {chunk.document_id}")
            chunk_output = await chunk_embedding(chunk)
            print(f"Chunk embedded successfully, vector dimension: {len(chunk_output.embedding_vector)}")
            embedding_output = await create_embedding(chunk_output)
            print(f"Embedding saved to database with ID: {embedding_output.id}")

            return embedding_output

        except (SaveEmbeddingError,EmbeddingError) as e:
            print(f"[EMBEDDING ERROR] Attempt {attempt}/{MAX_RETRIES + 1}: {str(e)}")
            if attempt <= MAX_RETRIES:
                await asyncio.sleep(2)
            else:
                raise

async def batch_embedding_process(chunks: List[ChunkRead]) :
    try:
        print(f"Starting batch processing for {len(chunks)} chunks")
        for i in range(0, len(chunks), BATCH_SIZE):
            batch = chunks[i:i + BATCH_SIZE]
            print(f"Processing batch {i//BATCH_SIZE + 1} with {len(batch)} chunks")
            tasks = [simple_embedding_process(chunk) for chunk in batch]
            await asyncio.gather(*tasks, return_exceptions=True)
        print(f"All {len(chunks)} chunks processed successfully")
    except (SaveEmbeddingError,EmbeddingRead) as e:
        print(f"[EMBEDDING ERROR] Batch processing failed: {str(e)}")
        raise

