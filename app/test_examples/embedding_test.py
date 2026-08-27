import os
import voyageai
from dotenv import load_dotenv

load_dotenv()

voyage_client = voyageai.Client(
    api_key=os.getenv("VOYAGE_API_KEY")
)

documents = [
    "Employees are entitled to ten sick days per calendar year.",
    "Employees receive 20 vacation days every year.",
    "The company provides health insurance to employees.",
]

query = "How much sick leave do employees get?"

# Embed documents
doc_result = voyage_client.embed(
    documents,
    model="voyage-4",
    input_type="document"
)

# Embed query
query_result = voyage_client.embed(
    [query],
    model="voyage-4",
    input_type="query"
)

doc_embeddings = doc_result.embeddings
query_embedding = query_result.embeddings[0]



import numpy as np


def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)

    return np.dot(a, b) / (
        np.linalg.norm(a) * np.linalg.norm(b)
    )

for document, embedding in zip(documents, doc_embeddings):

    score = cosine_similarity(
        query_embedding,
        embedding
    )

    print(f"{score:.4f} -> {document}")