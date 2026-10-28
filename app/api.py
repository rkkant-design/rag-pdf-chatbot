"""FastAPI backend exposing POST /chat and GET /health."""
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

from app.rag import answer

app = FastAPI(title="RAG PDF Chatbot", version="1.0.0")


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[dict[str, Any]]
    grounded: bool


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    result = answer(req.question)
    return ChatResponse(**result)
