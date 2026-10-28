# RAG PDF Chatbot

Ask questions in plain English and get answers **grounded in your own PDFs** — every answer
carries a **source citation** (document name + page), and when the answer isn't in the documents
the bot **says so** instead of guessing.

Built to be accuracy-first: the whole point of RAG over internal docs is that it must *not*
behave like generic ChatGPT.

```
PDFs ─► chunk + metadata ─► embeddings ─► Chroma (vector DB)
                                               │
                     question ─► retrieve top-k ─► relevance gate ─► LLM (grounded prompt)
                                               │                         │
                                               └──────── answer + citations, or honest refusal
```

## Features

- **Grounded answers only.** Two independent guardrails: a retrieval relevance gate *and* a
  prompt that forbids outside knowledge. If neither clears, the bot returns
  `"I couldn't find this in the provided documents."`
- **Source citations.** Each answer lists the document and page it came from. Citations are
  attached from retrieval metadata, never invented by the model.
- **Clean ingestion.** Per-page loading with `source` + `page` metadata, then recursive
  character chunking with overlap.
- **FastAPI `/chat` endpoint** and a **Streamlit chat UI**.
- **Evaluation harness** over sample questions (in-corpus answered, out-of-corpus refused),
  with a drop-in path to **RAGAS** metrics.
- **Docker + docker-compose**, `.env` config, and runnable **sample PDFs** so it works out of
  the box.

## Stack

Python · LangChain · OpenAI (chat + embeddings) · Chroma (vector DB) · FastAPI · Streamlit · Docker

## Quickstart (local)

```bash
# 1. Install
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure
cp .env.example .env            # add your OPENAI_API_KEY

# 3. Create the sample PDFs (or drop your own into ./data)
python scripts/make_sample_pdfs.py

# 4. Ingest the PDFs into the vector store
python -m app.ingest

# 5a. Run the API
uvicorn app.api:app --reload --port 8000

# 5b. In another terminal, run the chat UI
streamlit run ui/streamlit_app.py
```

Ask the API directly:

```bash
curl -s localhost:8000/chat -H "content-type: application/json" \
  -d '{"question":"How long is the warranty on the Trailblazer tent?"}'
```

```json
{
  "answer": "The Trailblazer Tent has a 2-year limited warranty covering manufacturing defects.",
  "sources": [{"document": "product-guide.pdf", "page": 1, "score": 0.52}],
  "grounded": true
}
```

Ask something outside the documents and it refuses:

```json
{ "answer": "I couldn't find this in the provided documents.", "sources": [], "grounded": false }
```

## Quickstart (Docker)

```bash
cp .env.example .env            # add your OPENAI_API_KEY
python scripts/make_sample_pdfs.py
docker compose run --rm api python -m app.ingest   # one-time ingest into the shared volume
docker compose up                                   # API on :8000, UI on :8501
```

## Evaluate

```bash
python -m eval.evaluate
```

Runs the questions in `eval/questions.json` and checks the two behaviours that matter:
in-corpus questions get answered (with sources), out-of-corpus questions get refused. For
metric-based scoring (faithfulness, answer relevancy, context precision/recall), add
[RAGAS](https://docs.ragas.io) — see the note in `eval/evaluate.py`.

## Configuration

All via environment (`.env`):

| Variable | Default | Purpose |
|---|---|---|
| `OPENAI_API_KEY` | — | required |
| `CHAT_MODEL` | `gpt-4o-mini` | answer generation |
| `EMBED_MODEL` | `text-embedding-3-small` | embeddings |
| `TOP_K` | `4` | chunks retrieved per question |
| `RELEVANCE_THRESHOLD` | `0.25` | below this for every chunk → refuse |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | `900` / `150` | chunking |

## How accuracy is protected

1. **Retrieval gate** — if no retrieved chunk clears `RELEVANCE_THRESHOLD`, the bot refuses
   *before* an LLM call (cheaper and safer).
2. **Grounded prompt** — the system prompt forbids outside knowledge and mandates the exact
   refusal string when the context lacks the answer.
3. **Citations from metadata** — sources come from the retrieved chunks' `source`/`page`
   metadata, so the model can't fabricate a reference.
4. **`temperature=0`** — deterministic, conservative answers.

## Project structure

```
app/
  config.py      env-driven settings
  prompts.py     grounded system prompt + refusal string
  ingest.py      PDF -> chunks -> Chroma
  rag.py         retrieve -> gate -> grounded answer + citations
  api.py         FastAPI /chat, /health
ui/
  streamlit_app.py   chat UI calling the API
eval/
  questions.json     sample eval set
  evaluate.py        in-corpus answered / out-of-corpus refused (+ RAGAS note)
scripts/
  make_sample_pdfs.py  generates runnable sample PDFs
data/                  your PDFs (sample set included)
Dockerfile, docker-compose.yml
```

## Production notes

For this demo the vector store is **Chroma** (zero external services, easy to run). For a
production deployment I'd recommend **pgvector on Postgres** — it keeps embeddings, metadata,
and citations in one database you already own and back up, which simplifies ops. Swapping is a
one-file change in `app/ingest.py` and `app/rag.py` (use `langchain_postgres.PGVector`). Other
production steps: auth on the API, response caching, and continuous RAGAS evaluation in CI.

## License

MIT © Kamalakanth Ramani
