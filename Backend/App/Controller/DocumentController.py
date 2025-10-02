from App.Schema.DocumentSchema import (DocumentCreate,DocumentRead)
from pydantic import ValidationError
from typing import List
import uuid
from App.Service.Document_service import (
    load_file_from_uploads,
    delete_file_from_uploads,
    add_metadata_to_docs,
    create_document,
    )
from App.Exception.IngestionException import (
    SaveDocumentError,
    UnsupportedFileTypeError,
    AddMetadataError
)

async def upload_documents(chatid : uuid.UUID) -> List[DocumentRead]:
    try:
        documents = load_file_from_uploads()
        #delete_file_from_uploads()
        documents_input =add_metadata_to_docs(documents,chatid)
        documents_output : List[DocumentRead] = []
        for doc in documents_input:
            doc_obj_return = await create_document(doc)
            documents_output.append(doc_obj_return)
        return documents_output

    except (ValueError, UnsupportedFileTypeError, ValidationError,SyntaxError,TypeError) as e:
        raise AddMetadataError from e
    
    except SaveDocumentError as e:
        raise e

