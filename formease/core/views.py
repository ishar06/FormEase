from django.shortcuts import render
import fitz  # PyMuPDF
import ollama  # Using Ollama Python package
from django.core.files.storage import FileSystemStorage

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
            text += page.get_text()
        doc.close()

        # Call Ollama for summarization
        prompt = f"Summarize the following text in bullet points:\n{text}"
        
        response = ollama.chat(
            model='llama3',  # or whatever model you are running
            messages=[{"role": "user", "content": prompt}]
        )
        summary = response['message']['content']

    return render(request, 'core/pdf_summary.html', {'summary': summary})
