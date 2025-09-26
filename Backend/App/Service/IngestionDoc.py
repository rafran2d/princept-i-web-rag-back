from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import TokenTextSplitter, SentenceSplitter
from docx2pdf import convert
from App.Controller.DocumentController import create_document as save_document
from App.Controller.DocumentChunkController import create_chunk as save_chunk
import os
import PyPDF2
import re

def get_num_pages_pdf(file_path):
    with open(file_path,"rb") as f:
        reader = PyPDF2.PdfReader(f)
        return len(reader.pages)

def get_num_pages_docx(file_path):
    base, _ = os.path.splitext(file_path)
    pdf_path = base + ".pdf"
    convert(file_path,pdf_path)
    return get_num_pages_pdf(pdf_path)

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

async def chunking_function(chat_id):
    
    token_splitter = TokenTextSplitter(chunk_size=750, chunk_overlap=75)
    sentence_splitter = SentenceSplitter(chunk_size=1000)
    target_folder = 'App/Data/Uploads'
    documents = SimpleDirectoryReader(target_folder).load_data()
    for filename in os.listdir(target_folder):
        file_path = os.path.join(target_folder, filename)
        if os.path.isfile(file_path):  
            os.remove(file_path)
    chunks=[]
    
    for doc in documents:
        doc.metadata["file_extension"] = doc.metadata.get('file_name').split('.')[-1]
        if doc.metadata.get('file_extension') == "pdf":
            doc.metadata['num_pages'] = get_num_pages_pdf(doc.metadata.get('file_path'))
        elif doc.metadata.get('file_extension') == "docx":
            doc.metadata['num_pages'] = get_num_pages_docx(doc.metadata.get('file_path'))
        else:
            raise Exception(f"Type de fichier non supporté: {doc.metadata.get('file_extension')}")
        
        doc_id = await save_document(chat_id,doc)
        
        nodes = sentence_splitter.get_nodes_from_documents([doc])
        i = 0
        chunk_index = 0

        while i < len(nodes):
            node = nodes[i]
            element_type = node.metadata.get('element_type',"").lower()

            if element_type == "image":
                i += 1
                continue
            elif element_type == "table":
                node.text = clean_text(node.text)
                chunks.append(node)
                await save_chunk(doc_id,chunk_index,node)
                chunk_index += 1
            elif element_type == "title":
                if i + 1 < len(nodes):
                    next_node = nodes[i + 1]
                    node.text = clean_text(node.text + "\n" + next_node.text)
                    i += 1
                else:
                    node.text = clean_text(node.text)
                chunks.append(node)
                await save_chunk(doc_id,chunk_index,node)
                
            else:
                if len(node.text.split()) > 200:
                    sub_nodes = token_splitter.split_text(node.text)
                    for sub_node in sub_nodes:
                        new_node = node.copy()
                        new_node.text = clean_text(sub_node)
                        chunks.append(new_node)
                        await save_chunk(doc_id,chunk_index,new_node)
                        chunk_index += 1
                else:
                    node.text = clean_text(node.text)
                    chunks.append(node)
                    await save_chunk(doc_id,chunk_index,node)
                    chunk_index += 1
            i += 1
    return chunks
