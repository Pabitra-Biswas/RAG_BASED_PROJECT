import os
from langchain.agents import AgentExecutor, create_react_agent
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools.retriever import create_retriever_tool
from langchain_huggingface.embeddings import HuggingFaceEmbeddings

from langchain import hub
from dotenv import load_dotenv

load_dotenv()

# 1. Initialize the LLM for the Agent's reasoning
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash",temperature=0.2)

# 2. Initialize the Retriever
# This component is the same as in the standard RAG setup
embedding_function = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')
chroma_client = Chroma(
    collection_name="rag_collection",
    embedding_function=embedding_function,
    persist_directory="./chroma_db_storage"
)
retriever = chroma_client.as_retriever()

# 3. Create a "Tool" for the Agent
# The agent doesn't directly use the retriever. It uses a "Tool" that wraps the retriever.
# This makes the system modular and allows you to add more tools later.
retriever_tool = create_retriever_tool(
    retriever,
    "document_retriever",
    "Searches and returns relevant information from the uploaded documents. Use this tool to answer any questions about the document content."
)

# A list of all tools the agent can use
tools = [retriever_tool]

# 4. Create the Agent
# We use a pre-built prompt template from LangChain Hub for the "ReAct" (Reason+Act) agent type.
# This prompt guides the LLM to think, act, and observe in a loop.
prompt = hub.pull("hwchase17/react")

# Bind the LLM, tools, and prompt together to create the agent
agent = create_react_agent(llm, tools, prompt)

# 5. Create the Agent Executor
# The executor is the runtime environment that runs the agent loop.
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


def invoke_agent(query: str):
    """
    Invokes the agent with a user query to get a response.
    """
    try:
        response = agent_executor.invoke({"input": query})
        return response.get('output', "No answer found.")
    except Exception as e:
        print(f"Agent invocation failed: {e}")
        return "An error occurred while processing your request." 