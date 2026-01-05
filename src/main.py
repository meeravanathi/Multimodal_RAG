import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import shutil
from pathlib import Path

from ingestion.indexer import DocumentIndexer
from generation.usecase_generator import UseCaseGenerator
from utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="Multimodal RAG Use Case Generator",
    description="Generate test cases and use cases from multimodal documents using RAG",
    version="1.0.0"
)

class QueryRequest(BaseModel):
    query: str
    debug_mode: Optional[bool] = False

class IndexResponse(BaseModel):
    message: str
    files_processed: int
    total_chunks: int

class GenerateResponse(BaseModel):
    use_cases: List[dict]
    confidence_score: float
    retrieved_sources: List[str]
    warnings: List[str]
    assumptions: List[str]
    error: Optional[str] = None

# Global instances
indexer = DocumentIndexer()
generator = UseCaseGenerator()

@app.get("/")
async def root():
    return {"message": "Multimodal RAG Use Case Generator API", "status": "running"}

@app.post("/index", response_model=IndexResponse)
async def index_documents():
    """Index all documents in the input directory"""
    try:
        total_chunks = indexer.index_all_documents()
        return IndexResponse(
            message="Documents indexed successfully",
            files_processed=len(indexer.file_loader.discover_files()),
            total_chunks=total_chunks
        )
    except Exception as e:
        logger.error(f"Indexing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file to the input directory for indexing"""
    try:
        input_dir = Path("./data/input")
        input_dir.mkdir(parents=True, exist_ok=True)

        file_path = input_dir / file.filename

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"File uploaded: {file.filename}")
        return {"message": f"File {file.filename} uploaded successfully"}

    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/generate", response_model=GenerateResponse)
async def generate_use_cases(request: QueryRequest):
    """Generate use cases based on the query"""
    try:
        result = generator.generate(request.query, request.debug_mode)

        return GenerateResponse(
            use_cases=result.get("use_cases", []),
            confidence_score=result.get("confidence_score", 0.0),
            retrieved_sources=result.get("retrieved_sources", []),
            warnings=result.get("warnings", []),
            assumptions=result.get("assumptions", []),
            error=result.get("error")
        )
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@app.get("/status")
async def get_status():
    """Get system status"""
    try:
        vector_count = indexer.vector_store.count()
        return {
            "status": "healthy",
            "indexed_chunks": vector_count,
            "input_directory": str(indexer.file_loader.input_dir)
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)