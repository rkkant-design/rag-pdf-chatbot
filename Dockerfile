FROM python:3.11-slim

WORKDIR /app

# System deps kept minimal; wheels cover chromadb/pypdf on slim.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
