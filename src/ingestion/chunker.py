import re
from typing import List, Dict, Any
from dataclasses import dataclass
from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class Chunk:
    content: str
    chunk_id: str
    source_file: str
    chunk_index: int
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "chunk_id": self.chunk_id,
            "source_file": self.source_file,
            "chunk_index": self.chunk_index,
            "metadata": self.metadata
        }

class SmartChunker:
    
    def __init__(self, chunk_size: int = None, overlap: int = None):
        self.chunk_size = chunk_size or settings.chunk_size
        self.overlap = overlap or settings.chunk_overlap
    
    def chunk_text(self, text: str, source_file: str, metadata: Dict[str, Any] = None) -> List[Chunk]:
        if not text or not text.strip():
            return []
        
        metadata = metadata or {}
        
        paragraphs = self._split_into_paragraphs(text)
        chunks = []
        current_chunk = ""
        chunk_index = 0
        
        for para in paragraphs:
            if len(current_chunk) + len(para) <= self.chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk.strip():
                    chunk = self._create_chunk(
                        current_chunk.strip(),
                        source_file,
                        chunk_index,
                        metadata
                    )
                    chunks.append(chunk)
                    chunk_index += 1
                
                if len(para) > self.chunk_size:
                    sub_chunks = self._split_large_paragraph(para)
                    for sub in sub_chunks:
                        chunk = self._create_chunk(
                            sub,
                            source_file,
                            chunk_index,
                            metadata
                        )
                        chunks.append(chunk)
                        chunk_index += 1
                    current_chunk = ""
                else:
                    current_chunk = para + "\n\n"
        
        if current_chunk.strip():
            chunk = self._create_chunk(
                current_chunk.strip(),
                source_file,
                chunk_index,
                metadata
            )
            chunks.append(chunk)
        
        chunks = self._add_overlap(chunks)
        
        logger.debug(f"Created {len(chunks)} chunks from {source_file}")
        return chunks
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        paragraphs = re.split(r'\n\s*\n', text)
        return [p.strip() for p in paragraphs if p.strip()]
    
    def _split_large_paragraph(self, paragraph: str) -> List[str]:
        sentences = re.split(r'(?<=[.!?])\s+', paragraph)
        chunks = []
        current = ""
        
        for sentence in sentences:
            if len(current) + len(sentence) <= self.chunk_size:
                current += sentence + " "
            else:
                if current.strip():
                    chunks.append(current.strip())
                current = sentence + " "
        
        if current.strip():
            chunks.append(current.strip())
        
        return chunks
    
    def _create_chunk(self, content: str, source_file: str, chunk_index: int, metadata: Dict[str, Any]) -> Chunk:
        chunk_id = f"{source_file}_{chunk_index}"
        return Chunk(
            content=content,
            chunk_id=chunk_id,
            source_file=source_file,
            chunk_index=chunk_index,
            metadata=metadata
        )
    
    def _add_overlap(self, chunks: List[Chunk]) -> List[Chunk]:
        if len(chunks) <= 1 or self.overlap == 0:
            return chunks
        
        for i in range(1, len(chunks)):
            prev_content = chunks[i-1].content
            overlap_text = prev_content[-self.overlap:] if len(prev_content) > self.overlap else prev_content
            chunks[i].content = overlap_text + "\n..." + chunks[i].content
        
        return chunks