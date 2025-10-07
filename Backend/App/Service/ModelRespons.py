from App.Service.Embedding_service import read_embedding
from App.Service.Chunk_service import read_chunk
from App.Service.Document_service import read_document_id
from openai import AsyncOpenAI
from dotenv import load_dotenv
import os
import uuid

load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("API_KEY"))

prompt = """
You are an expert assistant.
Respond to all the question  using all and only the data given bellow.
Strictly follow the instructions below when answering questions.
"""

instruction = """
Instruction for using the provided documents and metadata

1. Data usage
- Only use the data explicitly provided in the input. Do not consult or invent any external information.
- The provided data will be ranked by contextual relevance. Use more information from items with higher relevance and proportionally less from lower-ranked items.

2. Data presence check
- If there is no relevant data among the provided documents, reply exactly:
  "No corresponding context found in the provided documents. Please double-check the submitted documents."
- Do not fabricate, guess, or infer answers when the needed information is absent.

3. Input structure and what to extract
- Each input item is organized and delivered with fields such as:
  id | document | chunk_index | { chunk_content, meta_data }
- Use `chunk_content` as the source of text to answer the question.
- Use `meta_data` to extract source identification (the  document name and the page numbers).
- Only take content from `chunk_content`; only take source identifiers from `meta_data`.

4. References and source listing
- After answering, list all sources used at the bottom of the response.
- Use this recommended format for each source:
  Document: [document name], pages: [numbers]
- If page numbers are not available, use chunk_index or any page/paragraph identifiers available in `meta_data`.
- Include only the pages/paragraphs actually relevant to your answer. Do not list irrelevant files.

5. Response format and quality
- Structure answers clearly and professionally (like a short technical document).
- Provide step-by-step explanations when helpful.
- Avoid raw, unstructured dumps of text. Use headings, short paragraphs, and bullet lists as appropriate.

6. Behavior and tone
- Answer only the question asked.
- Respond in the same language as the question.
- Use a professional tone; do not use emojis.
- Do not add personal comments, unsolicited suggestions, or off-topic content.

7. Safety and accuracy
- If the provided data is ambiguous or incomplete for the user’s request, say so and cite only the relevant parts of the provided data.
- Never invent facts or attribute unsupported claims to the sources.
"""

async def chunk_embedding(question : str) -> list[float]:
    try:
        json_response = await client.embeddings.create(model="text-embedding-3-small",input=question)
        vector = json_response.data[0].embedding
        
        return vector
    
    except Exception as e:
        raise



async def generating_response(question: str, chat_id: uuid.UUID) -> str:
    try:
        datas = []
        sources = []
        vector = await chunk_embedding(question)
        embeddings = await read_embedding(vector, chat_id)

        for embedding in embeddings:
            chunk = await read_chunk(embedding.document_chunk_id)
            datas.append({
                "id": str(chunk.id),
                "chunk_index": chunk.chunk_index,
                "content": chunk.chunk_content,
                "meta_data": chunk.meta_data
            })

            file_name = chunk.meta_data.get("file_name")
            if file_name and file_name not in sources:
                sources.append(file_name)

        input_text = (
            prompt + "\n"
            + f"Datas : {datas}\n"
            + f"Sources : {sources}\n"
            + f"Instructions : {instruction}"
        )

        response = await client.responses.create(
            model="gpt-5",
            input=input_text
        )

        return response.output_text, sources

    except Exception as e:
        raise Exception(f"Error during the response generation process: {e}")
