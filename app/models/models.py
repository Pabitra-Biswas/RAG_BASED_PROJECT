from pydantic import BaseModel

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    query: str
    answer: str

class UploadResponse(BaseModel):
    status: str
    filename: str
    document_id: str
    chunks_stored: int