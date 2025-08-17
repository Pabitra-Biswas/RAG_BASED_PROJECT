# Initialize a new Git repository
git init -b main

# Add all your files to be tracked (Git will respect your .gitignore file)
git add .

# Make your first commit
git commit -m "Initial commit: Setup complete RAG application with Docker and Jenkins integration"

# Link your local repository to the one on GitHub
# (Replace YOUR_USERNAME and YOUR_REPO_NAME with your actual GitHub details)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push your code to GitHub
git push -u origin main

2. Final Project Structure
Your final, clean folder structure that you push to GitHub should look like this:
/
├── app/
│   ├── api/
│   │   └── routes.py
│   ├── core/
│   │   └── config.py
│   ├── models/
│   │   └── models.py
│   ├── services/
│   │   ├── document_preprocessor.py
│   │   └── rag_pipeline.py
│   └── main.py
│
├── custom_jenkins/
│   └── Dockerfile
│
├── templates/
│   └── index.html
│
├── .dockerignore
├── .env.example       
├── .gitignore
├── Dockerfile         
├── Jenkinsfile        
└── requirements.txt

Smart RAG Q&A System with FastAPI and Gemini
This project is a complete, full-stack Retrieval-Augmented Generation (RAG) application that allows users to upload PDF documents and ask questions about their content. The system uses Google's Gemini LLM, is built with FastAPI, containerized with Docker, and features a CI/CD pipeline orchestrated by Jenkins.
Features
Document Upload: Securely upload PDF files directly to Google Cloud Storage.
Intelligent Q&A: Ask questions in natural language and receive accurate, context-aware answers sourced directly from the uploaded documents.
RAG Architecture: Leverages a robust RAG pipeline with LangChain to minimize AI hallucinations and ensure factual responses.
Stateless & Scalable: Designed for the cloud with stateless architecture, making it ready for scalable deployments.
Containerized: Fully containerized with Docker for consistent development, testing, and production environments.
Automated Builds: Includes a Jenkins CI/CD pipeline for automated Docker image builds upon code changes.
Tech Stack & Architecture
Backend: Python, FastAPI
AI Orchestration: LangChain
LLM: Google Gemini 1.5 Flash
Vector Store: ChromaDB
Embeddings: HuggingFace all-MiniLM-L6-v2
Cloud Storage: Google Cloud Storage (GCS)
Containerization: Docker
CI/CD: Jenkins


Architecture Diagram:

+-----------+      +-----------------+      +-----------------------+
|   User    |----->|   FastAPI API   |----->| Google Cloud Storage  |
+-----------+      | (Docker Container)|      +-----------------------+
      ^            +--------+--------+                | (PDF Upload)
      |                     | (Query)                 |
      | (Answer)            |                         v
      |            +--------v--------+      +-----------------------+
      +------------|  LangChain Agent  |<---->|   Chroma Vector DB    |
                   | (Gemini LLM)    |      | (Embeddings)          |
                   +-----------------+      +-----------------------+

Setup and Installation
Prerequisites
Git
Python 3.10+
Docker and Docker Compose
A Google Cloud Platform (GCP) project

git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME

2. Google Cloud Setup
Create a GCS Bucket: Go to your GCP project and create a new Google Cloud Storage bucket.
Create a Service Account:
In the GCP Console, navigate to "IAM & Admin" > "Service Accounts".
Create a new service account (e.g., rag-app-sa).
Grant it the Storage Object Admin (roles/storage.objectAdmin) role on the bucket you created.
Download JSON Key:
After creating the service account, go to its "Keys" tab.
Click "Add Key" > "Create new key", select JSON, and download the file.
Save this file securely. Do not commit it to Git.


3. Local Environment Setup
Create a .env file:
Make a copy of the example environment file: cp .env.example .env
Edit the .env file with your specific credentials and settings:

# The name of your GCS bucket
GCS_BUCKET_NAME="your-gcs-bucket-name"

# Your Google API Key for Gemini
GOOGLE_API_KEY="your-google-api-key"

# The path to your service account JSON key file (for local development)
GOOGLE_APPLICATION_CREDENTIALS="C:/path/to/your/service-account-key.json"

# The local path for the vector database
CHROMA_PERSIST_DIRECTORY="./chroma_db_storage"


4. Running the Application
Option A: Running Locally with Uvicorn

uvicorn app.main:app --reload
```The application will be available at **http://127.0.0.1:8000**.

#### Option B: Running with Docker (Recommended)

This simulates a production environment.

1.  **Build the Docker Image:**
    ```bash
    docker build -t rag-fastapi-app .
    ```

2.  **Run the Docker Container:**
    This command runs the app and uses Docker volumes to persist your vector database.

    ```bash
    docker run -d -p 8000:8000 --name my-rag-app \
      --env-file .env \
      -v "$(pwd)/chroma_db_storage:/code/chroma_db_storage" \
      rag-fastapi-app
    ```
    The application will be available at **http://localhost:8000**.

## API Usage

You can interact with the API via the web interface at `http://localhost:8000` or use tools like `curl` or Postman.

#### 1. Upload a Document

-   **Endpoint:** `POST /upload`
-   **Body:** `multipart/form-data` with a `file` key containing the PDF.

**Example using `curl`:**
```bash
curl -X POST -F "file=@/path/to/your/document.pdf" http://localhost:8000/upload


CI/CD with Jenkins
This project includes a Jenkinsfile for automating the build of the application's Docker image.

docker run -d --name rag-jenkins \
  --privileged \
  -p 8080:8080 -p 50000:50000 \
  -m 4g \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v jenkins_home:/var/jenkins_home \
  rag_dind_jenkins
```3.  **Configure Jenkins:**
-   Access Jenkins at `http://localhost:8080`.
-   Create a new "Pipeline" job and point it to the `Jenkinsfile` in your Git repository.
-   Running the job will automatically build the `rag-fastapi-app` Docker image.
