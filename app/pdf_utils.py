"""
Utility functions for PDF manipulation
"""
import io
import zipfile
from PyPDF2 import PdfReader, PdfWriter
from typing import List, Dict, Tuple, Any, Optional


def embed_pdfs(host_pdf_bytes: bytes, attachment_bytes_list: List[bytes]) -> bytes:
    """
    Embeds multiple PDFs into a host PDF.
    
    Args:
        host_pdf_bytes: Bytes of the host PDF
        attachment_bytes_list: List of bytes objects for the PDFs to embed
        
    Returns:
        Bytes of the modified PDF with embedded files
    """
    # Load the host PDF
    pdf_stream = io.BytesIO(host_pdf_bytes)
    pdf_reader = PdfReader(pdf_stream)
    pdf_writer = PdfWriter()
    
    # Copy all pages from the reader to the writer
    for page in pdf_reader.pages:
        pdf_writer.add_page(page)
    
    # Add attachments
    for i, attachment_bytes in enumerate(attachment_bytes_list):
        filename = f"attachment_{i+1}.pdf"
        pdf_writer.add_attachment(filename, attachment_bytes)
    
    # Save the new PDF to a bytes buffer
    output_stream = io.BytesIO()
    pdf_writer.write(output_stream)
    output_stream.seek(0)
    
    return output_stream.getvalue()


def extract_pdfs(pdf_bytes: bytes) -> Tuple[List[Dict[str, Any]], bytes]:
    """
    Extract all embedded PDFs from a PDF.
    
    Args:
        pdf_bytes: Bytes of the PDF with embedded files
        
    Returns:
        Tuple containing:
        - List of dictionaries with attachment info (name, bytes)
        - ZIP file containing all extracted PDFs as bytes
    """
    pdf_stream = io.BytesIO(pdf_bytes)
    pdf_reader = PdfReader(pdf_stream)
    
    # Get all attachments
    attachments = []
    
    if hasattr(pdf_reader, 'attachments'):
        for attachment in pdf_reader.attachments:
            if attachment.filename.lower().endswith('.pdf'):
                attachments.append({
                    'name': attachment.filename,
                    'bytes': attachment.content
                })
    
    # Create a ZIP file with all attachments
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for attachment in attachments:
            zip_file.writestr(attachment['name'], attachment['bytes'])
    
    zip_buffer.seek(0)
    
    return attachments, zip_buffer.getvalue()