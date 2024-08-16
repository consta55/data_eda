import os
from google.cloud.sql.connector import Connector
import pg8000
from langchain_community.vectorstores.pgvector import PGVector
from langchain_google_vertexai import VertexAIEmbeddings
import pandas as pd
import ollama
#data = pd.read_csv('/Users/andrea/Documents/git/gcp/embeddings1.csv')





project_id = "function-health-dev-env"  # @param {type:"string"}
database_password = "FunctionHealth"  # @param {type:"string"}
region = "us-central1"  # @param {type:"string"}
instance_name = "development-ac-poc"  # @param {type:"string"}
database_name = "poc"  # @param {type:"string"}
database_user = "app"  # @param {type:"string"}
# Edit this to add the chain you want to add
# (1) Initialize VectorStore
connector = Connector()
def getconn() -> pg8000.dbapi.Connection:
    conn: pg8000.dbapi.Connection = connector.connect(
            f"{project_id}:{region}:{instance_name}",  # Cloud SQL instance connection name
            "pg8000",
            user=f"{database_user}",
            password=f"{database_password}",
            db=f"{database_name}",
        )

    return conn
vectorstore = PGVector(
    connection_string="postgresql+pg8000://",
    use_jsonb=True,
    engine_args=dict(
        creator=getconn,
    ),
    embedding_function= ollama.embeddings(
        model="mxbai-embed-large"
    )
)

# Save all release notes into the Cloud SQL database
texts = ['lets see if this works']
ids = vectorstore.add_texts(texts)

print(f"Done saving: {len(ids)} release notes")