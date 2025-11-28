from fastapi import FastAPI, UploadFile, File, HTTPException
from dotenv import load_dotenv
import os, requests
from PyPDF2 import PdfReader
from docx import Document
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

app = FastAPI()

# Pinecone setup (skip if using ChromaDB)
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = os.getenv("PINECONE_INDEX")

if index_name not in [i.name for i in pc.list_indexes()]:
    pc.create_index(
        name=index_name,
        dimension=768,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

index = pc.Index(index_name)


def extract_text(path):
    ext = path.split(".")[-1].lower()

    if ext == "pdf":
        reader = PdfReader(path)
        return " ".join(page.extract_text() for page in reader.pages)

    elif ext == "docx":
        doc = Document(path)
        return " ".join(p.text for p in doc.paragraphs)

    elif ext == "txt":
        return open(path, "r", encoding="utf-8").read()
    
    raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}. Only PDF, DOCX, and TXT are supported.")


def create_embedding(text):
    try:
        response = requests.post(
            "http://localhost:11434/api/embeddings",
            json={"model": "nomic-embed-text", "prompt": text}
        )
        response.raise_for_status()
        print(response.json())
        return response.json()["embedding"]
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Ollama embedding service error: {str(e)}")


@app.post("/upload")
async def upload_doc(file: UploadFile = File(...)):
    os.makedirs("uploads", exist_ok=True)
    file_path = f"uploads/{file.filename}"

    with open(file_path, "wb") as f:
        f.write(await file.read())

    text = extract_text(file_path)
    embedding = create_embedding(text)

    index.upsert([(file.filename, embedding, {"text": text})])

    return {"message": "Document processed and indexed!"}


@app.get("/search")
async def semantic_search(query: str,min_score: float = 0.60):
    query_emb = create_embedding(query)

    result = index.query(
        vector=query_emb,
        top_k=3,
        include_metadata=True
    )

    cleaned_results = [
        {
            "id": match.id,
            "score": match.score,
            "metadata": match.metadata
        }
        for match in result.matches
        if match.score >= min_score
    ]

    return {"results": cleaned_results}


@app.get("/chat")
async def chat_with_docs(query: str):
    search_results = await semantic_search(query)
    
    # Extract results from the dictionary
    results = search_results["results"]
    
    # Handle case when no results found
    if not results:
        return {"answer": "I don't have enough context to answer this question. Please upload relevant documents first."}
    
    context = "\n".join([result["metadata"]["text"] for result in results])

    prompt = f"Answer based on context:\n{context}\n\nUser: {query}\nAnswer:"

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3", "prompt": prompt, "stream": False}
        )
        response.raise_for_status()
        return {"answer": response.json()["response"]}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Ollama generation service error: {str(e)}")

    return {"answer": response}
