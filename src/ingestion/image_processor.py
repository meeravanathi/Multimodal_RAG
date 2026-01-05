import base64
from pathlib import Path
from PIL import Image
from typing import Optional
from utils.logger import get_logger

logger = get_logger(__name__)

class ImageProcessor:
    
    @staticmethod
    def process_image_with_ocr(file_path: str) -> str:
        try:
            import pytesseract
            
            img = Image.open(file_path)
            text = pytesseract.image_to_string(img)
            
            if text.strip():
                content = f"Image OCR: {Path(file_path).name}\n"
                content += f"Extracted Text:\n{text}"
                logger.debug(f"OCR processed image: {Path(file_path).name}")
                return content
            else:
                logger.warning(f"No text extracted from image: {Path(file_path).name}")
                return f"Image: {Path(file_path).name} (no text detected)"
                
        except ImportError:
            logger.warning("pytesseract not installed, skipping OCR")
            return f"Image: {Path(file_path).name} (OCR not available)"
        except Exception as e:
            logger.error(f"Error processing image {file_path}: {e}")
            return f"Image: {Path(file_path).name} (processing failed)"
    
    @staticmethod
    def encode_image_base64(file_path: str) -> Optional[str]:
        try:
            with open(file_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encoding image {file_path}: {e}")
            return None
    
    @staticmethod
    def get_image_description_placeholder(file_path: str) -> str:
        try:
            img = Image.open(file_path)
            width, height = img.size
            format_name = img.format or "unknown"
            
            content = f"Image File: {Path(file_path).name}\n"
            content += f"Format: {format_name}\n"
            content += f"Dimensions: {width}x{height} pixels\n"
            content += "Note: For detailed image analysis, consider using a vision model.\n"
            
            return content
        except Exception as e:
            logger.error(f"Error getting image info {file_path}: {e}")
            return f"Image: {Path(file_path).name}"