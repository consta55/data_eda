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
from IPython.display import display, Markdown
from pydantic import BaseModel
from langchain_community.chat_models import ChatOllama
from app.member_data_pull import get_ai_summary

import json



app = FastAPI()
user_query = "how can I lower my ldl cholesterol?"
#llm = ChatOllama(model="llama3.1")
llm = ChatVertexAI(model_name="gemini-pro")
prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|> You are a medical professional.
    Use the following pieces of retrieved context to answer the question. 
    If you don't know the answer, just say that you don't know.
    You also have access to the patient's member persona. Please use this information to personalize your answer
    Give a thoughtful and empathetic response to the question <|eot_id|><|start_header_id|>user<|end_header_id|>
    Question: {user_query}
    Context: {text}
    Member_Persona: {member_persona}
    Answer: <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["user_query", "text", "member_persona"],
)
class User_query(BaseModel):
  member_id: str  
  user_query: str

data = []
@app.post('/User_query/')
async def create_item(user_query: User_query):
    user_query_dict = user_query.model_dump()
    user_query = user_query_dict["user_query"]
    member_id = user_query_dict["member_id"]
    member_persona = get_ai_summary(member_id)
    llm_agent = prompt | llm 
    docs = await GCPRetriever().invoke(user_query)
    #docs = retriever.invoke(user_query)
    answer= llm_agent.invoke({"user_query" :user_query, "text": docs, "member_persona": member_persona})
    return (answer.content)



