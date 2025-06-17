from fastapi import FastAPI
from pydantic import BaseModel
from moviepy.editor import VideoFileClip, concatenate_videoclips
from utils.drive import list_files_in_folder, download_file
from fastapi.responses import FileResponse
import os
import logging

app = FastAPI()

FOLDER_ID = "1522x_bLGrJn5CjlCeMYuqNvRJU7xR7mg"

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

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

                try:
                    clip = VideoFileClip(path)
                    matched_videos.append(clip)
                    break
                except Exception as e:
                    logging.warning(f"Skipping invalid video '{file['name']}': {e}")
                    continue

    if not matched_videos:
        return {"error": "No valid matching videos found"}

    final_clip = concatenate_videoclips(matched_videos, method="compose")
    
    output_path = "videos/output_video.mp4"
    os.makedirs("videos", exist_ok=True)
    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

    # Cleanup
    for clip in matched_videos:
        clip.close()

    return {"message": "Video created", "video_url": "/video"}

@app.get("/video")
def get_video():
    if not os.path.exists("videos/output_video.mp4"):
        return {"error": "Video not found"}, 404
    return FileResponse("videos/output_video.mp4", media_type="video/mp4")
