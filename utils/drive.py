import os
import io
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
from typing import List, Dict, Optional

class GoogleDriveService:
    def __init__(self):
        self.drive_service = self._initialize_drive_service()

    def _initialize_drive_service(self):
        """Initialize and return the Google Drive service with proper error handling"""
        try:
            # Load service account credentials from environment variable
            json_str = os.getenv("GOOGLE_SERVICE_ACCOUNT")
            if not json_str:
                raise ValueError("GOOGLE_SERVICE_ACCOUNT environment variable not set")

            # Handle escaped newlines in private key
            json_str = json_str.replace('\\n', '\n')
            service_account_info = json.loads(json_str)

            credentials = service_account.Credentials.from_service_account_info(
                service_account_info,
                scopes=["https://www.googleapis.com/auth/drive"]
            )
            return build('drive', 'v3', credentials=credentials)

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in service account: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Drive service: {str(e)}")

    def list_files_in_folder(self, folder_id: str) -> List[Dict[str, str]]:
        """List all video files in the specified Google Drive folder"""
        try:
            query = f"'{folder_id}' in parents and mimeType contains 'video/'"
            results = self.drive_service.files().list(
                q=query,
                fields="files(id, name)",
                supportsAllDrives=True,
                includeItemsFromAllDrives=True
            ).execute()
            return results.get('files', [])
        except HttpError as error:
            print(f"Google Drive API error: {error}")
            return []

    def download_file(self, file_id: str, file_name: str, output_dir: str = "videos") -> Optional[str]:
        """Download a file from Google Drive to local storage"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            file_path = os.path.join(output_dir, file_name)

            # Skip if file already exists
            if os.path.exists(file_path):
                return file_path

            # Initialize download
            request = self.drive_service.files().get_media(
                fileId=file_id,
                supportsAllDrives=True
            )
            
            # Download with progress tracking
            with io.FileIO(file_path, 'wb') as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    print(f"Download progress: {int(status.progress() * 100)}%")

            return file_path

        except HttpError as error:
            print(f"Google Drive download error: {error}")
            # Clean up partially downloaded file if exists
            if os.path.exists(file_path):
                os.remove(file_path)
            return None
        except Exception as e:
            print(f"Unexpected error during download: {str(e)}")
            return None


# Example usage:
if __name__ == "__main__":
    try:
        drive = GoogleDriveService()
        
        # List files in folder
        folder_id = "YOUR_FOLDER_ID"
        files = drive.list_files_in_folder(folder_id)
        print(f"Found files: {files}")
        
        # Download first file
        if files:
            file_id = files[0]['id']
            file_name = files[0]['name']
            downloaded_path = drive.download_file(file_id, file_name)
            print(f"Downloaded to: {downloaded_path}")
            
    except Exception as e:
        print(f"Application error: {str(e)}")