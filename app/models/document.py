from ..extensions import db  # Changed from 'from app import db'
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from flask import current_app, url_for # Added url_for for get_url method
from enum import Enum


class DocumentType(Enum):
    """Types of documents that can be uploaded."""
    ID_PROOF = 'id_proof'
    ADDRESS_PROOF = 'address_proof'
    BANK_STATEMENT = 'bank_statement'
    TAX_DOCUMENT = 'tax_document'
    INVOICE = 'invoice'
    RECEIPT = 'receipt'
    CONTRACT = 'contract'
    OTHER = 'other'


class DocumentStatus(Enum):
    """Status values for document verification."""
    PENDING = 'pending'  # Awaiting review
    APPROVED = 'approved'  # Document verified and approved
    REJECTED = 'rejected'  # Document rejected (with reason)
    EXPIRED = 'expired'  # Document has expired
    UNDER_REVIEW = 'under_review'  # Currently being reviewed
    RESUBMISSION_REQUESTED = 'resubmission_requested'  # Need to resubmit
    VERIFIED = 'verified'  # Document verified (final approval)

class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    # Changed payment_id to be nullable True here, as it might be associated with other entities later.
    # If a document *must* always belong to a payment, keep nullable=False.
    # For a general Document model, it's safer to make it nullable or use a polymorphic approach.
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'), nullable=True, index=True) 
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # invoice, receipt, proof, other
    path = db.Column(db.String(255), nullable=False) # Stores the relative path within UPLOAD_FOLDER
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(255))
    
    # Relationship: 'documents' on Payment will back-populate to 'payments' here
    payment = db.relationship('Payment', back_populates='documents')

    def __init__(self, payment_id, file, type, description=None):
        self.payment_id = payment_id
        self.type = type
        self.description = description
        
        # Save the file
        filename = secure_filename(file.filename)
        # Construct the upload directory path relative to current_app.instance_path
        upload_dir = os.path.join(current_app.instance_path, current_app.config['UPLOAD_FOLDER'], 'documents')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename to prevent conflicts
        base_name, extension = os.path.splitext(filename)
        counter = 1
        unique_filename = filename
        while os.path.exists(os.path.join(upload_dir, unique_filename)):
            unique_filename = f"{base_name}_{counter}{extension}"
            counter += 1
        file.save(os.path.join(upload_dir, unique_filename))
        self.name = unique_filename
        self.path = os.path.join('documents', unique_filename)

    def delete(self):
        """Delete the document file from storage and the database record."""
        if self.path:
            # Construct the absolute path from the stored relative path
            file_path = os.path.join(current_app.instance_path, current_app.config['UPLOAD_FOLDER'], self.path)
            if os.path.exists(file_path):
                os.remove(file_path)
        db.session.delete(self)
        db.session.commit()

    def get_absolute_path(self):
        """Get the absolute path to the document file."""
        if self.path:
            return os.path.join(current_app.instance_path, current_app.config['UPLOAD_FOLDER'], self.path)
        return None

    def get_url(self):
        """Get the URL to download the document.
        Requires a Flask route (e.g., in admin_routes or client_routes) to serve this file.
        """
        # Ensure 'admin.download_document' or a similar endpoint is defined in your routes
        if self.id:
            # This 'admin.download_document' needs to be a real endpoint.
            # If it's for clients, it might be 'client.download_document' etc.
            # For this example, assuming an admin route exists.
            try:
                return url_for('admin.download_document', document_id=self.id, _external=True)
            except RuntimeError:
                # This can happen if called outside of an active request context
                current_app.logger.warning("url_for called outside of application context for document URL.")
                return f"/uploads/{self.path}" # Fallback, adjust based on your static file serving
        return None

    @staticmethod
    def allowed_file(filename):
        """Check if file extension is allowed."""
        allowed_extensions = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'txt'} # Added .txt for example
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

    @staticmethod
    def validate_file(file):
        """Validate file size and type."""
        if not file:
            return False, "No file provided"
        
        if not Document.allowed_file(file.filename):
            return False, "File type not allowed"
            
        # MAX_CONTENT_LENGTH is typically in bytes, ensure it's set in your config
        max_size_mb = current_app.config.get('MAX_UPLOAD_SIZE_MB', 5) # Default to 5MB
        if file.content_length > max_size_mb * 1024 * 1024:
            return False, f"File size exceeds limit ({max_size_mb}MB)"
        
        return True, "File valid"

