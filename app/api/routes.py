from fastapi import APIRouter, UploadFile, File, HTTPException
# <-- CHANGE: Remove 'Form' and import your Pydantic models
from app.models import QueryRequest, QueryResponse, UploadResponse
from app.services.document_preprocessor import process_and_store_document
from app.services.rag_pipeline import invoke_agent 
from google.cloud import storage
from app.core.config import settings

router = APIRouter()

# Instantiate the GCS client
storage_client = storage.Client()

# <-- CHANGE: Add the response_model to the decorator for validation and documentation
@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Uploads a PDF file to Google Cloud Storage and processes it into the vector database.
    """
    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    
    try:
        # 1. Get a reference to the bucket
        bucket = storage_client.bucket(settings.GCS_BUCKET_NAME)
        
        # 2. Create a blob and upload the file
        blob = bucket.blob(file.filename)
        blob.upload_from_file(file.file, content_type=file.content_type)

        # 3. Create the GCS URI
        gcs_uri = f"gs://{settings.GCS_BUCKET_NAME}/{file.filename}"
        document_id = file.filename
        
        # 4. Process the document
        num_chunks = process_and_store_document(gcs_uri, document_id)

        # 5. Return a dictionary that matches the UploadResponse model
        return {
            "status": "success", 
            "filename": file.filename,
            "gcs_uri": gcs_uri,
            "document_id": document_id, 
            "chunks_stored": num_chunks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")
    finally:
        file.file.close()


# <-- CHANGE: Add response_model and use the QueryRequest model for the request body
@router.post("/query", response_model=QueryResponse)
async def query_system(request: QueryRequest):
    """
    Endpoint to ask a question. The agent will decide how to answer it.
    """
    # <-- CHANGE: Access the query from the request model
    if not request.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    
    try:
        # <-- CHANGE: Pass request.query to the agent
        answer = invoke_agent(request.query)
        # Return a dictionary that matches the QueryResponse model
        return {"query": request.query, "answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")