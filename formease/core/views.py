from django.shortcuts import render
import fitz  # PyMuPDF
import ollama  # Using Ollama Python package
from django.core.files.storage import FileSystemStorage
import os
import pytesseract
from django.conf import settings
import numpy as np

# Configure Tesseract path - update this path after installing Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def home(request):
    return render(request, 'core/home.html')

def pdf_summary(request):
    summary = None
    if request.method == 'POST' and request.FILES['pdf_file']:
        pdf_file = request.FILES['pdf_file']
        
        # Save uploaded file temporarily
        fs = FileSystemStorage()
        filename = fs.save(pdf_file.name, pdf_file)
        file_path = fs.path(filename)

        # Extract text from PDF
        doc = fitz.open(file_path)
        text = ""
        
        for page in doc:
            # Try regular text extraction first
            regular_text = page.get_text()
            
            # If no text is found or text is very short, try OCR
            if not regular_text or len(regular_text.strip()) < 50:
                try:
                    # Convert PDF page to image with higher DPI for better OCR
                    zoom = 2  # zoom factor
                    mat = fitz.Matrix(zoom, zoom)
                    pix = page.get_pixmap(matrix=mat)
                    
                    # Get the image data as bytes
                    img_bytes = pix.samples
                    
                    # Convert to numpy array and reshape
                    img_array = np.frombuffer(img_bytes, dtype=np.uint8)
                    img_array = img_array.reshape(pix.height, pix.width, pix.n)
                    
                    # Perform OCR directly on the image array
                    ocr_text = pytesseract.image_to_string(img_array)
                    text += ocr_text if ocr_text else ""
                except Exception as e:
                    # If OCR fails, fall back to regular text
                    text += regular_text
                    print(f"OCR failed: {str(e)}")
            else:
                text += regular_text
                
        doc.close()
        
        # Clean up the temporary file
        try:
            os.remove(file_path)
        except OSError:
            pass

        # Call Ollama for summarization
        prompt = f"Summarize the following text in bullet points:\n{text}"
        
        response = ollama.chat(
            model='llama3',  # or whatever model you are running
            messages=[{"role": "user", "content": prompt}]
        )
        summary = response['message']['content']

    return render(request, 'core/pdf_summary.html', {'summary': summary})
