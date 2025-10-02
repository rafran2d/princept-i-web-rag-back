from App.Service.Embedding_service import (chunk_embedding, create_embedding)
from App.Schema.EmbeddingShcema import (EmbeddingCreate,EmbeddingRead)
from App.Schema.DocumentChunkSchema import ChunkRead
from typing import List
from App.Exception.IngestionException import(
    SaveEmbeddingError,
    EmbeddingError
)

async def embedding_management(chunk : ChunkRead) -> List[EmbeddingRead]:
    try:
        chunk_output = await chunk_embedding(chunk)
        embedding_output = await create_embedding(chunk_output)
        
        return embedding_output
    
    except (SaveEmbeddingError,EmbeddingError) as e:
        raise e
        