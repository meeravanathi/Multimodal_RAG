from typing import List, Dict, Any
from rank_bm25 import BM25Okapi
from retriever.vector_store import VectorStore
from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)

class HybridRetriever:
    
    def __init__(self):
        self.vector_store = VectorStore()
        self.bm25_index = None
        self.documents = []
        self.doc_ids = []
        self._build_bm25_index()
    
    def _build_bm25_index(self):
        try:
            count = self.vector_store.count()
            if count == 0:
                logger.warning("No documents in vector store for BM25 indexing")
                return
            
            all_docs = self.vector_store.collection.get(
                include=["documents", "metadatas"]
            )
            
            if all_docs['documents']:
                self.documents = all_docs['documents']
                self.doc_ids = all_docs['ids']
                
                tokenized_docs = [doc.lower().split() for doc in self.documents]
                self.bm25_index = BM25Okapi(tokenized_docs)
                
                logger.info(f"Built BM25 index with {len(self.documents)} documents")
        except Exception as e:
            logger.error(f"Error building BM25 index: {e}")
    
    def retrieve(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        top_k = top_k or settings.top_k_retrieval
        
        vector_results = self.vector_store.search(query, top_k=top_k * 2)
        
        keyword_results = []
        if self.bm25_index and self.documents:
            keyword_results = self._bm25_search(query, top_k=top_k * 2)
        
        if not keyword_results:
            logger.debug("Using vector-only retrieval (BM25 unavailable)")
            return vector_results[:top_k]
        
        fused_results = self._reciprocal_rank_fusion(
            vector_results,
            keyword_results,
            top_k=top_k
        )
        
        logger.info(f"Hybrid retrieval returned {len(fused_results)} results")
        return fused_results
    
    def _bm25_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        tokenized_query = query.lower().split()
        scores = self.bm25_index.get_scores(tokenized_query)
        
        scored_docs = [
            {
                'content': self.documents[i],
                'score': float(scores[i]),
                'chunk_id': self.doc_ids[i],
                'metadata': {}
            }
            for i in range(len(scores))
        ]
        
        scored_docs.sort(key=lambda x: x['score'], reverse=True)
        return scored_docs[:top_k]
    
    def _reciprocal_rank_fusion(
        self,
        vector_results: List[Dict[str, Any]],
        keyword_results: List[Dict[str, Any]],
        top_k: int,
        k: int = 60
    ) -> List[Dict[str, Any]]:
        
        doc_scores = {}
        doc_content = {}
        
        for rank, doc in enumerate(vector_results, start=1):
            doc_id = doc['chunk_id']
            doc_scores[doc_id] = doc_scores.get(doc_id, 0) + 1.0 / (k + rank)
            doc_content[doc_id] = doc
        
        for rank, doc in enumerate(keyword_results, start=1):
            doc_id = doc['chunk_id']
            doc_scores[doc_id] = doc_scores.get(doc_id, 0) + 1.0 / (k + rank)
            if doc_id not in doc_content:
                doc_content[doc_id] = doc
        
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        
        fused_results = []
        for doc_id, score in sorted_docs[:top_k]:
            doc = doc_content[doc_id].copy()
            doc['fusion_score'] = score
            fused_results.append(doc)
        
        return fused_results
    
    def refresh_index(self):
        self._build_bm25_index()