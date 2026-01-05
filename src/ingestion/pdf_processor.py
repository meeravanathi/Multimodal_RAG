import fitz
from pathlib import Path
from typing import List, Tuple
from utils.logger import get_logger

logger = get_logger(__name__)

class PDFProcessor:
    
    @staticmethod
    def process_pdf(file_path: str) -> str:
        try:
            doc = fitz.open(file_path)
            content = f"PDF Document: {Path(file_path).name}\n"
            content += f"Total Pages: {len(doc)}\n\n"
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                
                if text.strip():
                    content += f"--- Page {page_num + 1} ---\n"
                    content += text
                    content += "\n\n"
            
            doc.close()
            logger.debug(f"Processed PDF: {Path(file_path).name} ({len(doc)} pages)")
            return content
            
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {e}")
            return ""
    
    @staticmethod
    def extract_images_from_pdf(file_path: str) -> List[Tuple[int, bytes]]:
        images = []
        try:
            doc = fitz.open(file_path)
            for page_num in range(len(doc)):
                page = doc[page_num]
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    images.append((page_num + 1, image_bytes))
            
            doc.close()
            logger.debug(f"Extracted {len(images)} images from PDF: {Path(file_path).name}")
            return images
            
        except Exception as e:
            logger.error(f"Error extracting images from PDF {file_path}: {e}")
            return []