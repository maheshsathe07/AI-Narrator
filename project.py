from IPython.display import display, Audio
import google.generativeai as genai
import requests
import base64
from moviepy.editor import *
import json
import cv2

# Approximation: 1 second = 30 frames
# Approximation: 1 frame = 760 tokens
def video_to_base64(video_path):
    video = cv2.VideoCapture(video_path)

    base64Frames = []
    while video.isOpened():
        success, frame = video.read()
        
        if not success:
            break
        
        _, buffer = cv2.imencode(".png", frame)
        base64Frames.append(base64.b64encode(buffer).decode("utf-8"))

    video.release()
    print(len(base64Frames), "frames read.")
    return base64Frames



def generate_script_gemini(base64Frames):
    with open("config.json", 'r') as f:
        config = json.load(f)
        credentials = config['params']
        
        genai.configure(api_key=credentials['gemini_api_key'])
    
    generation_config = {
      "temperature": 0.4,
      "top_p": 1,
      "top_k": 32,
      "max_output_tokens": 4096,
    }

    safety_settings = [
      {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
      },
      {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
      },
      {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
      },
      {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
      },
    ]

    model = genai.GenerativeModel(model_name="gemini-pro-vision",
                                  generation_config=generation_config,
                                  safety_settings=safety_settings
                                )

    image_parts = [
        {
            "mime_type": "image/png",  # Change mime_type if using a different format
            "data": base64_frame
        } for base64_frame in base64Frames[0::200]
    ]

    prompt_parts = [
        {"text": "These are frames of a video. Create a short voiceover script by a commentator as if it was a live match. Note: Only include the narration & do not include timestamp.Striclty upto 50 words only."},
    ] + image_parts

    response = model.generate_content(prompt_parts)
    return response.text

def generate_audio(script):
    with open("config.json", 'r') as f:
        config = json.load(f)
        credentials = config['params']
        
    url = "https://v2.api.audio/speech/tts/sync"

    payload = {
        "sampling_rate": "24000",
        "bitrate": "192",
        "speed": 0.80,
        "text": script,
        # "voice": "Bronson"
        "voice": "Joanna"
        # "effect": "chewie"
    }
    headers = {
        "Accept": "audio/wav",
        "content-type": "application/json",
        "x-api-key": credentials['audiostack_api_key']
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        file_path = "static/audios/voiceover.wav"

        with open(file_path, 'wb') as file:
            file.write(response.content)

        print(f"Audio saved to {file_path}")
        return file_path

    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def add_voiceover(audio_path, video_path):
    

    video_clip = VideoFileClip(video_path)
    audio_clip = AudioFileClip(audio_path)

    video_clip = video_clip.set_audio(audio_clip)

    video_clip.write_videofile("static\\videos\\result.mp4", codec="libx264", audio_codec="aac")


def video_transcript(video_path):
    pass