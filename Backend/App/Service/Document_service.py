from llama_index.core import SimpleDirectoryReader
from App.Models.DocumentModel import DocumentModel
from App.database import AsyncSessionLocal
from App.Schema.DocumentSchema import DocumentCreate, DocumentRead, StatusEnum
from App.Exception.IngestionException import (SaveDocumentError,UpdateDocumentStatusError,UnsupportedFileTypeError,DocumentFailedError)
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
from sqlalchemy import select
from docx2pdf import convert
from pathlib import Path
from fastapi import UploadFile
import uuid
import os
import PyPDF2
import tempfile
from typing import List
import aiofiles


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

async def charge_document_uploads_directory(files: List[UploadFile]):
    target_folder = "App/Data/Uploads"
    os.makedirs(target_folder, exist_ok=True)
    for file in files:
        file_path = os.path.join(target_folder, file.filename)
        async with aiofiles.open(file_path, "wb") as f:
            content = await file.read()
            await f.write(content)

def add_metadata_to_docs(documents, chat_id: uuid.UUID) -> List[DocumentCreate]:
    docs: List[DocumentCreate] = []
    
    for doc in documents:
        try:
            file_name = doc.metadata.get('file_name')
            if not file_name:
                raise ValueError("Document missing 'file_name' in metadata")
            
            file_path = doc.metadata.get('file_path')
            if not file_path:
                raise ValueError("Document missing 'file_path' in metadata")
            
            file_ext = file_name.split('.')[-1].lower()
            doc.metadata["file_extension"] = file_ext
            
            if file_ext == "pdf":
                doc.metadata['num_pages'] = get_num_pages_pdf(file_path)
            elif file_ext == "docx":
                doc.metadata['num_pages'] = get_num_pages_docx(file_path)
            else:
                raise UnsupportedFileTypeError(f"Document type not supported: {file_ext}")
            
            doc_data = {
                "chat_id": chat_id,
                "text": doc.text,
                "meta_data": doc.metadata,
            }
            
            new_doc = DocumentCreate(**doc_data)
            docs.append(new_doc)
        
        except (ValueError, UnsupportedFileTypeError, ValidationError,SyntaxError, TypeError) as e:
            raise e

    return docs



async def create_document(document: DocumentCreate) -> DocumentRead:
    try:
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
            
    except (SQLAlchemyError,TypeError,SyntaxError) as e:
        raise SaveDocumentError(f"Failed to create document {document.meta_data.get('file_name')}") from e

async def update_document_status(document_id: uuid.UUID, new_status: StatusEnum):
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                stmt = select(DocumentModel).where(DocumentModel.id == document_id)
                result = await session.execute(stmt)
                document_obj = result.scalars().first()
                if not document_obj:
                    raise Exception(f"Document id {document_id} not found")
                document_obj.status = new_status
                await session.commit()
    except (SQLAlchemyError,TypeError,SyntaxError) as e:
        raise UpdateDocumentStatusError(f'Failed to update status of  document {document_id}') from e



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
                raise DocumentFailedError(f"Document {document_id} failed while being chunked")


async def set_ready_document(document_id: uuid.UUID):
    try:
        await update_document_status(document_id, StatusEnum.ready)
    except UpdateDocumentStatusError as e:
        raise 

async def set_document_failed(document_id: uuid.UUID):
    try:
        await update_document_status(document_id, StatusEnum.failed)
    except UpdateDocumentStatusError as e:
        raise 