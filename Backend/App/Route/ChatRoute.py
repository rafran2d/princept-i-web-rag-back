from fastapi import FastAPI, UploadFile, File
from pathlib import Path
import uuid
import shutil

#import all the necessary function from services and controllers
from App.Service.IngestionDoc import chunking_function as ingest_document
app = FastAPI()

@app.post("/chats/{chat_id}/documents")
async def upload_document(chat_id : uuid.UUID,file: UploadFile = File(...)):
    try:

        target_folder= Path("../Data/Uploads")
        target_folder.mkdir(parents=True, exist_ok=True)
        file_location = target_folder / file.filename
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        chunks = await ingest_document(chat_id)
        
        return {"info": f"file '{file.filename}' uploaded successfully"}
    except Exception as e:
        return{}