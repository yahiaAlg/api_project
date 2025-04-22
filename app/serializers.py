"""
Serializers for the PDF API
"""
from rest_framework import serializers


class CreateEmbeddedPdfSerializer(serializers.Serializer):
    """
    Serializer for embedding PDFs into a host PDF
    """
    host_pdf = serializers.CharField(help_text="Base64-encoded host PDF")
    attachments = serializers.ListField(
        child=serializers.CharField(),
        help_text="List of Base64-encoded PDFs to embed"
    )
    
    def validate_host_pdf(self, value):
        """Validate host_pdf is a Base64-encoded string"""
        try:
            # Just validation, not actual decoding
            value.encode('ascii')
            return value
        except (UnicodeEncodeError, AttributeError):
            raise serializers.ValidationError("host_pdf must be a valid Base64-encoded string")
    
    def validate_attachments(self, value):
        """Validate each attachment is a Base64-encoded string"""
        for i, attachment in enumerate(value):
            try:
                # Just validation, not actual decoding
                attachment.encode('ascii')
            except (UnicodeEncodeError, AttributeError):
                raise serializers.ValidationError(f"Attachment {i+1} must be a valid Base64-encoded string")
        return value


class ExtractEmbeddedPdfSerializer(serializers.Serializer):
    """
    Serializer for extracting embedded PDFs
    
    Note: This serializer doesn't actually validate anything since the input
    is raw binary data and is handled in the view directly.
    """
    pass