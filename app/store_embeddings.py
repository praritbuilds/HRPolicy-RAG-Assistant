import chromadb

from embedding import (
    load_chunks,
    create_embedding_texts,
    generate_embeddings
)


CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "employee_handbook"


def get_collection():
    client = chromadb.PersistentClient(
        path=CHROMA_PATH
    )

    return client.get_or_create_collection(
        name=COLLECTION_NAME
    )


def build_chroma_data(
    chunks,
    embedding_texts
):
    ids = []
    documents = []
    metadatas = []

    for index, chunk in enumerate(chunks):

        ids.append(
            f"chunk_{index}"
        )

        documents.append(
            embedding_texts[index]
        )

        metadatas.append({
            "pdf_page": chunk.get("pdf_page") or -1,
            "printed_page": chunk.get("printed_page") or -1,
            "section": chunk.get("section") or "",
            "subsection": chunk.get("subsection") or "",
            "group": chunk.get("group") or "",
            "policy": chunk.get("policy") or ""
        })

    return (
        ids,
        documents,
        metadatas
    )


def store_embeddings():
    chunks = load_chunks()

    embedding_texts = (
        create_embedding_texts(
            chunks
        )
    )

    all_embeddings = (
        generate_embeddings(
            embedding_texts
        )
    )

    collection = get_collection()

    ids, documents, metadatas = (
        build_chroma_data(
            chunks,
            embedding_texts
        )
    )

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=all_embeddings,
        metadatas=metadatas
    )

    print(
        "Documents stored:",
        collection.count()
    )


if __name__ == "__main__":
    store_embeddings()