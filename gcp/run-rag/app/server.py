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
llm = ChatVertexAI(model_name="gemini-pro")
prompt = PromptTemplate(
    template="""
                You will be given health information
                enclosed in triple backticks (```) and a question enclosed in
                double backticks(``).
                You are a medical professional. Given the member persona, please answer the question in 200 words in an empathetic and personalized manner. 
                Use only the given health information to answer and ensure to use the member persona to contextualize your response. 
                Biomarkers that are Overrange will be listed in the OVER_Range field of the member persona
                If the patient is a smoker this will be in the smoker field of the member persona
                If the patient drinks, this will be found in the alchol field, and the frequency of alcohol intake can be found in the alcohol_frequency field.
                The patient diet can be found in field diet, and if they are physically active, this field will be set to true
                The medications the patient is taking can be found in identified medications field, and the past medical conditions the patient has self identified can be found in the conditions field
                hollistically assess the patients member persona and ensure to use the member persona and the text to contextualize your response.
                
                Use everything you know about the patient from the member persona to contextualize text and give the member the most personalized answer possible

                Question:
                ``{user_query}``
                
                Context:
                ``{member_persona}``
                Description:
                ```{text}```


                Answer:
                """,
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
    return (answer.content)



