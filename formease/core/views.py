from django.shortcuts import render
import fitz  # PyMuPDF
import ollama  # Using Ollama Python package
from django.core.files.storage import FileSystemStorage
import os
import pytesseract
import numpy as np
from django.contrib import messages

# Configure Tesseract path - update this path after installing Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def home(request):
    return render(request, 'core/home.html')

def pdf_summary(request):
    summary = None
    if request.method == 'POST' and request.FILES.get('pdf_file'):
        try:
            pdf_file = request.FILES['pdf_file']
            
            # Validate file type
            if not pdf_file.name.endswith('.pdf'):
                messages.error(request, 'Please upload a valid PDF file.')
                return render(request, 'core/pdf_summary.html')
            
            # Save uploaded file temporarily
            fs = FileSystemStorage()
            filename = fs.save(pdf_file.name, pdf_file)
            file_path = fs.path(filename)

            # Extract text from PDF
            doc = fitz.open(file_path)
            text = ""
            
            for page_num, page in enumerate(doc, 1):
                try:
                    # Try regular text extraction first
                    regular_text = page.get_text()
                    
                    # If no text is found or text is very short, try OCR
                    if not regular_text or len(regular_text.strip()) < 50:
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
                    else:
                        text += regular_text
                except Exception as e:
                    messages.warning(request, f'Warning: Could not process page {page_num} properly. Using partial text.')
                    text += regular_text
                    
            doc.close()
            

            if not text.strip():
                messages.error(request, 'Could not extract any text from the PDF. Please make sure the file contains readable text.')
                return render(request, 'core/pdf_summary.html')

            # Call Ollama for summarization
            try:
                prompt = f"Summarize the following text in bullet points:\n{text}"
                response = ollama.chat(
                    model='llama3',
                    messages=[{"role": "user", "content": prompt}]
                )
                summary = response['message']['content']
                messages.success(request, 'Summary generated successfully!')
            except Exception as e:
                messages.error(request, 'An error occurred while generating the summary. Please try again.')
                return render(request, 'core/pdf_summary.html')

        except Exception as e:
            messages.error(request, f'An error occurred while processing your PDF: {str(e)}')
            return render(request, 'core/pdf_summary.html')

        # Clean up the temporary file
        try:
            os.remove(file_path)
        except OSError:
            pass
        
    return render(request, 'core/pdf_summary.html', {'summary': summary})
