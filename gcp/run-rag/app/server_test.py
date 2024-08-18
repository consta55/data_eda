from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from langserve import add_routes
import os
from google.cloud.sql.connector import Connector
from langchain_google_vertexai import VertexAI
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores.pgvector import PGVector
import ollama
import asyncio
import asyncpg
from google.cloud.sql.connector import Connector
import numpy as np
from pgvector.asyncpg import register_vector
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from langchain import PromptTemplate, LLMChain
#from IPython.display import display, Markdown
from langchain_google_vertexai import ChatVertexAI
from app.gcp_retriever import GCPRetriever, getconn
from langchain_core.callbacks import AsyncCallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import (
    RunnableBranch,
    RunnableLambda,
    RunnableParallel,
    RunnablePassthrough,
)
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

app = FastAPI()
user_query = "what does ldl cholesterol do?"
#llm = ChatOllama(model=local_llm, format="json", temperature=0)
@app.get("/")
async def get_embedding():
    #llm_agent = prompt | llm | JsonOutputParser()
    docs = await GCPRetriever().invoke(user_query)
    #docs = retriever.invoke(user_query)
    return docs


project_id = "function-health-dev-env"  # @param {type:"string"}
database_password = "FunctionHealth"  # @param {type:"string"}
region = "us-central1"  # @param {type:"string"}
instance_name = "development-ac-poc"  # @param {type:"string"}
database_name = "poc"  # @param {type:"string"}
database_user = "ac-dev"  # @param {type:"string"}

user_query = 'what does hdl cholesterol do'

# Edit this to add the chain you want to add
# (1) Initialize VectorStore
from google.cloud import aiplatform

aiplatform.init(project=f"{project_id}", location=f"{region}")




# (5) Chain everything together
  #answer = 
  
 
  
  
if __name__ == "__main__":
   
    import uvicorn
    
    uvicorn.run(app, port=8080)