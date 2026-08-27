import chromadb
import os
import json
import voyageai
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

voyage_client = voyageai.Client(
    api_key=os.getenv("VOYAGE_API_KEY")
)

client = chromadb.PersistentClient(
    path="chroma_db"
)

collection = client.get_or_create_collection(
    name="employee_handbook"
)

query = "How many sick days do international employees get?"

query_result = voyage_client.embed(
    [query],
    model="voyage-4",
    input_type="query"
)

query_embedding = query_result.embeddings[0]

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3
)


for i in range(len(results["documents"][0])):
    print("=" * 80)

    print(
        "Distance:",
        results["distances"][0][i]
    )

    print(
        "Metadata:",
        results["metadatas"][0][i]
    )

    print(
        "Document:",
        results["documents"][0][i]
    )