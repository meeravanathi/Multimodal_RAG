#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from config import settings
    print("✓ Config loaded successfully")

    from utils.logger import get_logger
    logger = get_logger(__name__)
    print("✓ Logger loaded successfully")

    from ingestion.file_loader import FileLoader
    print("✓ File loader loaded successfully")

    print("All basic imports work!")
    print(f"Input directory: {settings.vector_db_path}")

except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)