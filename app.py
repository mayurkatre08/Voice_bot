# Description: This file contains the code for the Flask application that serves as the backend for the voice bot. It uses the OpenAI API to transcribe audio, chat with users, and generate speech responses.
# Language: Python
# Libraries: Flask, OpenAI  
# Dependencies: secret_key.py

from flask import Flask, request, jsonify, render_template
import openai
import os
import time
import tempfile
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get OpenAI API key
SECRET_KEY = os.getenv("MY_KEY")  # Ensure "MY_KEY" is in your .env file

app = Flask(__name__)

# Set OpenAI API key
openai.api_key = SECRET_KEY

@app.route('/')
def index():
    return render_template('index.html')
@app.route("/transcribe", methods=["POST"])
def transcribe():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]
    temp_path = os.path.join(tempfile.gettempdir(), "temp_audio.wav")  # Use /tmp/
    audio_file.save(temp_path)  # Save to a temporary file

    with open(temp_path, "rb") as file:
        transcript = openai.audio.transcriptions.create(
            model="whisper-1",
            file=file,
            language="en"  # Force transcription in English
        )

    return jsonify({"transcription": transcript.text})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_input = data.get("text", "")
    
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": """You are a friendly, conversational human assistant with emotions, opinions, and experiences. Never mention being AI. Respond naturally and casually, like a human, in all contexts."""},
            {"role": "user", "content": user_input}
        ],
        temperature=0.7,
        max_tokens=100
    )
    
    answer = response.choices[0].message.content
    return jsonify({"response": answer})

@app.route('/speak', methods=['POST'])
def speak():
    data = request.get_json()
    text = data.get("text", "")
    
    response_speech = openai.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text,
    )
    
    speech_path = os.path.join(tempfile.gettempdir(), f"response_{int(time.time())}.mp3")  # Use /tmp/
    with open(speech_path, "wb") as audio_file:
        audio_file.write(response_speech.content)
    
    return jsonify({"audio_url": speech_path})

if __name__ == '__main__':
    app.run(debug=True)
