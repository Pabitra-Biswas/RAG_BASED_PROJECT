from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Manages all application settings.
    Reads from environment variables or a .env file.
    """
    
    # --- Google Cloud Settings ---
    # The name of the GCS bucket for storing uploaded documents.
    # This is a REQUIRED setting with no default. The app will not start without it.
    GCS_BUCKET_NAME: str

    # Your Google API key for authenticating with the Gemini LLM.
    GOOGLE_API_KEY: str

    # --- ChromaDB Settings ---
    # The directory where the vector database will be stored inside the container.
    # This path will be mapped to a Docker volume at runtime.
    CHROMA_PERSIST_DIRECTORY: str = "/code/chroma_db_storage"

    class Config:
        # Pydantic will automatically look for a .env file to load these settings
        # during local development. In production, these will be set as true
        # environment variables.
        env_file = ".env"
        env_file_encoding = 'utf-8'

# Create a single, importable instance of the settings
settings = Settings()