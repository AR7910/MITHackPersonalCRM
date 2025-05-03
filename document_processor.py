import PyPDF2
import easyocr
import numpy as np
from PIL import Image
import io
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_file):
    """
    Extract text from a PDF file
    Args:
        pdf_file: A file-like object containing the PDF
    Returns:
        str: Extracted text from the PDF
    """
    try:
        text = ""
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        logger.info(f"PDF has {len(pdf_reader.pages)} pages")
        
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            page_text = page.extract_text()
            text += page_text + "\n\n"
        
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise

def extract_text_from_image(image_file):
    """
    Extract text from an image using OCR
    Args:
        image_file: A file-like object containing the image
    Returns:
        str: Extracted text from the image
    """
    try:
        # Initialize EasyOCR reader
        reader = easyocr.Reader(['en'])
        
        # Open and process the image
        image_bytes = image_file.read()
        image = Image.open(io.BytesIO(image_bytes))
        image_np = np.array(image)
        
        # Perform OCR
        logger.info("Performing OCR on image")
        results = reader.readtext(image_np)
        
        # Combine results
        text = " ".join([result[1] for result in results])
        
        return text
    except Exception as e:
        logger.error(f"Error extracting text from image: {str(e)}")
        raise

def process_document(file, file_type):
    """
    Process a document based on its type and extract text
    Args:
        file: A file-like object
        file_type: The MIME type of the file
    Returns:
        str: Extracted text from the document
    """
    try:
        if 'pdf' in file_type.lower():
            return extract_text_from_pdf(file)
        elif 'image' in file_type.lower():
            return extract_text_from_image(file)
        else:
            error_msg = f"Unsupported file type: {file_type}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise
