#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from retriever.hybrid_retriever import HybridRetriever
from utils.logger import get_logger

logger = get_logger(__name__)

def main():
    try:
        logger.info("Testing retrieval...")

        retriever = HybridRetriever()
        query = "Generate test cases for user authentication and payment processing"
        results = retriever.retrieve(query, top_k=5)

        logger.info(f"Retrieved {len(results)} documents")

        print("\n" + "="*50)
        print("RETRIEVED DOCUMENTS")
        print("="*50)

        for i, doc in enumerate(results, 1):
            print(f"\n{i}. Source: {doc.get('metadata', {}).get('file_name', 'Unknown')}")
            print(f"   Score: {doc.get('score', 0):.3f}")
            content = doc.get('content', '')[:200] + "..." if len(doc.get('content', '')) > 200 else doc.get('content', '')
            print(f"   Content: {content}")

        print(f"\nTotal retrieved: {len(results)}")

    except Exception as e:
        logger.error(f"Retrieval failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()