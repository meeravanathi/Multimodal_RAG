#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from generation.usecase_generator import UseCaseGenerator
from utils.logger import get_logger

logger = get_logger(__name__)

def main():
    try:
        logger.info("Starting use case generation...")

        generator = UseCaseGenerator()
        query = "Generate test cases for user authentication and payment processing"
        result = generator.generate(query, debug_mode=True)

        logger.info(f"Generation completed! Got {len(result.get('use_cases', []))} use cases")

        # Print results
        print("\n" + "="*50)
        print("GENERATED USE CASES")
        print("="*50)

        for i, uc in enumerate(result.get('use_cases', []), 1):
            print(f"\n{i}. {uc.get('title', 'No title')}")
            print(f"   Goal: {uc.get('goal', 'No goal')}")
            print(f"   Preconditions: {uc.get('preconditions', [])}")
            print(f"   Steps: {len(uc.get('steps', []))} steps")

        print(f"\nConfidence Score: {result.get('confidence_score', 0):.2f}")
        print(f"Warnings: {result.get('warnings', [])}")
        print(f"Assumptions: {result.get('assumptions', [])}")

    except Exception as e:
        logger.error(f"Generation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()