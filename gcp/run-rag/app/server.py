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

app = FastAPI()


@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")

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

async def get_docs():
    retriever = GCPRetriever()


    docs = await retriever.invoke(user_query)
    
    return docs

docs = asyncio.run(get_docs())

#await retriever.ainvoke(user_query)



llm = ChatVertexAI(model_name="gemini-pro")

map_prompt_template = """
              You will be given a detailed description of a toy product.
              This description is enclosed in triple backticks (```).
              Using this description only, extract the name of the toy,
              the price of the toy and its features.

              ```{text}```
              SUMMARY:
              """
map_prompt = PromptTemplate(template=map_prompt_template, input_variables=["text"])
# (4) Initialize LLM
combine_prompt_template = """
                You will be given health information
                enclosed in triple backticks (```) and a question enclosed in
                double backticks(``).
                You are a medical professional. Please answer the question in 200 words in an empathetic manner. Use only the given health information to answer


                Description:
                ```{text}```


                Question:
                ``{user_query}``


                Answer:
                """
combine_prompt = PromptTemplate(
    template=combine_prompt_template, input_variables=["text", "user_query"]
)

chain = load_summarize_chain(
    llm, chain_type="map_reduce", map_prompt=map_prompt, combine_prompt=combine_prompt
)
answer = chain.run(
    {
        "input_documents": docs,
        "user_query": user_query
    }
)

# (5) Chain everything together


#add_routes(app, NotImplemented)
add_routes(app, chain)

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(app, port=8080)
