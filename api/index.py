"""
Clawdbot API - Flask backend for Vercel
"""

import os
import base64
import tempfile
from flask import Flask, request, jsonify

from zhipuai import ZhipuAI

app = Flask(__name__)

# Initialize ZhipuAI client
ZHIPU_API_KEY = os.getenv("ZHIPUAI_API_KEY", "507b2d0bb71945aab07c0e22bc666d4a.RiY1d2GYmM0Eodp3")
client = ZhipuAI(api_key=ZHIPU_API_KEY)

# Conversation history (in production, use Redis/database)
conversations = {}


@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok", "message": "Clawdbot API is running"})


@app.route("/api/transcribe", methods=["POST"])
def transcribe():
    """Transcribe audio using GLM-ASR-2512 cloud API."""
    try:
        data = request.get_json()

        if "audio_base64" not in data:
            return jsonify({"error": "audio_base64 required"}), 400

        # Decode base64 audio
        audio_bytes = base64.b64decode(data["audio_base64"])

        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_bytes)
            temp_path = f.name

        # Transcribe with GLM-ASR-2512
        with open(temp_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="glm-asr-2512",
                file=audio_file
            )

        # Clean up
        os.unlink(temp_path)

        return jsonify({
            "text": response.text,
            "success": True
        })

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@app.route("/api/chat", methods=["POST"])
def chat():
    """Chat with GLM-4.7."""
    try:
        data = request.get_json()

        if "message" not in data:
            return jsonify({"error": "message required"}), 400

        session_id = data.get("session_id", "default")
        user_message = data["message"]

        # Get or create conversation history
        if session_id not in conversations:
            conversations[session_id] = [{
                "role": "system",
                "content": """You are Clawdbot, a helpful voice assistant.
                Keep responses concise (2-3 sentences) since they will be spoken aloud.
                Be friendly, helpful, and conversational."""
            }]

        # Add user message
        conversations[session_id].append({
            "role": "user",
            "content": user_message
        })

        # Call GLM-4.7
        response = client.chat.completions.create(
            model="glm-4.7",
            messages=conversations[session_id]
        )

        assistant_message = response.choices[0].message.content

        # Save to history
        conversations[session_id].append({
            "role": "assistant",
            "content": assistant_message
        })

        return jsonify({
            "response": assistant_message,
            "success": True
        })

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@app.route("/api/voice-chat", methods=["POST"])
def voice_chat():
    """Complete voice chat: transcribe + respond."""
    try:
        data = request.get_json()

        if "audio_base64" not in data:
            return jsonify({"error": "audio_base64 required"}), 400

        session_id = data.get("session_id", "default")

        # Step 1: Transcribe
        audio_bytes = base64.b64decode(data["audio_base64"])

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_bytes)
            temp_path = f.name

        with open(temp_path, "rb") as audio_file:
            asr_response = client.audio.transcriptions.create(
                model="glm-asr-2512",
                file=audio_file
            )

        os.unlink(temp_path)
        transcription = asr_response.text

        # Step 2: Chat with GLM-4.7
        if session_id not in conversations:
            conversations[session_id] = [{
                "role": "system",
                "content": """You are Clawdbot, a helpful voice assistant.
                Keep responses concise (2-3 sentences) since they will be spoken aloud.
                Be friendly, helpful, and conversational."""
            }]

        conversations[session_id].append({
            "role": "user",
            "content": transcription
        })

        chat_response = client.chat.completions.create(
            model="glm-4.7",
            messages=conversations[session_id]
        )

        assistant_message = chat_response.choices[0].message.content

        conversations[session_id].append({
            "role": "assistant",
            "content": assistant_message
        })

        return jsonify({
            "transcription": transcription,
            "response": assistant_message,
            "success": True
        })

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@app.route("/api/reset", methods=["POST"])
def reset():
    """Reset conversation history."""
    data = request.get_json() or {}
    session_id = data.get("session_id", "default")

    if session_id in conversations:
        del conversations[session_id]

    return jsonify({"success": True, "message": "Conversation reset"})


if __name__ == "__main__":
    app.run(debug=True, port=3000)
