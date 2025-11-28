# Document Embedding API

A FastAPI-based document embedding and semantic search system using Ollama for embeddings and Pinecone for vector storage.

## Features

- 📄 **Document Upload**: Support for PDF, DOCX, and TXT files
- 🔍 **Semantic Search**: Find relevant documents using natural language queries
- 💬 **Chat with Documents**: Ask questions and get answers based on uploaded documents
- 🎯 **Score Filtering**: Configurable minimum score threshold for search results

## Prerequisites

- Python 3.8+
- [Ollama](https://ollama.ai/) installed and running
- Pinecone account and API key

## Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd doc-embedding-api
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install and Setup Ollama

Download and install Ollama from [https://ollama.ai/](https://ollama.ai/)

Pull the required models:

```bash
ollama pull nomic-embed-text
ollama pull llama3
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX=your_index_name_here
```

To get your Pinecone API key:

1. Sign up at [https://www.pinecone.io/](https://www.pinecone.io/)
2. Create a new project
3. Copy your API key from the dashboard

## Usage

### Start the Server

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### API Endpoints

#### 1. Upload Document

Upload and index a document:

```bash
curl -X POST -F "file=@your_document.pdf" http://localhost:8000/upload
```

**Supported formats**: PDF, DOCX, TXT

**Response**:

```json
{
  "message": "Document processed and indexed!"
}
```

#### 2. Semantic Search

Search for relevant documents:

```bash
curl "http://localhost:8000/search?query=your+search+query&min_score=0.60"
```

**Parameters**:

- `query` (required): Search query text
- `min_score` (optional): Minimum similarity score (default: 0.60)

**Response**:

```json
{
  "results": [
    {
      "id": "document.pdf",
      "score": 0.85,
      "metadata": {
        "text": "Document content..."
      }
    }
  ]
}
```

#### 3. Chat with Documents

Ask questions based on indexed documents:

```bash
curl "http://localhost:8000/chat?query=what+is+this+about"
```

**Response**:

```json
{
  "answer": "Based on the documents, this is about..."
}
```

### Interactive API Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI documentation.

## Project Structure

```
doc-embedding-api/
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (create this)
├── uploads/             # Uploaded files directory
└── README.md           # This file
```

## How It Works

1. **Document Upload**: Files are uploaded and text is extracted based on file type
2. **Embedding Generation**: Text is converted to vector embeddings using Ollama's `nomic-embed-text` model
3. **Vector Storage**: Embeddings are stored in Pinecone with metadata
4. **Semantic Search**: Query text is embedded and similar vectors are retrieved from Pinecone
5. **Chat**: Retrieved context is sent to Ollama's `llama3` model to generate answers

## Error Handling

The API includes comprehensive error handling:

- **400 Bad Request**: Unsupported file type
- **503 Service Unavailable**: Ollama service not reachable

## Troubleshooting

### Ollama Connection Error

Make sure Ollama is running:

```bash
ollama serve
```

### Models Not Found

Pull the required models:

```bash
ollama pull nomic-embed-text
ollama pull llama3
```

### Pinecone Index Error

Ensure your Pinecone index:

- Has dimension set to **768** (matching nomic-embed-text)
- Uses **cosine** metric
- Is in a supported region (e.g., us-east-1)

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
