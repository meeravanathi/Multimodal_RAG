# Multimodal RAG Use Case Generator

A comprehensive Retrieval-Augmented Generation (RAG) system for generating test cases and use cases from multimodal documents (text, PDFs, images).

## Features

- **📄 Multimodal Document Processing**: Supports text, markdown, PDF, images, CSV, JSON, and more
- **🔍 Intelligent Hybrid Retrieval**: Combines vector similarity search with BM25 keyword search
- **🛡️ Comprehensive Guard Rails**: Confidence checking, prompt injection filtering, deduplication, and hallucination detection
- **🎨 Beautiful Web UI**: Streamlit-based interface for easy document upload, indexing, and use case generation
- **⚡ FastAPI Backend**: RESTful API for programmatic access
- **📊 Rich Results**: Detailed use cases with confidence scores, assumptions, and source tracking
- **🔧 Production Ready**: Comprehensive logging, metrics, and error handling

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Ingestion     │    │   Retrieval     │    │  Generation     │
│                 │    │                 │    │                 │
│ • File Loader   │    │ • Vector Store  │    │ • LLM Client    │
│ • Text/PDF/Image│    │ • Hybrid Search │    │ • Prompt Builder│
│   Processors    │    │ • Query Proc.   │    │ • Use Case Gen. │
│ • Chunker       │    │                 │    │                 │
│ • Indexer       │    └─────────────────┘    └─────────────────┘
└─────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐
│    Guards       │    │     Utils      │
│                 │    │                 │
│ • Confidence    │    │ • Logger        │
│ • Injection     │    │ • Metrics       │
│   Filter        │    │ • Validators    │
│ • Deduplicator  │    │                 │
│ • Hallucination │    └─────────────────┘
│   Detector      │
└─────────────────┘
```

## Quick Start

### One-Command Launch (Recommended)

Start both the API and UI together:

```bash
cd src
python launcher.py
```

This will start:
- FastAPI backend on `http://localhost:8000`
- Streamlit UI on `http://localhost:8501`

### Manual Launch

1. **Terminal 1 - API Server:**
   ```bash
   cd src
   python main.py
   ```

2. **Terminal 2 - Web UI:**
   ```bash
   cd src
   streamlit run ui.py
   ```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd multimodal-rag
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   - Copy `.env.example` to `.env`
   - Add your API keys:
     ```
     GROQ_API_KEY=your_groq_api_key_here
     OPENAI_API_KEY=your_openai_api_key_here
     ANTHROPIC_API_KEY=your_anthropic_api_key_here
     ```

## Usage

### Option 1: Web UI (Recommended)

1. **Start the API server:**
   ```bash
   cd src
   python main.py
   ```

2. **Start the web UI (in another terminal):**
   ```bash
   cd src
   streamlit run ui.py
   ```

3. **Open your browser** to the Streamlit URL (usually `http://localhost:8501`)

### Option 2: API Only

1. **Index documents:**
   ```bash
   cd src
   python index_documents.py
   ```

2. **Start the API server:**
   ```bash
   cd src
   python main.py
   ```

3. **Use the API endpoints** or run the demo:
   ```bash
   cd src
   python demo.py
   ```

### Option 3: Direct Generation

With a valid API key in `.env`:
```bash
cd src
python generate_usecases.py
```

## API Endpoints

- `GET /` - Health check
- `POST /index` - Index all documents in input directory
- `POST /upload` - Upload a file for indexing
- `POST /generate` - Generate use cases from query
- `GET /status` - Get system status

## Supported File Types

- **Text**: `.txt`, `.md`
- **Data**: `.csv`, `.json`, `.yaml`, `.xlsx`
- **Documents**: `.pdf`, `.docx`
- **Images**: `.png`, `.jpg`, `.jpeg` (OCR supported)

## Configuration

Key settings in `config.py`:

- `llm_provider`: "groq", "openai", or "anthropic"
- `embedding_model`: Sentence transformer model
- `chunk_size`: Text chunk size (default: 512)
- `top_k_retrieval`: Number of documents to retrieve (default: 5)
- `confidence_threshold`: Minimum confidence score (default: 0.6)

## Testing

Run the test suite:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=src --cov-report=html
```

## Development

### Code Quality

```bash
# Format code
black src/

# Lint code
ruff check src/

# Type checking
mypy src/
```

### Adding New Features

1. **New Document Processor**: Add to `ingestion/` directory
2. **New Guard**: Add to `guards/` directory
3. **New Retrieval Method**: Extend `retriever/` classes
4. **New LLM Provider**: Update `generation/llm_client.py`

## Troubleshooting

### Common Issues

1. **"No module named 'src'"**: Run from `src/` directory
2. **API Key Errors**: Check `.env` file and API key validity
3. **No Documents Found**: Ensure files are in `data/input/` and indexed
4. **Low Confidence**: Try more specific queries or add more documents

### Logs

Check logs in `logs/app.log` for detailed debugging information.

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request