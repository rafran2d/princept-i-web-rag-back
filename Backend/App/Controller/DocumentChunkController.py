from App.Schema.DocumentSchema import DocumentRead
from App.Schema.DocumentChunkSchema import (ChunkCreate,ChunkRead)
from App.Service.Chunk_service import(
    chunking,
    create_chunk,
)
from typing import List
from App.Service.Document_service import (
    set_chunked_document,  
)

async def chunking_management(document : DocumentRead) -> List[ChunkRead]:
    try:
        input : DocumentRead = chunking(document)
        chunk_output_list : List[ChunkRead] = []
        for chunk in input.chunks:
           new_chunk_output = create_chunk(chunk)
           chunk_output_list.append(new_chunk_output)
        set_chunked_document(input.id)

        return chunk_output_list
    except Exception as e:
        raise e
