"""
URL patterns for the PDF API
"""
from django.urls import path
from app import views

urlpatterns = [
    path('create_embedded_pdf/', views.CreateEmbeddedPdfView.as_view(), name='create-embedded-pdf'),
    path('extract_embedded_pdf/', views.ExtractEmbeddedPdfView.as_view(), name='extract-embedded-pdf'),
]