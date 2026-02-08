"""
NomadAI Voice Agent API - Flask backend for Vercel
Integrates GLM models with intelligent skill routing.
"""

import os
import sys
import base64
import tempfile
import asyncio
from typing import Dict, Any, List
from flask import Flask, request, jsonify

from zhipuai import ZhipuAI

# Add src to path for skill imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.skills import get_all_skills
from src.skills.concierge import (
    RoomServiceSkill,
    HousekeepingSkill,
    AmenitiesSkill,
    WifiSkill,
)
from src.skills.sightseeing import (
    RecommendationSkill,
    ItinerarySkill,
    DirectionsSkill,
)
from src.skills.media import (
    ImagePreviewSkill,
    VideoTourSkill,
)

app = Flask(__name__)

# Initialize ZhipuAI client
ZHIPU_API_KEY = os.getenv("ZHIPUAI_API_KEY")
if not ZHIPU_API_KEY:
    raise ValueError("ZHIPUAI_API_KEY environment variable is required")
client = ZhipuAI(api_key=ZHIPU_API_KEY)

# Initialize skills
SKILLS = get_all_skills()

# Conversation history (in production, use Redis/database)
conversations = {}


def route_intent(transcription: str) -> Dict[str, Any]:
    """
    Route user utterance to the appropriate skill using GLM-4.7.

    Args:
        transcription: The user's transcribed speech

    Returns:
        Dict with matched skill name and confidence
    """
    # Build skill descriptions for intent classification
    skills_description = "\n".join([
        f"- {skill.name}: {skill.description}\n  Examples: {', '.join(skill.example_utterances[:3])}"
        for skill in SKILLS
    ])

    messages = [
        {
            "role": "system",
            "content": f"""You are an intent classification system.
            Given a user utterance, determine which skill should handle it.

            Available Skills:
            {skills_description}

            Respond with ONLY the skill name (e.g., "room_service", "wifi_help", "local_recommendations").
            If no skill matches, respond with "general_chat"."""
        },
        {
            "role": "user",
            "content": transcription
        }
    ]

    response = client.chat.completions.create(
        model="glm-4.7",
        messages=messages,
        temperature=0.1  # Low temperature for consistent classification
    )

    skill_name = response.choices[0].message.content.strip().lower()

    # Find matching skill
    for skill in SKILLS:
        if skill.name == skill_name:
            return {
                "skill": skill,
                "skill_name": skill_name,
                "matched": True
            }

    return {
        "skill": None,
        "skill_name": "general_chat",
        "matched": False
    }


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "ok",
        "message": "NomadAI Voice Agent API is running",
        "skills": [skill.name for skill in SKILLS]
    })


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
    """Text-based chat with skill routing (for testing without audio)."""
    try:
        data = request.get_json()

        if "message" not in data:
            return jsonify({"error": "message required"}), 400

        session_id = data.get("session_id", "default")
        user_message = data["message"]

        # Route to appropriate skill
        intent_result = route_intent(user_message)

        # Execute skill or fallback to general chat
        if intent_result["matched"] and intent_result["skill"]:
            skill = intent_result["skill"]

            context = {
                "transcription": user_message,
                "session_id": session_id,
                "location": "Tokyo",
                "hotel_location": "Shibuya Grand Hotel",
            }

            # Run async skill execution
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            skill_result = loop.run_until_complete(skill.execute(context))
            loop.close()

            assistant_message = skill_result["response"]

            return jsonify({
                "response": assistant_message,
                "skill_used": intent_result["skill_name"],
                "action": skill_result.get("action"),
                "metadata": skill_result.get("metadata", {}),
                "image_url": skill_result.get("image_url"),
                "video_task_id": skill_result.get("task_id"),
                "success": True
            })

        else:
            # Fallback to general chat
            if session_id not in conversations:
                conversations[session_id] = [{
                    "role": "system",
                    "content": """You are NomadAI, a helpful hotel voice assistant.
                    Keep responses concise (2-3 sentences) since they will be spoken aloud.
                    Be friendly, helpful, and conversational."""
                }]

            conversations[session_id].append({
                "role": "user",
                "content": user_message
            })

            response = client.chat.completions.create(
                model="glm-4.7",
                messages=conversations[session_id]
            )

            assistant_message = response.choices[0].message.content

            conversations[session_id].append({
                "role": "assistant",
                "content": assistant_message
            })

            return jsonify({
                "response": assistant_message,
                "skill_used": "general_chat",
                "success": True
            })

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@app.route("/api/voice-chat", methods=["POST"])
def voice_chat():
    """Complete voice chat: transcribe + route + respond with skills."""
    try:
        data = request.get_json()

        if "audio_base64" not in data:
            return jsonify({"error": "audio_base64 required"}), 400

        session_id = data.get("session_id", "default")

        # Step 1: Transcribe with GLM-ASR-2512
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

        # Step 2: Route to appropriate skill
        intent_result = route_intent(transcription)

        # Step 3: Execute skill or fallback to general chat
        if intent_result["matched"] and intent_result["skill"]:
            # Execute the matched skill
            skill = intent_result["skill"]

            # Build context for skill execution
            context = {
                "transcription": transcription,
                "session_id": session_id,
                "location": "Tokyo",  # In production, get from user profile
                "hotel_location": "Shibuya Grand Hotel",
            }

            # Run async skill execution in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            skill_result = loop.run_until_complete(skill.execute(context))
            loop.close()

            assistant_message = skill_result["response"]

            # Save to conversation history
            if session_id not in conversations:
                conversations[session_id] = []

            conversations[session_id].append({
                "role": "user",
                "content": transcription
            })
            conversations[session_id].append({
                "role": "assistant",
                "content": assistant_message
            })

            return jsonify({
                "transcription": transcription,
                "response": assistant_message,
                "skill_used": intent_result["skill_name"],
                "action": skill_result.get("action"),
                "metadata": skill_result.get("metadata", {}),
                "image_url": skill_result.get("image_url"),
                "video_task_id": skill_result.get("task_id"),
                "success": True
            })

        else:
            # Fallback to general chat
            if session_id not in conversations:
                conversations[session_id] = [{
                    "role": "system",
                    "content": """You are NomadAI, a helpful hotel voice assistant.
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
                "skill_used": "general_chat",
                "success": True
            })

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@app.route("/api/video-status/<task_id>", methods=["GET"])
def video_status(task_id):
    """Check video generation status."""
    try:
        from src.skills.media import check_video_status

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(check_video_status(task_id))
        loop.close()

        return jsonify({
            "success": True,
            **result
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
