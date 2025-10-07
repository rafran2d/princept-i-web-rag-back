from llama_index.core import SimpleDirectoryReader
from App.Models.DocumentModel import DocumentModel
from App.Models.UserModel import UserModel# TEMPORARY NEEDED
from App.database import AsyncSessionLocal
from App.Schema.DocumentSchema import DocumentCreate, DocumentRead, StatusEnum
from App.Exception.IngestionException import (SaveDocumentError,UpdateDocumentStatusError,UnsupportedFileTypeError,DocumentFailedError)
from App.Exception.DocumentException import (DocumentReadError,NumberPageError)
from sqlalchemy.exc import SQLAlchemyError
from docx import Document as DocxDocument
from sqlalchemy import select
from docx2pdf import convert
from pathlib import Path
from fastapi import UploadFile
import unicodedata
import re
import uuid
import os
import PyPDF2
import tempfile
from typing import List
import aiofiles

#-------crud------------
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

async def read_document(chat_id : uuid.UUID ) -> List[DocumentRead]:
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                stmt = select(DocumentModel).where(DocumentModel.chat_id == chat_id)
                result = await session.execute(stmt)
                documents = result.scalars().all()

                return [DocumentRead.from_orm(doc) for doc in documents]

    except Exception as e :
        raise DocumentReadError(f"Error while Reading documents.Cause : {e}")

async def read_document_id(id : uuid.UUID):
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                stmt = select(DocumentModel).where(DocumentModel.id == id)
                result = await session.execute(stmt)
                document = result.scalars().first()

                return DocumentRead.from_orm(document)

    except Exception as e :
        raise DocumentReadError(f"Error while Reading documents.Cause : {e}")

#--------- ofhter functions ------


def get_num_pages_pdf(file_path: str) -> int:
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        num_pages = len(reader.pages)
        if num_pages > 150:
            raise NumberPageError(f"{file_path} has more than 150 pages ({num_pages})")
        return num_pages



def get_num_pages_docx(file_path: str) -> int:
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_pdf:
            convert(file_path, tmp_pdf.name)
            num_pages = get_num_pages_pdf(tmp_pdf.name)
        return num_pages
    finally:
        if os.path.exists(tmp_pdf.name):
            os.remove(tmp_pdf.name)


def extract_text_pdf(file_path: Path) -> str:
    text = ""
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text

def extract_text_docx(file_path: Path) -> str:
    doc = DocxDocument(file_path)
    return "\n".join([p.text for p in doc.paragraphs])


def load_file_from_uploads(target_folder: Path = Path("App/Data/Uploads")) -> List[dict]:
    Documents = []
    try:
        for file_path in target_folder.iterdir():
            if file_path.is_file():
                ext = file_path.suffix.lower()
                
                if ext == ".pdf":
                    text = extract_text_pdf(file_path)
                    text = clean_text(text)
                elif ext == ".docx":
                    text = extract_text_docx(file_path)
                    text = clean_text(text)
                else:
                    raise UnsupportedFileTypeError(f"Document type not supported: {ext}")
                
                doc_dict = {
                    "text": text,
                    "file_extension": ext,
                    "file_name": file_path.name,
                    "file_path": file_path
                }
                Documents.append(doc_dict)
        return Documents
    except Exception as e:
        raise e

def delete_file_from_uploads():
    target_folder = "App/Data/Uploads"
    for filename in os.listdir(target_folder):
        file_path = os.path.join(target_folder, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

def clean_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"[\x00-\x1F\x7F-\x9F\u2000-\u206F\u2E00-\u2E7F\uF000-\uFFFF]", " ", text)
    text = text.replace("\n", " ").replace("\r", " ")
    text = re.sub(r"\s+", " ", text)
    text = text.strip()

    return text

async def charge_document_uploads_directory(files: List[UploadFile]):
    try:
        target_folder = "App/Data/Uploads"
        os.makedirs(target_folder, exist_ok=True)
        for file in files:
            file_path = os.path.join(target_folder, file.filename)
            async with aiofiles.open(file_path, "wb") as f:
                content = await file.read()
                await f.write(content)
    except Exception as e:
        raise e



async def if_exist(chat_id : uuid.UUID) -> bool:
    documents = await read_document(chat_id)
    if not documents:
        return False
    else : 
        return True



def add_metadata_to_docs(documents, chat_id: uuid.UUID) -> List[DocumentCreate]:
    docs: List[DocumentCreate] = []
    
    for doc in documents:
        try:
            text = doc['text']
            file_name = doc["file_name"]
            file_ext = doc["file_extension"]
            file_path = doc["file_path"]
            
            if file_ext == ".pdf":
                num_pages = get_num_pages_pdf(file_path)
            elif file_ext == ".docx":
                num_pages  = get_num_pages_docx(file_path)
            else:
                raise UnsupportedFileTypeError(f"Document type not supported: {file_ext}")
            
            doc_data = {
                "chat_id": chat_id,
                "text": text,
                "meta_data": {
                    "file_name": file_name,
                    "file_ext":file_ext,
                    "num_pages":num_pages
                },
            }
            
            new_doc = DocumentCreate(**doc_data)
            docs.append(new_doc)

        except NumberPageError as e :
            raise NumberPageError(f"Doc : {file_name} has more than 150 pages") 
        
        except Exception as e:
            raise 

    return docs



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


# ---------temporary function (ti will be deleted soon)---------------

async def get_user_prototype():
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                stmt = select(UserModel)
                resultUser = await session.execute(stmt)
                User_obj = resultUser.scalars().first()

                return User_obj
    except Exception as e:
        raise            