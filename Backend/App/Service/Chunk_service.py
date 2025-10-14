from llama_index.core.node_parser import TokenTextSplitter, SentenceSplitter
from llama_index.core import Document
from App.Models.DocumentChunkModel import DocumentChunkModel
from App.Schema.DocumentChunkSchema import ChunkCreate, ChunkRead
from App.Schema.DocumentSchema import DocumentRead
from App.Exception.IngestionException import ChunkingError, SaveChunkError
from App.Exception.ChunkException import ReadChunkError
from App.database import AsyncSessionLocal
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
import uuid
import re

token_splitter = TokenTextSplitter(chunk_size=750, chunk_overlap=75)
sentence_splitter = SentenceSplitter(chunk_size=1000)

#__________CRUD___________ 

async def create_chunk(chunk_input: ChunkCreate) -> ChunkRead :
    """
    Creates and saves a document chunk in the database.

    Args:
        chunk_input (ChunkCreate): The chunk data to save.

    Returns:
        ChunkRead: The saved chunk as a read schema.

    Raises:
        SaveChunkError: If saving the chunk fails.
    """
    try :
        async with AsyncSessionLocal() as session : #start communication with the db
            async with session.begin() : #start the conversation
                new_chunk = DocumentChunkModel(
                    document_id=chunk_input.document_id,
                    chunk_index=chunk_input.chunk_index,
                    chunk_content=chunk_input.chunk_content,
                    meta_data=chunk_input.meta_data
                )
                session.add(new_chunk)
                await session.flush() #save the operation without commit so that we get the id
                chunk_output = ChunkRead.from_orm(new_chunk)
        return chunk_output
    except SQLAlchemyError as e :
        raise SaveChunkError(f"Failed to save the chunk. Original error: {e}") from e
    except ValidationError as e :
        raise SaveChunkError(f"Failed to save the chunk: {e}") from e


async def read_chunk(chunk_ids : list[uuid.UUID]) -> list[ChunkRead] :
    """
    Reads chunks from the database by a list of IDs.

    Args:
        chunk_ids (list[uuid.UUID]): List of chunk IDs to retrieve.

    Returns:
        list[ChunkRead]: List of retrieved chunks.

    Raises:
        ReadChunkError: If reading the chunks fails.
    """
    try:
        async with AsyncSessionLocal() as session : #start communication with the db
            async with session.begin() : #start the conversation
                stmt = select(DocumentChunkModel).where(DocumentChunkModel.id.in_(chunk_ids))
                response = await session.execute(stmt)
                chunk_list = response.scalars().all()
                return [
                    ChunkRead.from_orm(chunk) for chunk in chunk_list #change the chunk_list from the db as a list of ChunkRead
                ]
    except Exception as e :
        raise  ReadChunkError(f"Failed to read chunks : Cause : {e}")


#___________other function_____________
#    

def clean_text(text) :
    """
    Cleans a text string by removing extra whitespace.

    Args:
        text (str): The input text.

    Returns:
        str: The cleaned text.
    """
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def chunking(document: DocumentRead) -> DocumentRead :
    """
    Splits a document into chunks based on sentences, tokens, and element types.

    Args:
        document (DocumentRead): The document to chunk.

    Returns:
        DocumentRead: The document with a 'chunks' attribute containing all generated chunks.

    Raises:
        ChunkingError: If chunking fails due to validation or type errors.
    """
    document.chunks = [] #Extra attribute for the document
    doc = Document( #Get the data and change its class from DocumentRead to Document
        text=document.text,
        metadata=document.meta_data
    )
    nodes = sentence_splitter.get_nodes_from_documents([doc]) #Split the doc as a list of (title, table, paragraph, and so on)
    i = 0
    chunk_index = 0 #rank of the nodes in the doc
    try :
        while i < len(nodes) :
            node = nodes[i]
            element_type = node.metadata.get('element_type', "").lower() #Get the node's type

            if element_type == "image": #if image, ignore
                i += 1
                continue

            elif element_type == "table" : #if table, get the table as a chunk
                node.text = clean_text(node.text)
                chunk = ChunkCreate(
                    document_id=document.id,
                    chunk_index=chunk_index,
                    chunk_content=node.text,
                    meta_data=dict(node.metadata)
                )
                chunk_index += 1
                document.chunks.append(chunk)

            elif element_type == "title":
                # Check the next node, if it exists
                if i + 1 < len(nodes):
                    next_node = nodes[i + 1]
                    next_type = next_node.metadata.get('element_type', "").lower()

                    # If the next one is another title → skip for now
                    if next_type == "title":
                        i += 1
                        continue

                    # Otherwise, merge the title with the next node's text
                    node.text = clean_text(node.text + "\n" + next_node.text)
                    i += 1
                else:
                    # If it's the last element, take the title alone
                    node.text = clean_text(node.text)

                # Create a chunk only now
                chunk = ChunkCreate(
                    document_id=document.id,
                    chunk_index=chunk_index,
                    chunk_content=node.text,
                    meta_data=dict(node.metadata)
                )
                chunk_index += 1
                document.chunks.append(chunk)

            else :
                if len(node.text.split()) > 200 : #split the node as a list of subnodes
                    sub_nodes = token_splitter.split_text(node.text)
                    for sub_node in sub_nodes :
                        chunk = ChunkCreate(
                            document_id=document.id,
                            chunk_index=chunk_index,
                            chunk_content=sub_node, 
                            meta_data=dict(node.metadata)
                        )
                        chunk_index += 1
                        document.chunks.append(chunk)
                else : #take it as its own chunk
                    node.text = clean_text(node.text)
                    chunk = ChunkCreate(
                        document_id=document.id,
                        chunk_index=chunk_index,
                        chunk_content=node.text,
                        meta_data=dict(node.metadata)
                    )
                    chunk_index += 1
                    document.chunks.append(chunk)
            i += 1
        return document
    except (ValidationError, SyntaxError, TypeError) as e :
        raise ChunkingError(f"Chunking failed for document {document.id}: {e}")
