from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
import fitz  # PyMuPDF
import ollama  # Using Ollama Python package
from django.core.files.storage import FileSystemStorage
import os
import pytesseract
import numpy as np
import json
from .models import Resume
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.utils.html import escape

# Configure Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def landing(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'core/landing.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Successfully logged in!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
            
    return render(request, 'core/login.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    
    return render(request, 'core/register.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Successfully logged out!')
    return redirect('landing')

@login_required
def home(request):
    return render(request, 'core/home.html')

@login_required
def pdf_summary(request):
    # ... existing pdf_summary code ...
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
            
            # Clean up the temporary file
            try:
                os.remove(file_path)
            except OSError:
                pass

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

    return render(request, 'core/pdf_summary.html', {'summary': summary})

@login_required
def download_resume_pdf(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    template = get_template('core/resume_pdf.html')
    html = template.render({'resume_content': resume.generated_content})
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{resume.full_name}_resume.pdf"'
    
    # Convert HTML to PDF
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)
    return response

@login_required
def resume_builder(request):
    if request.method == 'POST':
        try:
            # Extract form data
            data = {
                'full_name': escape(request.POST['full_name']),
                'email': escape(request.POST['email']),
                'phone': escape(request.POST['phone']),
                'location': escape(request.POST['location']),
                'summary': escape(request.POST['summary']),
                'education': [],
                'experience': [],
                'skills': []
            }
            
            # Process education entries
            education_count = 0
            while f'education[{education_count}][degree]' in request.POST:
                education = {
                    'degree': escape(request.POST[f'education[{education_count}][degree]']),
                    'institution': escape(request.POST[f'education[{education_count}][institution]']),
                    'start_date': escape(request.POST[f'education[{education_count}][start_date]']),
                    'end_date': escape(request.POST.get(f'education[{education_count}][end_date]', 'Present'))
                }
                data['education'].append(education)
                education_count += 1
            
            # Process experience entries
            experience_count = 0
            while f'experience[{experience_count}][title]' in request.POST:
                experience = {
                    'title': escape(request.POST[f'experience[{experience_count}][title]']),
                    'company': escape(request.POST[f'experience[{experience_count}][company]']),
                    'start_date': escape(request.POST[f'experience[{experience_count}][start_date]']),
                    'end_date': escape(request.POST.get(f'experience[{experience_count}][end_date]', 'Present')),
                    'description': escape(request.POST[f'experience[{experience_count}][description]'])
                }
                data['experience'].append(experience)
                experience_count += 1
            
            # Process skills entries
            skills_count = 0
            while f'skills[{skills_count}][category]' in request.POST:
                skills = {
                    'category': escape(request.POST[f'skills[{skills_count}][category]']),
                    'skills': [escape(s.strip()) for s in request.POST[f'skills[{skills_count}][skills]'].split(',')]
                }
                data['skills'].append(skills)
                skills_count += 1
            
            # Generate resume content using Ollama
            prompt = """Create a professional resume using HTML markup with the following information. Do not write any prefix, do only what you are told, no prefix or suffix. i don't want anything like 'Here is the professional resume in HTML markup:' in the beginning. Follow the HTML structure exactly:

<h1>{full_name}</h1>
<div class="contact-info">
<p>Email: <a href="mailto:{email}">{email}</a><br>
Phone: {phone}<br>
Location: {location}</p>
</div>

<div class="section">
<h2 class="section-title">Professional Summary</h2>
<p>{summary}</p>
</div>

<div class="section">
<h2 class="section-title">Education</h2>
""".format(**data)

            # Add education entries
            for edu in data['education']:
                prompt += f"""
<div class="entry">
<div class="entry-title">{edu['degree']}</div>
<div class="entry-subtitle">{edu['institution']}</div>
<div class="entry-date">{edu['start_date']} - {edu['end_date']}</div>
</div>"""

            prompt += """
</div>

<div class="section">
<h2 class="section-title">Experience</h2>
"""

            # Add experience entries
            for exp in data['experience']:
                prompt += f"""
<div class="entry">
<div class="entry-title">{exp['title']}</div>
<div class="entry-subtitle">{exp['company']}</div>
<div class="entry-date">{exp['start_date']} - {exp['end_date']}</div>
<p>{exp['description']}</p>
</div>"""

            prompt += """
</div>

<div class="section">
<h2 class="section-title">Skills</h2>
"""

            # Add skills entries
            for skill in data['skills']:
                prompt += f"""
<div class="skills-category">
<h3>{skill['category']}</h3>
<ul class="skills-list">
"""
                for s in skill['skills']:
                    prompt += f"<li>{s}</li>"
                prompt += """
</ul>
</div>"""

            prompt += """
</div>"""

            response = ollama.chat(
                model='llama3',
                messages=[{"role": "user", "content": prompt}]
            )
            
            generated_content = response['message']['content']
            
            # Clean up the generated HTML by removing any AI prefixes and code block markers
            unwanted_prefixes = [
                "Here is the HTML code for the professional resume:",
                "```html",
                "```",
                "Here's the formatted resume:",
                "Here's your professional resume:"
            ]
            for prefix in unwanted_prefixes:
                generated_content = generated_content.replace(prefix, "")
            generated_content = generated_content.strip()
            
            # Save to database
            resume = Resume(
                user=request.user,
                full_name=data['full_name'],
                email=data['email'],
                phone=data['phone'],
                location=data['location'],
                summary=data['summary'],
                education=data['education'],
                experience=data['experience'],
                skills=data['skills'],
                generated_content=generated_content
            )
            resume.save()
            
            messages.success(request, 'Resume generated successfully!')
            return render(request, 'core/resume_builder.html', {
                'resume_content': generated_content,
                'resume_id': resume.id
            })
            
        except Exception as e:
            messages.error(request, f'An error occurred while generating your resume: {str(e)}')
            return render(request, 'core/resume_builder.html')
    
    return render(request, 'core/resume_builder.html')
