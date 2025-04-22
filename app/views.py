"""
Views for the PDF API
"""
import base64
import io
from typing import List

from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser, FileUploadParser
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse

from app.serializers import CreateEmbeddedPdfSerializer, ExtractEmbeddedPdfSerializer
from app.pdf_utils import embed_pdfs, extract_pdfs


class CreateEmbeddedPdfView(APIView):
    """
    Embeds multiple PDFs into a host PDF.
    """
    parser_classes = [JSONParser]
    
    @extend_schema(
        request=CreateEmbeddedPdfSerializer,
        responses={
            200: OpenApiResponse(
                description="Modified PDF with embedded files",
                content={"application/pdf": {}}
            )
        },
        description="Embeds multiple PDFs into a host PDF",
        examples=[
            OpenApiExample(
                name="Embedding PDFs",
                description="Example of embedding two PDFs into a host PDF",
                value={
                    "host_pdf": "base64_encoded_pdf_content",
                    "attachments": [
                        "base64_encoded_pdf_attachment_1",
                        "base64_encoded_pdf_attachment_2"
                    ]
                },
                request_only=True
            )
        ]
    )
    def post(self, request):
        """
        Embed multiple PDFs into a host PDF.
        """
        serializer = CreateEmbeddedPdfSerializer(data=request.data)
        
        if serializer.is_valid():
            # Decode base64 host PDF
            try:
                host_pdf_bytes = base64.b64decode(serializer.validated_data['host_pdf'])
            except Exception as e:
                return Response(
                    {"error": f"Failed to decode host PDF: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Decode base64 attachments
            attachment_bytes_list = []
            try:
                for i, attachment in enumerate(serializer.validated_data['attachments']):
                    attachment_bytes = base64.b64decode(attachment)
                    attachment_bytes_list.append(attachment_bytes)
            except Exception as e:
                return Response(
                    {"error": f"Failed to decode attachment {i+1}: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Process PDFs
            try:
                result_bytes = embed_pdfs(host_pdf_bytes, attachment_bytes_list)
            except Exception as e:
                return Response(
                    {"error": f"Failed to embed PDFs: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Return the modified PDF
            response = HttpResponse(result_bytes, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="embedded_pdf.pdf"'
            return response
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExtractEmbeddedPdfView(APIView):
    """
    Extracts embedded PDFs from a PDF.
    """
    parser_classes = [FileUploadParser]
    
    @extend_schema(
        request={
            'application/pdf': OpenApiResponse(description="PDF file with embedded attachments")
        },
        responses={
            200: OpenApiResponse(
                description="ZIP file containing extracted PDFs",
                content={"application/zip": {}}
            )
        },
        description="Extracts all embedded PDFs from a PDF and returns them as a ZIP archive"
    )
    def post(self, request):
        """
        Extract embedded PDFs from a PDF.
        """
        if not request.data or 'file' not in request.data:
            # Read raw body instead
            if hasattr(request, 'body') and request.body:
                pdf_bytes = request.body
            else:
                return Response(
                    {"error": "No PDF provided"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            pdf_bytes = request.data['file'].read()
        
        # Process PDF
        try:
            attachments, zip_bytes = extract_pdfs(pdf_bytes)
            
            if not attachments:
                return Response(
                    {"error": "No PDF attachments found in the provided PDF"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Return ZIP archive with extracted PDFs
            response = HttpResponse(zip_bytes, content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="extracted_pdfs.zip"'
            return response
            
        except Exception as e:
            return Response(
                {"error": f"Failed to extract PDFs: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )