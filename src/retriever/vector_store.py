import chromadb
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from config import settings
from ingestion.chunker import Chunk
from utils.logger import get_logger

logger = get_logger(__name__)

class VectorStore:
    
    def __init__(self):
        self.embedding_model = SentenceTransformer(settings.embedding_model)
        
        self.client = chromadb.PersistentClient(path=settings.vector_db_path)
        
        try:
            self.collection = self.client.get_collection("documents")
            logger.info("Loaded existing ChromaDB collection")
        except:
            self.collection = self.client.create_collection(
                name="documents",
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("Created new ChromaDB collection")
    
    def add_documents(self, chunks: List[Chunk]):
        if not chunks:
            return
        
        documents = [chunk.content for chunk in chunks]
        ids = [chunk.chunk_id for chunk in chunks]
        
        # Flatten metadata for ChromaDB
        metadatas = []
        for chunk in chunks:
            metadata = {
                'chunk_id': chunk.chunk_id,
                'source_file': chunk.source_file,
                'chunk_index': chunk.chunk_index,
                'file_path': chunk.metadata.get('file_path', ''),
                'file_name': chunk.metadata.get('file_name', ''),
                'file_type': chunk.metadata.get('file_type', ''),
                'file_size': str(chunk.metadata.get('file_size', 0))
            }
            metadatas.append(metadata)
        
        embeddings = self.embedding_model.encode(
            documents,
            show_progress_bar=False,
            convert_to_numpy=True
        ).tolist()
        
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas
        )
        
        logger.debug(f"Added {len(chunks)} chunks to vector store")
    
    def search(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        top_k = top_k or settings.top_k_retrieval
        
        query_embedding = self.embedding_model.encode(
            [query],
            show_progress_bar=False,
            convert_to_numpy=True
        ).tolist()[0]
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        retrieved = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                retrieved.append({
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'score': 1 - results['distances'][0][i],
                    'chunk_id': results['ids'][0][i]
                })
        
        logger.debug(f"Vector search returned {len(retrieved)} results")
        return retrieved
    
    def clear(self):
        try:
            self.client.delete_collection("documents")
            self.collection = self.client.create_collection(
                name="documents",
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("Cleared vector store")
        except Exception as e:
            logger.error(f"Error clearing vector store: {e}")
    
    def count(self) -> int:
        return self.collection.count()