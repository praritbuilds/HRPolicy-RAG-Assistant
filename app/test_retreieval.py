from embedding import get_query_embedding
from vector_store import get_collection


query = (
    "Can international employees "
    "carry forward unused sick leave?"
)

query_embedding = (
    get_query_embedding(query)
)

collection = get_collection()

results = collection.query(
    query_embeddings=[
        query_embedding
    ],
    n_results=5
)

for i in range(
    len(results["documents"][0])
):
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