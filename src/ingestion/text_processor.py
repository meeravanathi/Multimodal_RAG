import yaml
import json
import csv
from typing import Dict, Any
from pathlib import Path
from utils.logger import get_logger

logger = get_logger(__name__)

class TextProcessor:
    
    @staticmethod
    def process_text(file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.debug(f"Processed text file: {Path(file_path).name}")
            return content
        except Exception as e:
            logger.error(f"Error processing text file {file_path}: {e}")
            return ""
    
    @staticmethod
    def process_markdown(file_path: str) -> str:
        return TextProcessor.process_text(file_path)
    
    @staticmethod
    def process_yaml(file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            content = f"YAML File: {Path(file_path).name}\n\n"
            content += yaml.dump(data, default_flow_style=False, sort_keys=False)
            
            logger.debug(f"Processed YAML file: {Path(file_path).name}")
            return content
        except Exception as e:
            logger.error(f"Error processing YAML file {file_path}: {e}")
            return TextProcessor.process_text(file_path)
    
    @staticmethod
    def process_json(file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            content = f"JSON File: {Path(file_path).name}\n\n"
            content += json.dumps(data, indent=2)
            
            logger.debug(f"Processed JSON file: {Path(file_path).name}")
            return content
        except Exception as e:
            logger.error(f"Error processing JSON file {file_path}: {e}")
            return TextProcessor.process_text(file_path)
    
    @staticmethod
    def process_csv(file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            content = f"CSV File: {Path(file_path).name}\n\n"
            if rows:
                content += f"Columns: {', '.join(rows[0].keys())}\n"
                content += f"Total Rows: {len(rows)}\n\n"
                content += "Sample Data (first 5 rows):\n"
                for i, row in enumerate(rows[:5], 1):
                    content += f"\nRow {i}:\n"
                    for key, value in row.items():
                        content += f"  {key}: {value}\n"
            
            logger.debug(f"Processed CSV file: {Path(file_path).name}")
            return content
        except Exception as e:
            logger.error(f"Error processing CSV file {file_path}: {e}")
            return TextProcessor.process_text(file_path)