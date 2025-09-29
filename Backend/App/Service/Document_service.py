from llama_index.core import SimpleDirectoryReader
from App.Models.DocumentModel import DocumentModel
from App.database import AsyncSessionLocal 
from sqlalchemy import select
from docx2pdf import convert
from pathlib import Path
import os
import PyPDF2


def get_num_pages_pdf(file_path : str):
    with open(file_path,"rb") as f:
        reader = PyPDF2.PdfReader(f)
        return len(reader.pages)

def get_num_pages_docx(file_path : str):
    base, _ = os.path.splitext(file_path)
    pdf_path = base + ".pdf"
    convert(file_path,pdf_path)
    return get_num_pages_pdf(pdf_path)

def load_file_from_uploads():
    target_folder = "App/Data/Uploads"
    return SimpleDirectoryReader(target_folder).load_data()

def delete_file_from_uploads():
    target_folder = 'App/Data/Uploads'
    for filename in os.listdir(target_folder):
        file_path = os.path.join(target_folder, filename)
        if os.path.isfile(file_path):  
            os.remove(file_path)

def add_metadata_to_docs(documents):
        docs=[]
        for doc in documents:
            doc.metadata["file_extension"] = doc.metadata.get('file_name').split('.')[-1]
            if doc.metadata.get('file_extension') == "pdf":
                doc.metadata['num_pages'] = get_num_pages_pdf(doc.metadata.get('file_path'))
                docs.append(doc)
            elif doc.metadata.get('file_extension') == "docx":
                doc.metadata['num_pages'] = get_num_pages_docx(doc.metadata.get('file_path'))
                docs.append(doc)
            else:
                raise Exception(f"Type de fichier non supporté: {doc.metadata.get('file_extension')}")
        return docs

async def create_document(chatid,document):

    async with AsyncSessionLocal() as session:
        async with session.begin():

            try:
                doc_content = document.text
                doc_metadata = document.metadata
                file_name = doc_metadata.get('file_name','')
                doc_title = Path(file_name).stem
                new_document =  DocumentModel(chat_id=chatid,title=doc_title,content=doc_content,meta_data=doc_metadata)
                session.add(new_document)
                await session.flush()
                return new_document.id
            
            except Exception as e:
                raise e
            

async def set_upload_document(document):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            try:
                stmt = select(DocumentModel).where(DocumentModel.id == document.id)
                result = await session.execute(stmt)
                document_obj = result.scalars().first()
                if document_obj:
                    document_obj.status = "uploaded"
                    await session.commit()
                else:
                    raise Exception(f"Document id {document.id} not found")
            except Exception as e:
                raise e


async def set_chunked_document(document):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            try:
                stmt = select(DocumentModel).where(DocumentModel.id == document.id)
                result = await session.execute(stmt)
                document_obj = result.scalars().first()
                if document_obj.status == "uploaded":
                    document_obj.status = "chunked"
                    await session.commit()
                elif document_obj.status == "failed":
                    raise Exception("documents uploading failed")
                else:
                    raise Exception(f"document id{document.id} not found")

            except Exception as e:
                raise e

async def set_ready_document(document):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            try:
                stmt = select(DocumentModel).where(DocumentModel.id == document.id)
                result = await session.execute(stmt)
                document_obj = result.scalars().first()
                if document_obj:
                    document_obj.status = "chunked"
                    await session.commit()
                elif document_obj.status == "failed":
                    raise Exception("documents chunking failed")
                else:
                    raise Exception(f"Document id {document.id} not found")
            except Exception as e:
                raise e
            
async def set_document_failed(id):
    async with AsyncSessionLocal as session:
        async with session.begin():
            try:
                stmt = select(DocumentModel).where(DocumentModel.id == id)
                result = await session.execute(stmt)
                document_obj = result.scalars().first()
                if document_obj:
                    document_obj.status = "failed"
                    await session.commit()
                else:
                    raise Exception(f"Document id {id} not found")                                

            except Exception as e:
                raise e