#!/usr/bin/env python3
"""
Demo script showing the Multimodal RAG system capabilities.
This demonstrates document indexing and retrieval without requiring LLM API keys.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ingestion.indexer import DocumentIndexer
from retriever.hybrid_retriever import HybridRetriever
from utils.logger import get_logger

logger = get_logger(__name__)

def demo():
    print("🚀 Multimodal RAG Use Case Generator Demo")
    print("=" * 50)

    try:
        # Step 1: Index documents
        print("\n📚 Step 1: Indexing Documents")
        indexer = DocumentIndexer()
        total_chunks = indexer.index_all_documents()
        print(f"✅ Indexed {total_chunks} chunks from documents")

        # Step 2: Test retrieval
        print("\n🔍 Step 2: Testing Retrieval")
        retriever = HybridRetriever()
        query = "Generate test cases for user authentication and payment processing"
        results = retriever.retrieve(query, top_k=3)

        print(f"✅ Retrieved {len(results)} relevant document chunks")

        # Step 3: Show results
        print("\n📋 Step 3: Retrieved Content Preview")
        for i, doc in enumerate(results, 1):
            print(f"\n{i}. {doc.get('metadata', {}).get('file_name', 'Unknown')}")
            print(f"   Relevance Score: {doc.get('score', 0):.3f}")
            content = doc.get('content', '')
            preview = content[:150] + "..." if len(content) > 150 else content
            print(f"   Content: {preview}")

        # Step 4: System status
        print("\n📊 Step 4: System Status")
        vector_count = indexer.vector_store.count()
        print(f"✅ Vector store contains {vector_count} indexed chunks")
        print(f"✅ BM25 index built with {len(retriever.bm25_index.doc_len)} documents")

        print("\n🎉 Demo completed successfully!")
        print("\nTo generate actual use cases with LLM:")
        print("1. Add valid API key to .env file")
        print("2. Run: python generate_usecases.py")
        print("3. Or start API server: python main.py")

    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"❌ Demo failed: {e}")
        return False

    return True

if __name__ == "__main__":
    success = demo()
    sys.exit(0 if success else 1)