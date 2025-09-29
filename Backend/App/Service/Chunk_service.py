from llama_index.core.node_parser import TokenTextSplitter, SentenceSplitter
from App.Models.DocumentChunkModel import DocumentChunkModel
from App.database import AsyncSessionLocal
from copy import deepcopy
import re

token_splitter = TokenTextSplitter(chunk_size=750, chunk_overlap=75)
sentence_splitter = SentenceSplitter(chunk_size=1000)

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def chunking(document):
    document.chunks = []
    nodes = sentence_splitter.get_nodes_from_documents([document])
    i = 0

    while i < len(nodes):
        node = nodes[i]
        element_type = node.metadata.get('element_type', "").lower()

        if element_type == "image":
            i += 1
            continue

        elif element_type == "table":
            node.text = clean_text(node.text)
            document.chunks.append(node)

        elif element_type == "title":
            if i + 1 < len(nodes):
                next_node = nodes[i + 1]
                node.text = clean_text(node.text + "\n" + next_node.text)
                i += 1
            else:
                node.text = clean_text(node.text)
            document.chunks.append(node)

        else:
            if len(node.text.split()) > 200:
                sub_nodes = token_splitter.split_text(node.text)
                for sub_node in sub_nodes:
                    new_node = deepcopy(node)
                    new_node.text = clean_text(sub_node)
                    document.chunks.append(new_node)
            else:
                node.text = clean_text(node.text)
                document.chunks.append(node)

        i += 1

    return document

async def create_chunk(document_id, chunk):
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                new_chunk = DocumentChunkModel(
                    document_id=document_id,
                    chunk_content=chunk.text,
                    meta_data=chunk.metadata
                )
                session.add(new_chunk)
                await session.flush()  
        return new_chunk.id
    except Exception as e:
        raise e
