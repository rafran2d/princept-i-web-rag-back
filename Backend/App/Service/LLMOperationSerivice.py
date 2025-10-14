from App.Service.Embedding_service import read_embedding
from App.Service.Chunk_service import read_chunk
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
- Use more information from items with higher contextual relevance and less from lower-ranked items.

2. Data presence check
- If the topic of the question does not match the content of the provided data, respond in the same language as the question: 
  'The submitted documents do not contain information about the topic mentioned in the question.'
- Do not fabricate, guess, or infer answers when the needed information is absent.

3. Input structure
- Each input item contains: { content, meta_data }
- Use `content` to answer the question.
- Use `meta_data` for source identification (document name and page/chunk index).
- Only include relevant content and sources.

4. References and source listing
- List all sources used at the bottom of the response.
- Don’t repeat sources and provide only the document name.
- Mention only the documents and concerned pages if given.
- Use the format: Document: [document name]
- Include only pages/paragraphs actually relevant to your answer.

5. Structure of the output
5.1 Headings
- Use '#' for main titles, '##' for subtitles, '###' for sub-subtitles, etc.
- Headings should summarize the following section clearly.

5.2 Paragraphs
- Write clear and detailed explanations for each point.

5.3 Lists
- Use '-' for unordered lists and '1.' for ordered lists.
- Each item should contain only one idea.

5.4 Tables
- Use Markdown table format if a table is needed:
    ```
    | Column 1 | Column 2 | Column 3 |
    |----------|----------|----------|
    | Value1   | Value2   | Value3   |
    ```
- Include only relevant rows and columns.

6. Response format and quality
- Structure answers professionally, like a short technical document.
- Provide step-by-step explanations when helpful.
- Avoid raw, unstructured text dumps.

7. Behavior and tone
- Answer only the question asked.
- Respond in the same language as the question.
- Use a professional tone; avoid emojis and personal comments.

8. Safety and accuracy
- If the provided data is ambiguous or incomplete, state it and cite only relevant parts.
- Never invent facts or attribute unsupported claims to the sources.
"""

async def chunk_embedding(question : str) -> list[float] :
    """
    Generate an embedding vector for a given question using OpenAI's embeddings API.

    Args:
        question (str): The question text to embed.

    Returns:
        list[float]: Embedding vector representing the question.
    
    Raises:
        Exception: If the embedding generation fails.
    """
    try :
        json_response = await client.embeddings.create(model="text-embedding-3-small",input=question)
        vector = json_response.data[0].embedding
        
        return vector
    
    except Exception as e :
        raise


async def generating_response(question: str, chat_id: uuid.UUID) -> str :
    """
    Generate a response from the LLM based on the user's question and relevant document chunks.

    Steps:
    1. Generate embedding for the question.
    2. Retrieve relevant embeddings from the database.
    3. Fetch corresponding document chunks.
    4. Compile input with prompt, instructions, data, and sources.
    5. Call LLM to generate the response.

    Args:
        question (str): The user's question.
        chat_id (uuid.UUID): The chat session identifier to fetch relevant embeddings.

    Returns:
        str: Generated response from the LLM.
        list[str]: List of document sources used to answer the question.

    Raises:
        Exception: If an error occurs during the response generation process.
    """
    try :
        datas = []
        sources = []
        question_vector = await chunk_embedding(question)#Generate embedding for the question
        embedding_list = await read_embedding(question_vector, chat_id)#retrive all the embedding that is conserned
        embedding_ids =  [embedding.document_chunk_id for embedding in embedding_list]
        chunks = await read_chunk(embedding_ids)#Get the chunks linked to the embeddings
        for chunk in chunks : 
            datas.append({
                "content": chunk.chunk_content,
                "meta_data": chunk.meta_data
            })

            file_name = chunk.meta_data.get("file_name")

            if file_name and file_name not in sources :
                sources.append(file_name)

        input_text = (
            prompt + "\n"
            + f"Datas : {datas}\n"
            + f"Sources : {sources}\n"
            + f"Instructions : {instruction}\n"
            + f"Question : {question}"
        )

        response = await client.responses.create(
            model="gpt-5",
            input=input_text
        )

        return response.output_text, sources

    except Exception as e :
        raise Exception(f"Error during the response generation process: {e}")
