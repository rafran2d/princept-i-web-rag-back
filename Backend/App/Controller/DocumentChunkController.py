from App.Service.Chunk_service import(
    chunking,
    create_chunk,
)

from App.Service.Document_service import (
    set_chunked_document,set_document_failed   
)

async def chunk_documents(documents):
    try:
        for doc in documents:
            if doc.status == "uploaded":
                chunking(doc)
                for chunk,i in enumerate(doc.chunks):
                    chunk.id = await create_chunk(doc.id,i,chunk)
                set_chunked_document(doc)
                return documents
            else:
                raise Exception("Document's upload failed")    
    except Exception as e:
        set_document_failed(doc.id)
        raise e