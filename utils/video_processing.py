from moviepy.editor import VideoFileClip, concatenate_videoclips
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import tempfile

# Initialize Google Drive service
def get_drive_service():
    creds = service_account.Credentials.from_service_account_info(
        os.getenv("GOOGLE_DRIVE_CREDENTIALS_JSON"),
        scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )
    return build("drive", "v3", credentials=creds)

async def stitch_videos(ingredients: list, output_path: str):
    drive_service = get_drive_service()
    
    # Search for videos matching ingredients
    matched_videos = []
    for ingredient in ingredients:
        query = f"name contains '{ingredient}' and mimeType contains 'video/'"
        results = drive_service.files().list(
            q=query,
            fields="files(id, name)",
            corpora="allDrives",
            includeItemsFromAllDrives=True,
            supportsAllDrives=True
        ).execute()
        
        if results.get("files"):
            matched_videos.append(results["files"][0]["id"])
    
    if not matched_videos:
        raise ValueError("No videos matched the ingredients")
    
    # Download matched videos to temp files
    clips = []
    with tempfile.TemporaryDirectory() as temp_dir:
        for i, video_id in enumerate(matched_videos):
            request = drive_service.files().get_media(fileId=video_id)
            temp_path = os.path.join(temp_dir, f"temp_{i}.mp4")
            
            with open(temp_path, "wb") as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
            
            clips.append(VideoFileClip(temp_path))
        
        # Concatenate videos
        final_clip = concatenate_videoclips(clips, method="compose")
        final_clip.write_videofile(output_path, codec="libx264")
    
    return output_path