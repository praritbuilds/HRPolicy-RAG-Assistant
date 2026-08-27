from pypdf import PdfReader


def extract_pages(file_path):
    reader = PdfReader(file_path)

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text()

        if text:
            pages.append({
                "page": page_number,
                "text": text.strip()
            })

    return pages

def chunk_text(text, chunksize=1000, overlap=200):
    start=0
    chunks=[]
    while start < len(text):
        end = start + chunksize
        chunks.append(text[start:end])
        start+=chunksize-overlap
    return chunks

def create_chunks(pages):
    all_chunks = []
    for page in pages:
        chunks = chunk_text(page["text"])
        for index, chunk in enumerate(chunks):
            all_chunks.append({
                "page": page["page"],
                "chunk_id": index,
                "text": chunk
            })
    return all_chunks

pages = extract_pages("data/employee-handbook.pdf")

chunks = create_chunks(pages)
for chunk in chunks:
    print(chunk)
    print("="*80)