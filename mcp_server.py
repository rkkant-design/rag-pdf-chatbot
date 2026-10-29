"""MCP server exposing the RAG document corpus as standard tools.

Model Context Protocol (MCP) lets any compatible host - Claude Desktop, an IDE,
or an agent framework - connect to this knowledge base through one standard
interface, instead of each app writing bespoke glue to reach it.

This server exposes two tools over stdio:
  - search_documents: semantic search, returns the most relevant chunks + citations
  - ask_documents:    a grounded answer with sources, or an honest refusal

Prerequisites: the PDFs must be ingested first (python -m app.ingest) and
OPENAI_API_KEY set, exactly as for the API and UI.

Run:  python mcp_server.py
"""
from mcp.server.fastmcp import FastMCP

from app.rag import answer, retrieve

mcp = FastMCP("rag-pdf-chatbot")


@mcp.tool()
def search_documents(query: str, k: int = 4) -> str:
    """Semantically search the ingested PDFs and return the most relevant
    passages, each tagged with its source document and page. Use this to ground
    an answer in the company's own documents.

    Args:
        query: what to look for.
        k: how many passages to return (default 4).
    """
    results = retrieve(query, k=k)
    if not results:
        return "No matching passages were found in the document set."
    blocks = []
    for doc, score in results:
        src = doc.metadata.get("source", "unknown")
        page = doc.metadata.get("page", "?")
        rel = round(float(score), 3) if score is not None else "n/a"
        blocks.append(f"[{src} p.{page} | relevance {rel}]\n{doc.page_content}")
    return "\n\n---\n\n".join(blocks)


@mcp.tool()
def ask_documents(question: str) -> str:
    """Answer a question using ONLY the ingested PDFs, with source citations.
    If the answer is not in the documents, it says so instead of guessing.

    Args:
        question: the question to answer from the documents.
    """
    result = answer(question)
    if not result["grounded"]:
        return result["answer"]  # the honest refusal
    sources = "; ".join(f"{s['document']} p.{s['page']}" for s in result["sources"])
    return f"{result['answer']}\n\nSources: {sources}"


if __name__ == "__main__":
    # Default transport is stdio, which is how MCP hosts launch local servers.
    mcp.run()
