from typing import List
import os
from ingestion.file_loader import FileLoader, FileMetadata
from ingestion.text_processor import TextProcessor
from ingestion.pdf_processor import PDFProcessor
from ingestion.image_processor import ImageProcessor
from ingestion.chunker import SmartChunker, Chunk
from retriever.vector_store import VectorStore
from utils.logger import get_logger
from utils.metrics import metrics_collector

logger = get_logger(__name__)

class DocumentIndexer:
    
    def __init__(self, input_dir: str = None):
        if input_dir is None:
            # Get the project root (parent of src directory)
            current_file = os.path.abspath(__file__)
            ingestion_dir = os.path.dirname(current_file)  # src/ingestion
            src_dir = os.path.dirname(ingestion_dir)       # src
            project_root = os.path.dirname(src_dir)        # project root
            input_dir = os.path.join(project_root, "data", "input")
        logger.info(f"Using input directory: {input_dir}")
        self.file_loader = FileLoader(input_dir)
        self.text_processor = TextProcessor()
        self.pdf_processor = PDFProcessor()
        self.image_processor = ImageProcessor()
        self.chunker = SmartChunker()
        self.vector_store = VectorStore()
    
    def index_all_documents(self) -> int:
        metric = metrics_collector.track("full_indexing")
        
        files = self.file_loader.discover_files()
        if not files:
            logger.warning("No files found to index")
            return 0
        
        total_chunks = 0
        for file_meta in files:
            chunks = self._process_file(file_meta)
            if chunks:
                self.vector_store.add_documents(chunks)
                total_chunks += len(chunks)
        
        metric.stop().add_metadata(files_processed=len(files), total_chunks=total_chunks)
        logger.info(f"Indexed {len(files)} files into {total_chunks} chunks")
        return total_chunks
    
    def _process_file(self, file_meta: FileMetadata) -> List[Chunk]:
        logger.info(f"Processing: {file_meta.file_name} ({file_meta.file_type})")
        
        try:
            content = self._extract_content(file_meta)
            if not content:
                logger.warning(f"No content extracted from {file_meta.file_name}")
                return []
            
            metadata = file_meta.to_dict()
            chunks = self.chunker.chunk_text(content, file_meta.file_name, metadata)
            
            logger.info(f"Created {len(chunks)} chunks from {file_meta.file_name}")
            return chunks
            
        except Exception as e:
            logger.error(f"Error processing {file_meta.file_name}: {e}")
            return []
    
    def _extract_content(self, file_meta: FileMetadata) -> str:
        file_type = file_meta.file_type
        file_path = file_meta.file_path
        
        processors = {
            'text': lambda: self.text_processor.process_text(file_path),
            'markdown': lambda: self.text_processor.process_markdown(file_path),
            'yaml': lambda: self.text_processor.process_yaml(file_path),
            'json': lambda: self.text_processor.process_json(file_path),
            'csv': lambda: self.text_processor.process_csv(file_path),
            'pdf': lambda: self.pdf_processor.process_pdf(file_path),
            'image': lambda: self._process_image_content(file_path),
        }
        
        processor = processors.get(file_type)
        if processor:
            return processor()
        else:
            logger.warning(f"No processor for type: {file_type}")
            return ""
    
    def _process_image_content(self, file_path: str) -> str:
        ocr_text = self.image_processor.process_image_with_ocr(file_path)
        description = self.image_processor.get_image_description_placeholder(file_path)
        return f"{description}\n\n{ocr_text}"
    
    def clear_index(self):
        self.vector_store.clear()
        logger.info("Cleared all indexed documents")