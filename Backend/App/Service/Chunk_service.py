from llama_index.core.node_parser import TokenTextSplitter, SentenceSplitter
from llama_index.core import Document
from App.Models.DocumentChunkModel import DocumentChunkModel
from App.Schema.DocumentChunkSchema import (ChunkCreate, ChunkRead)
from App.Schema.DocumentSchema import (DocumentRead)
from App.Exception.IngestionException import (ChunkingError, SaveChunkError)
from App.database import AsyncSessionLocal
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from copy import deepcopy
import re

token_splitter = TokenTextSplitter(chunk_size=750, chunk_overlap=75)
sentence_splitter = SentenceSplitter(chunk_size=1000)

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def chunking(document: DocumentRead) -> DocumentRead:
    document.chunks = []
    doc = Document(
        text=document.text,
        metadata=document.meta_data
    )
    nodes = sentence_splitter.get_nodes_from_documents([doc])
    i = 0
    chunk_index = 0
    try:
        while i < len(nodes):
            node = nodes[i]
            element_type = node.metadata.get('element_type', "").lower()

            if element_type == "image":
                i += 1
                continue
            elif element_type == "table":
                node.text = clean_text(node.text)
                chunk = ChunkCreate(
                    document_id=document.id,
                    chunk_index=chunk_index,
                    chunk_content=node.text,
                    meta_data=node.metadata
                )
                chunk_index += 1
                document.chunks.append(chunk)
            elif element_type == "title":
                if i + 1 < len(nodes):
                    next_node = nodes[i + 1]
                    node.text = clean_text(node.text + "\n" + next_node.text)
                    i += 1
                else:
                    chunk = ChunkCreate(
                        document_id=document.id,
                        chunk_index=chunk_index,
                        chunk_content=node.text,
                        meta_data=node.metadata
                    )
                    chunk_index += 1
                    document.chunks.append(chunk)
            else:
                if len(node.text.split()) > 200:
                    sub_nodes = token_splitter.split_text(node.text)
                    for sub_node in sub_nodes:
                        new_node = deepcopy(node)
                        chunk = ChunkCreate(
                            document_id=document.id,
                            chunk_index=chunk_index,
                            chunk_content=sub_node,
                            meta_data=node.metadata
                        )
                        chunk_index += 1
                        document.chunks.append(chunk)
                else:
                    node.text = clean_text(node.text)
                    chunk = ChunkCreate(
                        document_id=document.id,
                        chunk_index=chunk_index,
                        chunk_content=node.text,
                        meta_data=node.metadata
                    )
                    chunk_index += 1
                    document.chunks.append(chunk)
            i += 1
        return document
    except (ValidationError, SyntaxError, TypeError) as e:
        raise ChunkingError(f"Chunking failed for document {document.id}: {e}") from e

async def create_chunk(chunk_input: ChunkCreate) -> ChunkRead:
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                new_chunk = DocumentChunkModel(
                    document_id=chunk_input.document_id,
                    chunk_index=chunk_input.chunk_index,
                    chunk_content=chunk_input.chunk_content,
                    meta_data=chunk_input.meta_data
                )
                session.add(new_chunk)
                await session.flush()
                chunk_output = ChunkRead.from_orm(new_chunk)
        return chunk_output
    except SQLAlchemyError as e:
        raise SaveChunkError(f"Failed to save the chunk. Original error: {e}") from e
    except ValidationError as e:
        raise SaveChunkError(f"Failed to save the chunk: {e}") from e
