import os
import uuid
import firebase_admin
from firebase_admin import credentials, storage
from google.cloud import storage as gcloud_storage

# Download Firebase credentials from Firebase Storage
def download_firebase_credentials():
    bucket_name = 'postergoats-ai.appspot.com'  # Your Firebase Storage bucket name
    credentials_file_path = 'firebase_service_account.json'  # Path of the credentials in Firebase Storage
    
    # Initialize Google Cloud Storage client
    client = gcloud_storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(credentials_file_path)

    # Download the file to the local directory
    blob.download_to_filename(credentials_file_path)
    return credentials_file_path

# Ensure Firebase Admin SDK is initialized with downloaded credentials
FIREBASE_CREDENTIALS_FILE = download_firebase_credentials()  # This will download the file
FIREBASE_STORAGE_BUCKET = os.getenv("FIREBASE_STORAGE_BUCKET")  # e.g. postergoats.appspot.com

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
