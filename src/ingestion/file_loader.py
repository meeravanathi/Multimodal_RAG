import os
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass
from utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class FileMetadata:
    file_path: str
    file_name: str
    file_type: str
    file_size: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "file_name": self.file_name,
            "file_type": self.file_type,
            "file_size": self.file_size
        }

class FileLoader:
    SUPPORTED_EXTENSIONS = {
        '.txt': 'text',
        '.md': 'markdown',
        '.pdf': 'pdf',
        '.docx': 'docx',
        '.doc': 'doc',
        '.png': 'image',
        '.jpg': 'image',
        '.jpeg': 'image',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.json': 'json',
        '.csv': 'csv',
        '.xlsx': 'excel',
        '.xls': 'excel'
    }
    
    def __init__(self, input_dir: str = "./data/input"):
        self.input_dir = Path(input_dir)
        logger.info(f"FileLoader input_dir: {self.input_dir} (exists: {self.input_dir.exists()})")
        if not self.input_dir.exists():
            self.input_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created input directory: {self.input_dir}")
    
    def discover_files(self) -> List[FileMetadata]:
        files = []
        for file_path in self.input_dir.rglob('*'):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext in self.SUPPORTED_EXTENSIONS:
                    metadata = FileMetadata(
                        file_path=str(file_path),
                        file_name=file_path.name,
                        file_type=self.SUPPORTED_EXTENSIONS[ext],
                        file_size=file_path.stat().st_size
                    )
                    files.append(metadata)
                    logger.debug(f"Discovered: {file_path.name} ({metadata.file_type})")
        
        logger.info(f"Discovered {len(files)} supported files")
        return files
    
    def load_file(self, file_path: str) -> bytes:
        with open(file_path, 'rb') as f:
            return f.read()
    
    def get_file_type(self, file_path: str) -> str:
        ext = Path(file_path).suffix.lower()
        return self.SUPPORTED_EXTENSIONS.get(ext, 'unknown')