from App.database import AsyncSessionLocal
from App.Models.DocumentChunkModel import DocumentChunkModel

async def create_chunk(document_id,chunk_index,chunk):

    async with AsyncSessionLocal() as session:
        async with session.begin(): 
                new_chunk = DocumentChunkModel(
                    document_id=document_id,
                    chunk_index=chunk_index,
                    chunk_content=chunk.text,
                    meta_data=chunk.metadata
                )
                session.add(new_chunk)

    return new_chunk.id