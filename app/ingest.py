"""Ingest PDFs: load -> clean chunk (with doc/page metadata) -> embed -> Chroma.

Run:  python -m app.ingest
"""
import glob
import os

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from app import config


def load_pages(data_dir: str) -> list[Document]:
    """One Document per PDF page, tagged with source filename + 1-based page."""
    pdfs = sorted(glob.glob(os.path.join(data_dir, "*.pdf")))
    if not pdfs:
        raise SystemExit(
            f"No PDFs found in '{data_dir}'. Run: python scripts/make_sample_pdfs.py"
        )
    pages: list[Document] = []
    for path in pdfs:
        reader = PdfReader(path)
        for i, page in enumerate(reader.pages):
            text = (page.extract_text() or "").strip()
            if text:
                pages.append(
                    Document(
                        page_content=text,
                        metadata={"source": os.path.basename(path), "page": i + 1},
                    )
                )
    return pages


def build_index():
    config.require_key()
    pages = load_pages(config.DATA_DIR)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(pages)

    embeddings = OpenAIEmbeddings(model=config.EMBED_MODEL, api_key=config.OPENAI_API_KEY)

    # Rebuild the collection from scratch so re-ingesting is idempotent.
    Chroma(
        collection_name=config.COLLECTION,
        embedding_function=embeddings,
        persist_directory=config.CHROMA_DIR,
    ).delete_collection()

    Chroma.from_documents(
        chunks,
        embedding=embeddings,
        collection_name=config.COLLECTION,
        persist_directory=config.CHROMA_DIR,
        # Cosine space gives normalized 0..1 relevance scores for a reliable gate.
        collection_metadata={"hnsw:space": "cosine"},
    )
    print(
        f"Ingested {len(pages)} page(s) -> {len(chunks)} chunk(s) "
        f"into collection '{config.COLLECTION}' at '{config.CHROMA_DIR}'."
    )


if __name__ == "__main__":
    build_index()
