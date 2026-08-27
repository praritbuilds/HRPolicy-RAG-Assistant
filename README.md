# HRPolicy --- RAG-Based Employee Policy Chatbot

HRPolicy is an AI-powered employee policy assistant that answers
questions using an employee handbook as its source of truth.

The project implements Retrieval-Augmented Generation (RAG): relevant
handbook policies are retrieved using semantic search and supplied to an
LLM to produce a grounded answer with the printed handbook page as the
source.

## Features

-   Extracts handbook text with PyPDF
-   Preserves both physical PDF pages and printed handbook/footer pages
-   Creates policy-aware chunks with section, subsection, group, and
    policy metadata
-   Generates document and query embeddings with Voyage AI
-   Stores and searches vectors with ChromaDB
-   Uses Gemini Flash or another LLM for grounded answer generation
-   Includes printed handbook page references
-   Returns a fallback response when the handbook does not support an
    answer
-   Keeps API credentials outside source code

## Architecture

``` text
Employee Handbook PDF
        |
        v
      PyPDF
        |
        v
Structured Policy Chunks
        |
        v
Voyage AI Embeddings
        |
        v
     ChromaDB
        |
        v
User Question
        |
        v
Voyage Query Embedding
        |
        v
Semantic Retrieval
        |
        v
Top Relevant Policies
        |
        v
Prompt + Retrieved Context
        |
        v
Gemini / Other LLM
        |
        v
Grounded Answer + Printed Page
```

## Tech Stack

-   Python
-   PyPDF
-   Voyage AI
-   ChromaDB
-   Gemini API or another LLM API
-   python-dotenv
-   requests

## Project Structure

``` text
policy-chatbot/
|-- app/
|   |-- chatbot.py
|   |-- embedding.py
|   `-- chunking.py
|-- data/
|   |-- employee-handbook.pdf
|   `-- policy_chunks.json
|-- chroma_db/
|-- .env
|-- .env.example
|-- .gitignore
|-- requirements.txt
`-- README.md
```

## How It Works

### 1. Extract the handbook

PyPDF reads the handbook page by page. The extraction stage retains both
page values:

``` json
{
    "pdf_page": 14,
    "page": 10
}
```

`pdf_page` is the physical PDF position and is useful for debugging.
`page` is the number printed in the handbook footer and is used for
chatbot citations.

### 2. Create structured policy chunks

``` json
{
    "pdf_page": 14,
    "page": 10,
    "section": "III. EMPLOYEE BENEFITS",
    "subsection": "A. EMPLOYEE LEAVE",
    "group": "2. Leave for International Employees",
    "policy": "b. Sick Leave",
    "text": "Employees are entitled to ten (10) sick days per calendar year..."
}
```

### 3. Generate embeddings

Metadata is combined with policy content before embedding so retrieval
understands both the text and its policy context.

Voyage document embeddings use:

``` python
input_type="document"
```

Questions use:

``` python
input_type="query"
```

For lower API rate limits, handbook chunks are processed in token-aware
batches.

### 4. Store vectors in ChromaDB

ChromaDB persists embeddings together with document text and metadata
including the printed handbook page, physical PDF page, section,
subsection, group, and policy.

### 5. Retrieve relevant policies

The user's question is embedded with Voyage AI. ChromaDB performs
semantic similarity search and returns the most relevant handbook
chunks.

### 6. Generate a grounded answer

The retrieved chunks are sent to the LLM as context. The model is
instructed to answer only from that context, avoid inventing policies,
and cite the printed handbook page.

Example:

``` text
International employees are entitled to 10 sick days per calendar year.
Up to 3 unused sick days may be carried over to the next year, but sick
leave is not paid out upon termination.

Source: Employee Handbook, Page 10
```

For unsupported questions:

``` text
I could not find this information in the employee handbook.
```

## Setup

### Create a virtual environment

Windows:

``` bash
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

``` bash
python -m venv .venv
source .venv/bin/activate
```

### Install dependencies

``` bash
pip install pypdf voyageai chromadb python-dotenv requests
```

### Environment variables

Create a local `.env` file:

``` env
VOYAGE_API_KEY=your_voyage_api_key
GEMINI_API_KEY=your_gemini_api_key
```

If another LLM provider is used, configure only the credentials required
for that provider.

Never commit real API keys. Rotate any API key that has been exposed.

## Current Status

-   [x] PDF extraction
-   [x] Printed footer-page extraction
-   [x] Policy-aware chunking
-   [x] Metadata preservation
-   [x] Voyage embeddings
-   [x] Token-aware embedding batching
-   [x] ChromaDB persistence
-   [x] Semantic retrieval
-   [x] LLM answer generation
-   [x] Unsupported-policy fallback
-   [x] Printed handbook page citations
-   [ ] FastAPI backend
-   [ ] Chat UI
-   [ ] Automated retrieval evaluation
-   [ ] Conversation history
-   [ ] Multiple policy documents

## Future Improvements

-   FastAPI REST API
-   Web chat interface
-   Retrieval score thresholds
-   Hybrid keyword + semantic search
-   Reranking
-   Automated RAG evaluation
-   Multiple policy documents
-   Conversation history
-   Docker deployment
-   Authentication and authorization
-   Logging and observability
-   Policy versioning
-   Streaming LLM responses

## Security

-   Store secrets in `.env` or a proper secret manager.
-   Keep `.env` out of Git.
-   Do not commit private employee handbooks unless approved for source
    control.
-   Rotate any exposed API key.
-   Adding `.env` to `.gitignore` does not untrack an already committed
    file. Use `git rm --cached .env` and commit the removal.

## Disclaimer

HRPolicy is a learning project. Generated answers should be validated
against the authoritative employee handbook before being used for
employment or HR decisions.
