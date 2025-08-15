from pydantic import BaseSettings

class Settings(BaseSettings):
    # Directory to store uploaded files
    upload_dir: str = "./uploads"
    # Directory for ChromaDB storage
    chroma_db_dir: str = "./chroma_db_storage"
    # Google API key for LLM (if needed)
    google_api_key: str = ""
    # Add other settings as needed

    class Config:
        env_file = ".env"  # Loads environment variables from .env file

settings = Settings()