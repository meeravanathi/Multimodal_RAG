from typing import List, Dict, Any
from difflib import SequenceMatcher
from utils.logger import get_logger

logger = get_logger(__name__)

class Deduplicator:
    
    @staticmethod
    def deduplicate_chunks(chunks: List[Dict[str, Any]], similarity_threshold: float = 0.85) -> List[Dict[str, Any]]:
        
        if len(chunks) <= 1:
            return chunks
        
        unique_chunks = []
        seen_content = []
        
        for chunk in chunks:
            content = chunk.get('content', '')
            
            is_duplicate = False
            for seen in seen_content:
                similarity = SequenceMatcher(None, content, seen).ratio()
                if similarity >= similarity_threshold:
                    is_duplicate = True
                    logger.debug(f"Removed duplicate chunk (similarity: {similarity:.2f})")
                    break
            
            if not is_duplicate:
                unique_chunks.append(chunk)
                seen_content.append(content)
        
        removed = len(chunks) - len(unique_chunks)
        if removed > 0:
            logger.info(f"Removed {removed} duplicate chunks")
        
        return unique_chunks
    
    @staticmethod
    def deduplicate_by_source(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        
        seen_sources = set()
        unique_chunks = []
        
        for chunk in chunks:
            source = chunk.get('metadata', {}).get('source_file', '')
            chunk_id = chunk.get('chunk_id', '')
            
            if chunk_id not in seen_sources:
                unique_chunks.append(chunk)
                seen_sources.add(chunk_id)
        
        return unique_chunks
    
    @staticmethod
    def merge_similar_chunks(chunks: List[Dict[str, Any]], similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        
        if len(chunks) <= 1:
            return chunks
        
        merged = []
        skip_indices = set()
        
        for i, chunk1 in enumerate(chunks):
            if i in skip_indices:
                continue
            
            content1 = chunk1.get('content', '')
            merged_content = content1
            
            for j, chunk2 in enumerate(chunks[i+1:], start=i+1):
                if j in skip_indices:
                    continue
                
                content2 = chunk2.get('content', '')
                similarity = SequenceMatcher(None, content1, content2).ratio()
                
                if similarity >= similarity_threshold:
                    if content2 not in merged_content:
                        merged_content += "\n" + content2
                    skip_indices.add(j)
            
            merged_chunk = chunk1.copy()
            merged_chunk['content'] = merged_content
            merged.append(merged_chunk)
        
        return merged