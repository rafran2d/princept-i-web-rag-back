from App.Service.Embedding_service import batch_embedding_openai, create_embedding
from App.Schema.EmbeddingShcema import EmbeddingRead
from App.Schema.DocumentChunkSchema import ChunkRead
from App.Exception.EmbeddingException import EmbeddingStepError
from typing import List


async def batch_embedding_process(chunks: List[ChunkRead]) -> list[EmbeddingRead]:
    """
    Generate embeddings for a list of document chunks and save them in the database.

    This function performs the following steps:
    1. Generates embeddings for each chunk using OpenAI.
    2. Saves the generated embeddings into the database.
    
    Args:
        chunks (List[ChunkRead]): List of document chunks to embed.
        max_parallel (int, optional): Maximum number of parallel embedding requests. Defaults to 50.
    
    Returns:
        List[EmbeddingRead]: A list of saved embeddings as Pydantic models.
    
    Raises:
        SaveEmbeddingError: If saving embeddings to the database fails.
        EmbeddingError: If embedding generation fails.
    """
    try :
        embedding_input_list = await batch_embedding_openai(chunks) #Store the embedding generated
        embedding_output_list = await create_embedding(embedding_input_list) #Save the embedding in the DB

        return embedding_output_list
    
    except Exception as e: 
        raise EmbeddingStepError(f"Error encountered during the embedding process. Original error {e} ")
