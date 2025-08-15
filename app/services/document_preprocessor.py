import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface.embeddings import HuggingFaceEmbeddings

# Initialize the embedding model
embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
# Initialize ChromaDB client
chroma_client = Chroma(
    collection_name="rag_collection",
    embedding_function=embedding_function,
    persist_directory="./chroma_db_storage" # This can be a mounted volume in production
)

def process_and_store_document(file_path: str, document_id: str):
    """Loads, chunks, and stores a document in the vector database."""
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)

    # Add document_id to metadata for each chunk
    for chunk in chunks:
        chunk.metadata["document_id"] = document_id

    # Add chunks to ChromaDB
    chroma_client.add_documents(chunks)
    
    # In a real system, you would store metadata here in a relational/NoSQL DB
    # e.g., db.save_metadata(document_id, original_filename, num_chunks)
    
    return len(chunks)