import os
import requests
import chromadb
import voyageai

from dotenv import load_dotenv


load_dotenv()


VOYAGE_MODEL = "voyage-4"

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/models/gemini-3.1-flash-lite:generateContent"
)

CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "employee_handbook"


voyage_client = voyageai.Client(
    api_key=os.getenv("VOYAGE_API_KEY")
)

chroma_client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

collection = chroma_client.get_or_create_collection(
    name=COLLECTION_NAME
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def generate_answer(question, context):
    prompt = f"""
You are an employee policy assistant.

Answer the user's question using ONLY the employee handbook
context provided below.

Rules:
- Do not use outside knowledge.
- Do not invent company policies.
- If the answer cannot be found in the provided context,
  say: "I could not find this information in the employee handbook."
- Give a concise and clear answer.
- Include the source handbook page number used for the answer.

EMPLOYEE HANDBOOK CONTEXT:

{context}

USER QUESTION:

{question}
"""

    response = requests.post(
        GEMINI_URL,
        headers={
            "Content-Type": "application/json",
            "X-goog-api-key": GEMINI_API_KEY
        },
        json={
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": 200,
                "temperature": 0.2
            }
        },
        timeout=20
    )

    response.raise_for_status()

    data = response.json()

    return data["candidates"][0]["content"]["parts"][0]["text"]


def build_context(results):
    contexts = []

    for document, metadata in zip(
        results["documents"][0],
        results["metadatas"][0]
    ):
        context = f"""
Printed handbook page: {metadata["printed_page"]}
PDF page: {metadata["pdf_page"]}

{document}
"""
        contexts.append(context)

    return "\n\n---\n\n".join(contexts)


def execute_query(query):
    query_result = voyage_client.embed(
        [query],
        model=VOYAGE_MODEL,
        input_type="query"
    )

    query_embedding = query_result.embeddings[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    context = build_context(results)
    return generate_answer(
        query,
        context
    )