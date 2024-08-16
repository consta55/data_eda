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


# Edit this to add the chain you want to add
# (1) Initialize VectorStore
from google.cloud import aiplatform

aiplatform.init(project=f"{project_id}", location=f"{region}")

# (3) Create prompt template

user_query = input("User: ")
qe = ollama.embeddings(model="mxbai-embed-large", prompt= user_query)
qe1=qe[0]

matches = []

async def main():
    loop = asyncio.get_running_loop()
    async with Connector(loop=loop) as connector:
        # Create connection to Cloud SQL database.
        conn: asyncpg.Connection = await connector.connect_async(
            f"{project_id}:{region}:{instance_name}",  # Cloud SQL instance connection name
            "asyncpg",
            user=f"{database_user}",
            password=f"{database_password}",
            db=f"{database_name}",
        )

        await register_vector(conn)
        similarity_threshold = 0.3
        num_matches = 10

        # Find similar products to the query using cosine similarity search
        # over all vector embeddings. This new feature is provided by `pgvector`.
        results = await conn.fetch(
            """
                            WITH vector_matches AS (
                              SELECT content, 1 - (embedding <=> $1) AS similarity
                              FROM data_set1
                              WHERE 1 - (embedding <=> $1) > $2
                              ORDER BY similarity DESC
                              LIMIT $3
                            )
                            SELECT * from vector_matches
                            """,
            qe1,
            similarity_threshold,
            num_matches,
    
        )

        if len(results) == 0:
            raise Exception("Did not find any results. Adjust the query parameters.")

        for r in results:
            # Collect the description for all the matched similar toy products.
            matches.append(
                f"""{r["content"]}.
                         ."""
            )
        await conn.close()


# Run the SQL commands now.
    await main()  

# Show the results for similar products that matched the user query.
matches


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

docs = [Document(page_content=t) for t in matches]
chain = load_summarize_chain(
    llm, chain_type="map_reduce", map_prompt=map_prompt, combine_prompt=combine_prompt
)
answer = RunnableParallel.run(
    {
        "input_documents": docs,
        "user_query": RunnablePassthrough()
    }
)

# (5) Chain everything together


#add_routes(app, NotImplemented)
add_routes(app, chain)

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(app, port=8080)
