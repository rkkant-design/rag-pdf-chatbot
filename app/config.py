"""Central configuration, read from environment (.env supported)."""
import os

from dotenv import load_dotenv

load_dotenv()

# --- OpenAI ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4o-mini")
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")

# --- Paths ---
DATA_DIR = os.getenv("DATA_DIR", "data")
CHROMA_DIR = os.getenv("CHROMA_DIR", "chroma_store")
COLLECTION = os.getenv("COLLECTION", "docs")

# --- Chunking ---
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "900"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))

# --- Retrieval ---
TOP_K = int(os.getenv("TOP_K", "4"))
# Minimum cosine relevance (0..1) for the BEST match. If even the top chunk is
# below this, the query is off-topic and the bot refuses before calling the LLM.
# Chunks at or above this are shown as citations. Tune per corpus.
RELEVANCE_THRESHOLD = float(os.getenv("RELEVANCE_THRESHOLD", "0.15"))
# Cite only chunks within this cosine margin of the best match, so citations point
# to the source(s) the answer actually came from rather than every retrieved chunk.
CITATION_MARGIN = float(os.getenv("CITATION_MARGIN", "0.08"))


def require_key() -> str:
    if not OPENAI_API_KEY:
        raise SystemExit(
            "OPENAI_API_KEY is not set. Copy .env.example to .env and add your key."
        )
    return OPENAI_API_KEY
