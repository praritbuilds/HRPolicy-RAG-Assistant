import json
import os
import time

import voyageai
from dotenv import load_dotenv


load_dotenv()


VOYAGE_MODEL = "voyage-4"
POLICY_CHUNKS_PATH = "data/policy_chunks.json"
MAX_BATCH_TOKENS = 4500


voyage_client = voyageai.Client(
    api_key=os.getenv("VOYAGE_API_KEY")
)


def load_chunks(file_path=POLICY_CHUNKS_PATH):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def prepare_embedding_text(chunk):
    parts = []

    if chunk.get("section"):
        parts.append(
            f"Section: {chunk['section']}"
        )

    if chunk.get("subsection"):
        parts.append(
            f"Subsection: {chunk['subsection']}"
        )

    if chunk.get("group"):
        parts.append(
            f"Group: {chunk['group']}"
        )

    if chunk.get("policy"):
        parts.append(
            f"Policy: {chunk['policy']}"
        )

    if chunk.get("text"):
        parts.append(
            f"Content: {chunk['text']}"
        )

    return "\n".join(parts)


def create_embedding_texts(chunks):
    return [
        prepare_embedding_text(chunk)
        for chunk in chunks
    ]


def create_batches(
    texts,
    max_tokens=MAX_BATCH_TOKENS
):
    batches = []
    current_batch = []

    for text in texts:
        candidate_batch = (
            current_batch + [text]
        )

        token_count = (
            voyage_client.count_tokens(
                candidate_batch
            )
        )

        if (
            token_count > max_tokens
            and current_batch
        ):
            batches.append(
                current_batch
            )

            current_batch = [text]

        else:
            current_batch.append(text)

    if current_batch:
        batches.append(
            current_batch
        )

    return batches


def generate_embeddings(
    embedding_texts
):
    batches = create_batches(
        embedding_texts
    )

    print(
        "Number of batches:",
        len(batches)
    )

    all_embeddings = []

    for index, batch in enumerate(
        batches,
        start=1
    ):
        token_count = (
            voyage_client.count_tokens(
                batch
            )
        )

        print(
            f"Batch {index}",
            "| Tokens:",
            token_count
        )

        result = voyage_client.embed(
            batch,
            model=VOYAGE_MODEL,
            input_type="document"
        )

        all_embeddings.extend(
            result.embeddings
        )

        time.sleep(31)

    return all_embeddings


def get_query_embedding(query):
    result = voyage_client.embed(
        [query],
        model=VOYAGE_MODEL,
        input_type="query"
    )

    return result.embeddings[0]


def main():
    chunks = load_chunks()

    embedding_texts = (
        create_embedding_texts(chunks)
    )

    token_count = (
        voyage_client.count_tokens(
            embedding_texts
        )
    )

    print(
        "Total chunks:",
        len(chunks)
    )

    print(
        "Total tokens:",
        token_count
    )

    all_embeddings = (
        generate_embeddings(
            embedding_texts
        )
    )

    print(
        "Total embeddings:",
        len(all_embeddings)
    )

    assert (
        len(all_embeddings)
        == len(chunks)
    )


if __name__ == "__main__":
    main()