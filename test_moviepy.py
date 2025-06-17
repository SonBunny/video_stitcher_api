try:
    from moviepy.editor import VideoFileClip, concatenate_videoclips
    print("MoviePy imported successfully!")
    print(f"Version: {VideoFileClip.__version__}")
except ImportError as e:
    print(f"Error: {e}")