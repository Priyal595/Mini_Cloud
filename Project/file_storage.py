"""
File Storage Module
Handles file upload to Firebase Storage and metadata storage in Firestore
"""

from firebase_config import get_storage_bucket, get_firestore_db
from firebase_admin import firestore
from datetime import datetime
import os

# Maximum file size: 10 MB
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

class FileStorageManager:
    """Manages file upload, metadata storage, and retrieval"""

    def __init__(self):
        self.bucket = get_storage_bucket()
        self.db = get_firestore_db()
        self.collection_name = 'files'

    def upload_file(self, uploaded_file):
        """
        Upload file to Firebase Storage and store metadata in Firestore

        Args:
            uploaded_file: Streamlit UploadedFile object

        Returns:
            dict: Upload result with status and metadata or error message
        """
        try:
            # Validate file size
            file_size = uploaded_file.size
            if file_size > MAX_FILE_SIZE_BYTES:
                return {
                    'success': False,
                    'error': f'File size exceeds {MAX_FILE_SIZE_MB} MB limit'
                }

            # Generate unique filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            original_name = uploaded_file.name
            file_extension = os.path.splitext(original_name)[1]
            unique_filename = f"{timestamp}_{original_name}"

            # Upload to Firebase Storage
            blob = self.bucket.blob(f"uploads/{unique_filename}")
            blob.upload_from_string(
                uploaded_file.getvalue(),
                content_type=uploaded_file.type
            )

            # Make the file publicly accessible (for download)
            blob.make_public()

            # Get download URL
            download_url = blob.public_url

            # Prepare metadata
            metadata = {
                'original_name': original_name,
                'stored_name': unique_filename,
                'size_bytes': file_size,
                'size_mb': round(file_size / (1024 * 1024), 2),
                'mime_type': uploaded_file.type,
                'storage_path': f"uploads/{unique_filename}",
                'download_url': download_url,
                'uploaded_at': datetime.now(),
                'file_extension': file_extension
            }

            # Store metadata in Firestore
            doc_ref = self.db.collection(self.collection_name).document()
            doc_ref.set(metadata)

            return {
                'success': True,
                'metadata': metadata,
                'doc_id': doc_ref.id
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_all_files(self):
        """
        Retrieve all file metadata from Firestore

        Returns:
            list: List of dictionaries containing file metadata
        """
        try:
            files = []
            docs = self.db.collection(self.collection_name).order_by(
                'uploaded_at', direction=firestore.Query.DESCENDING
            ).stream()

            for doc in docs:
                file_data = doc.to_dict()
                file_data['id'] = doc.id
                files.append(file_data)

            return files

        except Exception as e:
            print(f"Error retrieving files: {str(e)}")
            return []

    def delete_file(self, doc_id, storage_path):
        """
        Delete file from Storage and remove metadata from Firestore

        Args:
            doc_id: Firestore document ID
            storage_path: Path to file in Firebase Storage

        Returns:
            dict: Deletion result
        """
        try:
            # Delete from Storage
            blob = self.bucket.blob(storage_path)
            blob.delete()

            # Delete from Firestore
            self.db.collection(self.collection_name).document(doc_id).delete()

            return {
                'success': True,
                'message': 'File deleted successfully'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_storage_stats(self):
        """
        Get storage statistics

        Returns:
            dict: Storage statistics
        """
        try:
            files = self.get_all_files()
            total_files = len(files)
            total_size_bytes = sum(f.get('size_bytes', 0) for f in files)
            total_size_mb = round(total_size_bytes / (1024 * 1024), 2)

            return {
                'total_files': total_files,
                'total_size_bytes': total_size_bytes,
                'total_size_mb': total_size_mb
            }

        except Exception as e:
            print(f"Error getting storage stats: {str(e)}")
            return {
                'total_files': 0,
                'total_size_bytes': 0,
                'total_size_mb': 0
            }
