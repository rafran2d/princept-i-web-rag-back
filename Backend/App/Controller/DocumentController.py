from App.Schema.DocumentSchema import DocumentRead
from App.Schema.DocumentSchema import StatusEnum
from typing import List
import uuid
from App.Service.Document_service import (
    load_file_from_uploads,
    delete_file_from_uploads,
    add_metadata_to_docs,
    create_document,
    charge_document_uploads_directory,
    compare_hash,
    delete_document,
    read_document_id
)

from fastapi import UploadFile

async def upload_documents(chatid : uuid.UUID, files : List[UploadFile]) -> List[DocumentRead] :
    """
    Handle uploading multiple documents for a given chat.

    This function performs the following steps:
    1. Deletes any existing files in the uploads directory.
    2. Saves the new uploaded files to the uploads directory.
    3. Loads the uploaded files and adds metadata to each document.
    4. Creates the documents in the database.
    
    Args:
        chatid (uuid.UUID): The ID of the chat the documents belong to.
        files (List[UploadFile]): A list of files uploaded by the user.
    
    Returns:
        List[DocumentRead]: A list of created document objects with metadata.
    
    Raises:
        Exception: Propagates any exception raised during the upload or document creation process.
    """
    try :
        delete_file_from_uploads()
        await charge_document_uploads_directory(files)
        documents = load_file_from_uploads()
        documents_input = await add_metadata_to_docs(documents, chatid)
        documents_output : List[DocumentRead] = []

        for doc in documents_input :
            doc_obj_return = await create_document(doc)
            documents_output.append(doc_obj_return)

        return documents_output

    except Exception as e : 
        raise 

    
async def if_already_uploade(files: List[UploadFile], chat_id: uuid.UUID) -> List[UploadFile] :
    """
    Check which files have already been uploaded and delete those whose status is not ready.

    Args:
        files (List[UploadFile]): The list of files to check.
        chat_id (uuid.UUID): The ID of the chat associated with the files.

    Returns:
        List[UploadFile]: A list of files that have not yet been uploaded.

    Notes:
        - For each file, `compare_hash` is called to check if it already exists in the database and returns it.
        - If a file exists but its status is not `StatusEnum.ready`, it is deleted via `delete_document`.
        - Files that do not exist in the database are returned in the result list.
    """
    try :
        new_list: List[UploadFile] = []

        for file in files :
            chunkRead_output = await compare_hash(file, chat_id) #list with attributes hash_key
            if chunkRead_output is not None :

                if chunkRead_output.status != StatusEnum.ready :
                    new_chunkread = await read_document_id(chunkRead_output.id)
                    await delete_document(new_chunkread)
            else:
                new_list.append(file)

        return new_list
    
    except Exception as e :
        raise e