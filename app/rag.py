"""Retrieval-augmented answering with source citations and honest refusal.

Two guardrails against hallucination:
  1. Relevance gate: if even the best-matching chunk is below RELEVANCE_THRESHOLD,
     the query is off-topic, so refuse before calling the LLM.
  2. Grounded prompt: the retrieved chunks are passed to the LLM, which is instructed
     to answer only from them and return the exact refusal string otherwise.
Sources (document name + page) come from retrieval metadata, never invented by the model.
"""
from functools import lru_cache

from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from app import config
from app.prompts import ANSWER_TEMPLATE, REFUSAL, SYSTEM_PROMPT


@lru_cache(maxsize=1)
def _store() -> Chroma:
    embeddings = OpenAIEmbeddings(model=config.EMBED_MODEL, api_key=config.OPENAI_API_KEY)
    return Chroma(
        collection_name=config.COLLECTION,
        embedding_function=embeddings,
        persist_directory=config.CHROMA_DIR,
    )


@lru_cache(maxsize=1)
def _llm() -> ChatOpenAI:
    return ChatOpenAI(model=config.CHAT_MODEL, temperature=0, api_key=config.OPENAI_API_KEY)


def retrieve(question: str, k: int | None = None):
    """Return [(Document, relevance_score)] with cosine relevance in 0..1."""
    return _store().similarity_search_with_relevance_scores(question, k=k or config.TOP_K)


def answer(question: str) -> dict:
    """Return {answer, sources, grounded}."""
    results = retrieve(question)
    if not results:
        return {"answer": REFUSAL, "sources": [], "grounded": False}

    scored = [(doc, (score if score is not None else 0.0)) for doc, score in results]
    best = max(score for _, score in scored)

    # Guardrail 1: nothing is even plausibly relevant -> refuse without an LLM call.
    if best < config.RELEVANCE_THRESHOLD:
        return {"answer": REFUSAL, "sources": [], "grounded": False}

    # Pass the retrieved chunks to the LLM; the grounded prompt decides if they answer.
    # Cite only the top matches (within CITATION_MARGIN of the best), so references
    # point to where the answer came from, not every retrieved chunk.
    cite_floor = max(config.RELEVANCE_THRESHOLD, best - config.CITATION_MARGIN)
    context_blocks, sources = [], []
    for doc, score in scored:
        src = doc.metadata.get("source", "unknown")
        page = doc.metadata.get("page", "?")
        context_blocks.append(f"[{src} p.{page}]\n{doc.page_content}")
        if score >= cite_floor:
            sources.append({"document": src, "page": page, "score": round(float(score), 3)})

    prompt = ANSWER_TEMPLATE.format(context="\n\n".join(context_blocks), question=question)
    response = _llm().invoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)])
    text = response.content.strip()

    # Guardrail 2: honour the model's refusal, and hide sources when it refuses.
    grounded = REFUSAL.lower() not in text.lower()
    if not grounded:
        return {"answer": text, "sources": [], "grounded": False}

    # De-duplicate sources by (document, page), preserving best-score order.
    unique, seen = [], set()
    for s in sources:
        key = (s["document"], s["page"])
        if key not in seen:
            seen.add(key)
            unique.append(s)

    return {"answer": text, "sources": unique, "grounded": True}
