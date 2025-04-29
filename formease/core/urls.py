from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('home/', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('pdf-summary/', views.pdf_summary, name='pdf_summary'),
    path('resume-builder/', views.resume_builder, name='resume_builder'),
    path('resume/<int:resume_id>/download/', views.download_resume_pdf, name='download_resume_pdf'),
]

