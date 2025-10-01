from App.Service.Document_service import (
    get_num_pages_docx,
    get_num_pages_pdf,
    load_file_from_uploads,
    delete_file_from_uploads,
    add_metadata_to_docs,
)
from App.Service.Chunk_service import(
    clean_text,
    chunking,

)

def management():
    