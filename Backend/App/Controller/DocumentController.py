from App.Schema.DocumentSchema import DocumentRead
from typing import List
import uuid
from App.Service.Document_service import (
    load_file_from_uploads,
    delete_file_from_uploads,
    add_metadata_to_docs,
    create_document,
    charge_document_uploads_directory,
    )

from fastapi import UploadFile

async def upload_documents(chatid : uuid.UUID,files : List[UploadFile]) -> List[DocumentRead]:
    try:
        delete_file_from_uploads()
        await charge_document_uploads_directory(files)
        documents = load_file_from_uploads()
        documents_input =add_metadata_to_docs(documents,chatid)
        documents_output : List[DocumentRead] = []
        for doc in documents_input:
            doc_obj_return = await create_document(doc)
            documents_output.append(doc_obj_return)
        return documents_output


    except Exception as e:
        raise 

