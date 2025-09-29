from App.Service.Document_service import (
    load_file_from_uploads,
    delete_file_from_uploads,
    add_metadata_to_docs,
    create_document,
    set_upload_document
    )

async def upload_documents(chatid):
    try:
        documents = load_file_from_uploads()
        documents = add_metadata_to_docs(documents)
        for doc in documents:
            doc.id = create_document(chatid,doc)
            set_upload_document(doc)
        delete_file_from_uploads()
        return documents
    except Exception as e:
        raise Exception("document uploading failed")