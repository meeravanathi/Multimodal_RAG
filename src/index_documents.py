#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ingestion.indexer import DocumentIndexer
from utils.logger import get_logger

logger = get_logger(__name__)

def main():
    try:
        logger.info("Starting document indexing...")

        indexer = DocumentIndexer()
        total_chunks = indexer.index_all_documents()

        logger.info(f"Indexing completed! Total chunks: {total_chunks}")

    except Exception as e:
        logger.error(f"Indexing failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()