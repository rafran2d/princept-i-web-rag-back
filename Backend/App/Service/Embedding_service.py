from App.database import AsyncSessionLocal 
from App.Models.DocumentChunkModel import DocumentChunkModel
from App.Schema.DocumentChunkSchema import ChunkRead
from App.Schema.EmbeddingShcema import EmbeddingCreate
from sqlalchemy import select
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv
load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("API_KEY"))


async def chunk_embedding(chunk : str) -> list[float]:
    try:
        json_response = await client.embeddings.create(model="text-embedding-3-small",input=chunk)
        vector = json_response.data[0].embedding
        return vector
    except Exception as e:
        raise 