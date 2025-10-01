from llama_index.core import SimpleDirectoryReader
from App.Models.DocumentModel import DocumentModel
from App.database import AsyncSessionLocal
from App.Schema.DocumentSchema import DocumentCreate, DocumentRead, StatusEnum
from sqlalchemy import select
from docx2pdf import convert
from pathlib import Path
import uuid
import os
import PyPDF2
import tempfile
from typing import List


def get_num_pages_pdf(file_path: str) -> int:
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        return len(reader.pages)


def get_num_pages_docx(file_path: str) -> int:
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True) as tmp_pdf:
        convert(file_path, tmp_pdf.name)
        return get_num_pages_pdf(tmp_pdf.name)


def load_file_from_uploads() -> List:
    target_folder = "App/Data/Uploads"
    return SimpleDirectoryReader(target_folder).load_data()


def delete_file_from_uploads():
    target_folder = "App/Data/Uploads"
    for filename in os.listdir(target_folder):
        file_path = os.path.join(target_folder, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)


def add_metadata_to_docs(documents, chat_id: uuid.UUID) -> List[DocumentCreate]:
    try:
        docs: List[DocumentCreate] = []
        for doc in documents:
            file_name = doc.metadata.get('file_name')
            if not file_name:
                raise ValueError("Document missing file_name in metadata")
            file_path = doc.metadata.get('file_path')
            if not file_path:
                raise ValueError("Document missing file_path in metadata")
            file_ext = file_name.split('.')[-1].lower()
            doc.metadata["file_extension"] = file_ext
            if file_ext == "pdf":
                doc.metadata['num_pages'] = get_num_pages_pdf(file_path)
            elif file_ext == "docx":
                doc.metadata['num_pages'] = get_num_pages_docx(file_path)
            else:
                raise Exception(f"Type de fichier non supporté: {file_ext}")
            doc_data = {
                "chat_id": chat_id,
                "text": doc.text,
                "meta_data": doc.metadata,
            }
            new_doc = DocumentCreate(**doc_data)
            docs.append(new_doc)
        return docs
    except Exception as e:
        raise e


async def create_document(document: DocumentCreate) -> DocumentRead:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            doc_title = Path(document.meta_data.get('file_name', '')).stem
            new_document = DocumentModel(
                chat_id=document.chat_id,
                title=doc_title,
                text=document.text,
                meta_data=document.meta_data
            )
            session.add(new_document)
            await session.flush()
            return DocumentRead.from_orm(new_document)


async def update_document_status(document_id: uuid.UUID, new_status: StatusEnum):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            stmt = select(DocumentModel).where(DocumentModel.id == document_id)
            result = await session.execute(stmt)
            document_obj = result.scalars().first()
            if not document_obj:
                raise Exception(f"Document id {document_id} not found")
            document_obj.status = new_status
            await session.commit()



async def set_chunked_document(document_id: uuid.UUID):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            stmt = select(DocumentModel).where(DocumentModel.id == document_id)
            result = await session.execute(stmt)
            document_obj = result.scalars().first()
            if not document_obj:
                raise Exception(f"Document id {document_id} not found")
            if document_obj.status == StatusEnum.uploaded:
                document_obj.status = StatusEnum.chunked
                await session.commit()
            elif document_obj.status == StatusEnum.failed:
                raise Exception("documents uploading failed")
            else:
                raise Exception(f"Document id {document_id} in unexpected status: {document_obj.status}")


async def set_ready_document(document_id: uuid.UUID):
    await update_document_status(document_id, StatusEnum.ready)


async def set_document_failed(document_id: uuid.UUID):
    await update_document_status(document_id, StatusEnum.failed)
