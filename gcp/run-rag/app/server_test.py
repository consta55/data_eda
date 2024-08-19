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


app = FastAPI()
user_query = "how can I lower my ldl cholesterol?"
member_persona =[{
        "patient_id":"001db85bd9a25730eacf1297e639ac56329f1b20d669101d7400c7f8372409f1",
        "requisition_id":"2975090ecdc502c8ec1bc740969be9d780fe5cf56380a4167c121eb6ec2fd785",
        "diet":[
            "Omnivore"
        ],
        "physically_active":[
            "false"
        ],
        "smoker":[
            "false"
        ],
        "sex":[
            "Female"
        ],
        "alcohol":[
            "true"
        ],
        "alcohol_frequency":[
            "Once a month"
        ],
        "OVER_Range":[
            "ldl particle number",
            "ldl medium",
            "ldl peak size",
            "ldl small",
            "ldl cholesterol",
            "total cholesterol",
            "apolipoprotein b (apob)"
        ],
        "BELOW_Range":[

        ],
        "Outof_Range":[

        ],
        "identified_medications":"vitamin d, vitamin a, zinc",
        "conditions":[
            "asthma"
        ],
        "content":"Apolipoprotein B (Apo B) was high. Elevated levels of Apo B increase your cardiovascular risk. Apo B attaches to negative types of cholesterol that cause plaque buildup in your blood vessels, which can lead to damage and heart disease.\nThere are signs of a cholesterol problem (high total cholesterol, high LDL \u201cbad\u201d cholesterol, high LDL small cholesterol, high LDL medium cholesterol, high LDL particle number, high non-HDL cholesterol). This can be due to several causes including diet, genetics, and\/or toxin exposure. However, your HDL \"good\" cholesterol was high, which actually decreases cardiovascular risk. Please talk with your local doctor to develop a treatment plan.\nYour omega 3 profile correlates with moderate risk for heart disease. You have a mix of both negative and protective factors. Overall, the levels aren\u2019t concerning but this is something to keep an eye on.\n"
    }]
llm = ChatOllama(model="llama3.1")
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
  user_query: str

data = []
@app.post('/User_query/')
async def create_item(user_query: User_query):
    user_query_dict = user_query.model_dump()
    user_query = user_query_dict["user_query"]
    llm_agent = prompt | llm 
    docs = await GCPRetriever().invoke(user_query)
    #docs = retriever.invoke(user_query)
    answer= llm_agent.invoke({"user_query" :user_query, "text": docs, "member_persona": member_persona})
    return (answer)



