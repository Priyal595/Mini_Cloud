"""
Firebase Configuration Module
Initializes Firebase Admin SDK and provides access to Storage and Firestore
"""

import firebase_admin
from firebase_admin import credentials, storage, firestore
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Flag to track initialization
_initialized = False

def initialize_firebase():
    """
    Initialize Firebase Admin SDK
    Should be called once at the start of the application
    """
    global _initialized

    if _initialized:
        return

    try:
        # Get credentials path from environment
        cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
        storage_bucket = os.getenv('FIREBASE_STORAGE_BUCKET')

        if not cred_path or not storage_bucket:
            raise ValueError(
                "Missing Firebase configuration. Please set FIREBASE_CREDENTIALS_PATH "
                "and FIREBASE_STORAGE_BUCKET in your .env file"
            )

        # Initialize Firebase Admin
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred, {
            'storageBucket': storage_bucket
        })

        _initialized = True
        print("✅ Firebase initialized successfully")

    except Exception as e:
        print(f"❌ Error initializing Firebase: {str(e)}")
        raise

def get_storage_bucket():
    """
    Get Firebase Storage bucket instance
    Returns: storage.bucket() instance
    """
    if not _initialized:
        initialize_firebase()
    return storage.bucket()

def get_firestore_db():
    """
    Get Firestore database instance
    Returns: firestore.client() instance
    """
    if not _initialized:
        initialize_firebase()
    return firestore.client()
