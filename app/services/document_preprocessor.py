import os
import tempfile
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
# <-- CHANGE: Add the Google Cloud Storage client library
from google.cloud import storage
from app.core.config import settings

# --- CHANGE: Make the database path configurable via an environment variable ---
# This allows you to easily change the path for Docker/production without changing code.
# It defaults to the old value if the environment variable isn't set.
# CHROMA_PERSIST_DIRECTORY = os.environ.get("CHROMA_PERSIST_DIRECTORY", "./chroma_db_storage")

# Initialize the embedding model
embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Initialize GCS client to be used later
# This will automatically authenticate using a service account when run on GCP or Docker
storage_client = storage.Client()

# Initialize ChromaDB client with the new configurable path
chroma_client = Chroma(
    collection_name="rag_collection",
    embedding_function=embedding_function,
    persist_directory=settings.CHROMA_PERSIST_DIRECTORY
)

def process_and_store_document(file_path_or_uri: str, document_id: str):
    """
    Loads a document from either a local path or a GCS URI,
    then chunks and stores it in the vector database.
    """
    
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