from django.db import models
from django.contrib.auth.models import User

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Personal Information
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    location = models.CharField(max_length=100)
    summary = models.TextField()
    
    # Education
    education = models.JSONField()  # Store multiple education entries
    
    # Experience
    experience = models.JSONField()  # Store multiple experience entries
    
    # Skills
    skills = models.JSONField()  # Store skills with categories
    
    # Generated Content
    generated_content = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name}'s Resume - {self.created_at.strftime('%Y-%m-%d')}"

class PDFSummary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    file_name = models.CharField(max_length=255)
    summary = models.TextField()
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'PDF Summaries'
    
    def __str__(self):
        return f"{self.file_name} - {self.created_at.strftime('%Y-%m-%d')}"
