from fastapi import FastAPI
from pydantic import BaseModel
from moviepy.editor import VideoFileClip, concatenate_videoclips
from drive_utils import list_files_in_folder, download_file
from fastapi.responses import FileResponse
import os

app = FastAPI()

# Replace this with your actual Google Drive folder ID
FOLDER_ID = "1522x_bLGrJn5CjlCeMYuqNvRJU7xR7mg"

class IngredientsRequest(BaseModel):
    ingredients: list[str]

@app.post("/generate-video")
def generate_video(request: IngredientsRequest):
    files = list_files_in_folder(FOLDER_ID)
    matched_videos = []

    for ingredient in request.ingredients:
        for file in files:
            if ingredient.lower() in file['name'].lower():
                path = download_file(file['id'], file['name'])
                matched_videos.append(path)
                break

    if not matched_videos:
        return {"error": "No matching videos found"}

    clips = [VideoFileClip(path) for path in matched_videos]
    final_clip = concatenate_videoclips(clips, method="compose")

    output_path = "videos/output_video.mp4"
    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

    return {"message": "Video created", "video_url": "/video"}

@app.get("/video")
def get_video():
    return FileResponse("videos/output_video.mp4", media_type="video/mp4")
