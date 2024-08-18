from typing import List

from langchain_core.callbacks import AsyncCallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
import asyncio
import asyncpg
from google.cloud.sql.connector import Connector
import numpy as np
from pgvector.asyncpg import register_vector
import ollama

project_id = "function-health-dev-env"  # @param {type:"string"}
database_password = "FunctionHealth"  # @param {type:"string"}
region = "us-central1"  # @param {type:"string"}
instance_name = "development-ac-poc"  # @param {type:"string"}
database_name = "poc"  # @param {type:"string"}
database_user = "ac-dev"  # @param {type:"string"}


async def embed_query(user_query:str):
    qe = ollama.embeddings(model="mxbai-embed-large", prompt=user_query)
    qe1 = qe['embedding']
    return(qe1)

async def get_docs(user_query:str):
    qe1 = await embed_query(user_query)
    matches = await main(qe1)
    return [Document(page_content=t) for t in matches]

async def getconn():
    
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
    return conn


async def main(user_query):
    qe = ollama.embeddings(model="mxbai-embed-large", prompt=user_query)
    qe1 = qe['embedding']
    matches = []
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
        return(matches)

from typing import List

from langchain_core.callbacks import AsyncCallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever


class GCPRetriever(BaseRetriever):
    #def __init__(self,_get_relevant_documents):
     #   self._get_relevant_documents = _get_relevant_documents()
                
    
    """Asynchronously get documents relevant to a query.

    #     Args:
    #         query: String to find relevant documents for
    #         run_manager: The callbacks handler to use

    #     Returns:
    #         List of relevant documents
    """
   

    

    async def get_docs(user_query:str):
            qe = ollama.embeddings(model="mxbai-embed-large", prompt=user_query)
            qe1 = qe['embedding']
            matches = await main(qe1)
            docs = [Document(page_content=t) for t in matches]
            print(docs)
            return docs
   
    
        
    #docs = await get_docs(user_query)
    async def _get_relevant_documents(
            self, user_query: str, *, run_manager: AsyncCallbackManagerForRetrieverRun
        )-> List[Document]:
            """Sync implementations for retriever."""
            
            #raise Exception("Sorry, no numbers below zero")
            matches = await main(user_query)
            docs = [Document(page_content=t) for t in matches]
            
            return docs

    

if __name__ == "__main__":
   
    user_query = "what does cholesterol do ?"
    asyncio.run(GCPRetriever())
    asyncio.run(_get_relevant_documents())
    
