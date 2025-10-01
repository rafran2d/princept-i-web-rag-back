from fastapi import FastAPI, HTTPException
from pathlib import Path
import uuid
import shutil

app = FastAPI()

@app.post("/chats/{chat_id}/documents")
async def documemt_ingestion(chat_id : uuid):
    try:

    except Exception as e:
        raise HTTPException(status_code = 500, detail=f"Erreur serveur:{str(e)}")