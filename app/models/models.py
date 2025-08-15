from pydantic import BaseModel

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    query: str
    answer: str

class UploadResponse(BaseModel):
    status: str
    filename: str
    # <-- CHANGE: Add the new gcs_uri field to match the API response
    gcs_uri: str
    document_id: str
    chunks_stored: int