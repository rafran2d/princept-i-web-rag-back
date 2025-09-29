from App.database import AsyncSessionLocal 
from App.Models.DocumentChunkModel import DocumentChunkModel
from sqlalchemy import select
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv
load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("API_KEY"))

async def embedding_management(chunk_id):
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():        
                stmt = select(DocumentChunkModel).where(DocumentChunkModel.id == chunk_id)
                response = await session.execute(stmt)
                chunk_obj = response.scalars().first()
                if chunk_obj:
                    document = chunk_obj.document
                    document.status = "ready"
                else:
                    raise Exception(f'chunk id{chunk_id} not found')
    except Exception as e:
        raise e

async def chunk_embedding(chunk : str) -> list[float]:
    try:
        json_response = await client.embeddings.create(model="text-embedding-3-small",input=chunk)
        vector = json_response.data[0].embedding
        return vector
    except Exception as e:
        raise 