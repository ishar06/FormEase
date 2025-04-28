from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('pdf-summary/', views.pdf_summary, name='pdf_summary'),
]

