import os
import uuid
import firebase_admin
from firebase_admin import credentials, storage

# Path to your Firebase service account JSON
FIREBASE_CREDENTIALS_FILE = "firebase_service_account.json"

# Bucket name from your Firebase project
FIREBASE_STORAGE_BUCKET = os.getenv("FIREBASE_STORAGE_BUCKET")  # e.g. postergoats.appspot.com

# Initialize Firebase App
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CREDENTIALS_FILE)
    firebase_admin.initialize_app(cred, {
        'storageBucket': FIREBASE_STORAGE_BUCKET
    })

def upload_to_firebase(file_path):
    """Uploads a local file to Firebase Storage and returns its public URL"""
    bucket = storage.bucket()
    blob_name = f"generated_posters/{uuid.uuid4().hex}_{os.path.basename(file_path)}"
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(file_path)
    blob.make_public()
    return blob.public_url
