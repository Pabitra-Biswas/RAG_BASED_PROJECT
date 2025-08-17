# from fastapi import APIRouter, UploadFile, File, HTTPException
# # <-- CHANGE: Remove 'Form' and import your Pydantic models
# from app.models import QueryRequest, QueryResponse, UploadResponse
# from app.services.document_preprocessor import process_and_store_document
# from app.services.rag_pipeline import invoke_agent 
# from google.cloud import storage
# from app.core.config import settings

# router = APIRouter()

# # Instantiate the GCS client
# # storage_client = storage.Client()

# from typing import Optional

# _storage_client: Optional[storage.Client] = None

# def get_storage_client() -> storage.Client:
#     """Get or create a storage client instance."""
#     global _storage_client
#     if _storage_client is None:
#         _storage_client = storage.Client()
#     return _storage_client

# # <-- CHANGE: Add the response_model to the decorator for validation and documentation
# @router.post("/upload", response_model=UploadResponse)
# async def upload_document(file: UploadFile = File(...)):
#     """
#     Uploads a PDF file to Google Cloud Storage and processes it into the vector database.
#     """
#     if file.content_type != 'application/pdf':
#         raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    
#     try:
#         # 1. Get a reference to the bucket
#         # New usage:
#         storage_client = get_storage_client()
#         bucket = storage_client.bucket("bucket-name")
        
#         # 2. Create a blob and upload the file
#         blob = bucket.blob(file.filename)
#         blob.upload_from_file(file.file, content_type=file.content_type)

#         # 3. Create the GCS URI
#         gcs_uri = f"gs://{settings.GCS_BUCKET_NAME}/{file.filename}"
#         document_id = file.filename
        
#         # 4. Process the document
#         num_chunks = process_and_store_document(gcs_uri, document_id)

#         # 5. Return a dictionary that matches the UploadResponse model
#         return {
#             "status": "success", 
#             "filename": file.filename,
#             "gcs_uri": gcs_uri,
#             "document_id": document_id, 
#             "chunks_stored": num_chunks
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")
#     finally:
#         file.file.close()


# # <-- CHANGE: Add response_model and use the QueryRequest model for the request body
# @router.post("/query", response_model=QueryResponse)
# async def query_system(request: QueryRequest):
#     """
#     Endpoint to ask a question. The agent will decide how to answer it.
#     """
#     # <-- CHANGE: Access the query from the request model
#     if not request.query:
#         raise HTTPException(status_code=400, detail="Query cannot be empty.")
    
#     try:
#         # <-- CHANGE: Pass request.query to the agent
#         answer = invoke_agent(request.query)
#         # Return a dictionary that matches the QueryResponse model
#         return {"query": request.query, "answer": answer}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models import QueryRequest, QueryResponse, UploadResponse
from app.services.document_preprocessor import process_and_store_document
from app.services.rag_pipeline import invoke_agent 
from google.cloud import storage
from app.core.config import settings
import traceback
import logging

router = APIRouter()

from typing import Optional

_storage_client: Optional[storage.Client] = None

def get_storage_client() -> storage.Client:
    """Get or create a storage client instance."""
    global _storage_client
    if _storage_client is None:
        _storage_client = storage.Client(project='my-bigquery-test-466512')
    return _storage_client

@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Uploads a PDF file to Google Cloud Storage and processes it into the vector database.
    """
    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    
    try:
        print(f"Processing file: {file.filename}")
        print(f"Content type: {file.content_type}")
        
        # 1. Get a reference to the bucket - FIXED: Use actual bucket name
        storage_client = get_storage_client()
        bucket_name = "my_buckets99"  # Your actual bucket name
        bucket = storage_client.bucket(bucket_name)
        print(f"Connected to bucket: {bucket_name}")
        
        # 2. Reset file pointer to beginning (important!)
        await file.seek(0)
        
        # 3. Create a blob and upload the file
        blob = bucket.blob(file.filename)
        print(f"Uploading to blob: {file.filename}")
        
        # Read file content
        file_content = await file.read()
        blob.upload_from_string(file_content, content_type=file.content_type)
        print(f"Upload successful")

        # 4. Create the GCS URI - FIXED: Use actual bucket name
        gcs_uri = f"gs://{bucket_name}/{file.filename}"
        document_id = file.filename
        
        # 5. Process the document
        print(f"Processing document with URI: {gcs_uri}")
        num_chunks = process_and_store_document(gcs_uri, document_id)
        print(f"Document processed, chunks: {num_chunks}")

        # 6. Return a dictionary that matches the UploadResponse model
        return {
            "status": "success", 
            "filename": file.filename,
            "gcs_uri": gcs_uri,
            "document_id": document_id, 
            "chunks_stored": num_chunks
        }
    except Exception as e:
        # FIXED: Better error logging
        error_msg = f"Failed to process file: {str(e)}"
        print(f"ERROR: {error_msg}")
        print(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=error_msg)


@router.post("/query", response_model=QueryResponse)
async def query_system(request: QueryRequest):
    """
    Endpoint to ask a question. The agent will decide how to answer it.
    """
    if not request.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    
    try:
        answer = invoke_agent(request.query)
        return {"query": request.query, "answer": answer}
    except Exception as e:
        print(f"Query error: {str(e)}")
        print(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")