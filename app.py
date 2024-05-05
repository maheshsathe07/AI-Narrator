from flask import Flask, render_template, request
import google.generativeai as genai
from openai import OpenAI
from project import *
import json

app = Flask(__name__)

@app.route('/')
def index():
    # return "Hello World!"
    return render_template('index.html')

@app.route('/upload')
def upload():
    return render_template('generate.html')

@app.route('/generateSummary', methods=['POST'])
def generateSummary():
    video = request.files['video']
    video.save('static/videos/input.mp4')
    video_path = "static/videos/input.mp4"
    base64_frames = video_to_base64(video_path)
    script = generate_script_gemini(base64_frames)
    print(script)
    audio_path = generate_audio(script)
    add_voiceover(audio_path, video_path)
    return render_template('preview.html', video="result.mp4", audio = "voiceover.wav")

@app.route('/hello')
def hello():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run()