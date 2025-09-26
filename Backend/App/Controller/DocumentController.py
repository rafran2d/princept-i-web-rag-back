from pathlib import Path
from App.Models.DocumentModel import DocumentModel
from App.database import AsyncSessionLocal

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