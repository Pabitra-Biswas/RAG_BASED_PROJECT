import os
from langchain.agents import AgentExecutor, create_react_agent
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools.retriever import create_retriever_tool
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from app.core.config import settings

from langchain import hub
from dotenv import load_dotenv

# load_dotenv() is great for local development. In production (e.g., Docker/Cloud Run),
# you will set environment variables directly in the environment.
load_dotenv()

# --- CHANGE 1: Correct the LLM model name to a valid one ---
# "gemini-2.0-flash" is not a recognized model. Use "gemini-1.5-flash-latest".
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")


# --- CHANGE 2: Make the database path configurable to match the preprocessor ---
# Both files must point to the exact same directory.
# CHROMA_PERSIST_DIRECTORY = os.environ.get("CHROMA_PERSIST_DIRECTORY", "./chroma_db_storage")

embedding_function = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')
chroma_client = Chroma(
    collection_name="rag_collection",
    embedding_function=embedding_function,
    persist_directory=settings.CHROMA_PERSIST_DIRECTORY
)
retriever = chroma_client.as_retriever()


# --- The rest of the file remains the same ---

# 3. Create a "Tool" for the Agent
retriever_tool = create_retriever_tool(
    retriever,
    "document_retriever",
    "Searches and returns relevant information from the uploaded documents. Use this tool to answer any questions about the document content."
)

tools = [retriever_tool]

# 4. Create the Agent
prompt = hub.pull("hwchase17/react")
agent = create_react_agent(llm, tools, prompt)

# 5. Create the Agent Executor
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


def invoke_agent(query: str):
    """
    Invokes the agent with a user query to get a response.
    """
    try:
        response = agent_executor.invoke({"input": query})
        # Safely get the output to avoid errors if the key doesn't exist
        return response.get('output', "The agent did not produce a final answer.")
    except Exception as e:
        # It's good practice to log the error for debugging
        print(f"ERROR: Agent invocation failed: {e}")
        return "An error occurred while processing your request. Please check the server logs."