import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from app.services.document_preprocessor import process_and_store_document
# Import the new agent service
from app.services.rag_pipeline import invoke_agent 

router = APIRouter()
UPLOAD_DIRECTORY = "./uploads"

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

# The /upload endpoint remains the same
@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    
    file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        document_id = file.filename
        num_chunks = process_and_store_document(file_path, document_id)
        return {"status": "success", "filename": file.filename, "document_id": document_id, "chunks_stored": num_chunks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")
    finally:
        file.file.close()

# The /query endpoint now uses the agent
@router.post("/query")
async def query_system(query: str = Form(...)):
    """
    Endpoint to ask a question. The agent will decide how to answer it.
    """
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    
    try:
        answer = invoke_agent(query)
        # Note: Getting specific source documents is more complex with an agent,
        # as it might perform multiple retrievals. The final answer is synthesized.
        # For now, we return the agent's final answer.
        return {"query": query, "answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")