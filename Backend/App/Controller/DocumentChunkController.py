from App.Schema.DocumentSchema import DocumentRead
from App.Schema.DocumentChunkSchema import ChunkRead
from App.Service.Chunk_service import(
    chunking,
    create_chunk,
)
from App.Exception.ChunkException import ChunkStepError
from typing import List

async def chunking_management(document : DocumentRead) -> List[ChunkRead] :
    """
    Manage the chunking process for a given document.
    
    This function performs the following steps:
    1. Splits the document into chunks using the `chunking` function.
    2. Creates each chunk in the database via `create_chunk`.
    3. Updates the document status to 'chunked' after all chunks are created.
    
    Args:
        document (DocumentRead): The document to be chunked.
    
    Returns:
        List[ChunkRead]: A list of all created chunk objects.
    
    Raises:
        SaveChunkError: If saving a chunk fails.
        ChunkingError: If the chunking process fails.
        UpdateDocumentStatusError: If updating the document status fails.
    """
    try :
        input : DocumentRead = chunking(document)
        chunk_output_list : List[ChunkRead] = []
        for chunk in input.chunks:
           new_chunk_output = await create_chunk(chunk)
           chunk_output_list.append(new_chunk_output)

        return chunk_output_list
    
    except Exception as e :
        raise ChunkStepError(f"Error encountered during the chunk step process. Orirginal error {e}")
