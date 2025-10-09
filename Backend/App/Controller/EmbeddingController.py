from App.Service.Embedding_service import batch_embedding_openai, create_embedding
from App.Schema.EmbeddingShcema import EmbeddingRead
from App.Schema.DocumentChunkSchema import ChunkRead
from typing import List
from App.Exception.IngestionException import(
    SaveEmbeddingError,
    EmbeddingError
)



async def batch_embedding_process(chunks: List[ChunkRead], max_parallel = 50) :
    """
    Generate embeddings of the chunks and save them in the database.
    """
    try :
        embedding_input_list = await batch_embedding_openai(chunks)#Store the embedding generated
        embedding_output_list = await create_embedding(embedding_input_list)#Save teh embedding in the DB

        return embedding_output_list
    
    except (SaveEmbeddingError,EmbeddingError) as e : 
        raise
