import os
import io
import json
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# Load credentials from environment variable
try:
    SERVICE_ACCOUNT_INFO = json.loads(os.getenv("GOOGLE_SERVICE_ACCOUNT"))
except Exception as e:
    logging.error("Failed to load GOOGLE_SERVICE_ACCOUNT: %s", e)
    raise RuntimeError("Missing or invalid GOOGLE_SERVICE_ACCOUNT environment variable")

SCOPES = ["https://www.googleapis.com/auth/drive"]
credentials = service_account.Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)

def list_files_in_folder(folder_id):
    query = f"'{folder_id}' in parents"
    results = drive_service.files().list(q=query, fields="files(id, name, mimeType)").execute()
    
    # Only keep video files
    return [
        file for file in results.get('files', [])
        if file['mimeType'].startswith('video/')
    ]

def download_file(file_id, file_name, output_dir="videos"):
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, file_name)

    # Skip if already downloaded
    if os.path.exists(file_path):
        return file_path

    request = drive_service.files().get_media(fileId=file_id)
    fh = io.FileIO(file_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    return file_path
