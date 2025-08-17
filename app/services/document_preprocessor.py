import os
import tempfile
from typing import Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
# <-- CHANGE: Add the Google Cloud Storage client library
from google.cloud import storage
from app.core.config import settings

# Initialize the embedding model
embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# --- CHANGE: Use lazy initialization for GCS client to avoid authentication issues during import ---
# Global variable to hold the client instance
_storage_client: Optional[storage.Client] = None

def get_storage_client() -> storage.Client:
    """
    Get or create a storage client instance.
    This lazy initialization prevents authentication errors during app startup/testing.
    """
    global _storage_client
    if _storage_client is None:
        _storage_client = storage.Client()
    return _storage_client

# --- CHANGE: Use lazy initialization for ChromaDB client as well ---
_chroma_client: Optional[Chroma] = None

def get_chroma_client() -> Chroma:
    """
    Get or create a ChromaDB client instance.
    This lazy initialization allows for better testing and startup performance.
    """
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = Chroma(
            collection_name="rag_collection",
            embedding_function=embedding_function,
            persist_directory=settings.CHROMA_PERSIST_DIRECTORY
        )
    return _chroma_client

def process_and_store_document(file_path_or_uri: str, document_id: str):
    """
    Loads a document from either a local path or a GCS URI,
    then chunks and stores it in the vector database.
    """
    
    # Get clients using lazy initialization
    storage_client = get_storage_client()
    chroma_client = get_chroma_client()
    
    # --- CHANGE: Add logic to handle GCS URIs ---
    # Check if the input is a GCS path
    if file_path_or_uri.startswith('gs://'):
        
        # 1. Parse the GCS URI to get the bucket name and the file name (blob name)
        bucket_name = file_path_or_uri.split('/')[2]
        file_name = "/".join(file_path_or_uri.split('/')[3:])

        # 2. Get a reference to the GCS object (the file)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)

        # 3. Download the file from GCS to a temporary local file.
        # This is the easiest way to make it compatible with PyPDFLoader.
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            blob.download_to_filename(tmp_file.name)
            processing_file_path = tmp_file.name # This is the path to the temp file
    else:
        # If it's not a GCS URI, assume it's a regular local file path
        processing_file_path = file_path_or_uri

    try:
        # The rest of the logic remains the same, using the local file path
        loader = PyPDFLoader(processing_file_path)
        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(documents)

        for chunk in chunks:
            chunk.metadata["document_id"] = document_id

        chroma_client.add_documents(chunks)
        
        return len(chunks)

    finally:
        # --- CHANGE: Clean up the temporary file if one was created ---
        # This is crucial to prevent the server's disk from filling up
        if file_path_or_uri.startswith('gs://') and os.path.exists(processing_file_path):
            os.remove(processing_file_path)