import pdfplumber

# Extract raw text from PDF
def extract_text_from_pdf(file_path: str) -> list[dict]:
    """
    Returns a list of {"page": page_number, "text": page_text} dicts,
    one per page, preserving page boundaries for later chunking.
    """
    pages = []
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            page_text = page.extract_text()
            if page_text:
                pages.append({"page": i, "text": page_text})
    return pages

# Normalize the text
def normalize_text(pages: list[dict]) -> list[dict]:
    """
    Cleans whitespace/line-breaks within each page's text,
    while preserving page boundaries.
    """
    normalized = []
    for p in pages:
        cleaned = p["text"].replace("\n", " ").replace("\r", " ")
        cleaned = " ".join(cleaned.split())
        normalized.append({"page": p["page"], "text": cleaned})
    return normalized

# Chunk the text
def chunk_text(pages: list[dict], chunk_size: int = 500, overlap: int = 50) -> list[dict]:
    """
    Split each page's text into overlapping chunks.
    Returns a list of dicts: {"text", "start", "end", "page"}
    start/end are character offsets within that page's text.
    """
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks = []
    for p in pages:
        page_num = p["page"]
        page_text = p["text"]
        start = 0
        while start < len(page_text):
            end = min(start + chunk_size, len(page_text))
            chunks.append({
                "text": page_text[start:end],
                "start": start,
                "end": end,
                "page": page_num
            })
            if end == len(page_text):
                break
            start += chunk_size - overlap
    return chunks