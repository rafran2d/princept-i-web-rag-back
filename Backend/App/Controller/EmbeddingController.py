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
            chunk_output = await chunk_embedding(chunk)
            embedding_output = await create_embedding(chunk_output)
            
            return embedding_output
        
        except (SaveEmbeddingError,EmbeddingError) as e:
            if attempt <= MAX_RETRIES:
                await asyncio.sleep(2)            
            else:
                raise e
            
async def batch_embedding_process(chunks: List[ChunkRead]) :
    try:
        for i in range(0,len(chunks,BATCH_SIZE)):
            batch = chunks[i:i + BATCH_SIZE]
            tasks = [simple_embedding_process(chunk) for chunk in batch]
            await asyncio.gather(*tasks, return_exceptions=True)
    except (SaveEmbeddingError,EmbeddingRead) as e:
        raise e
    
