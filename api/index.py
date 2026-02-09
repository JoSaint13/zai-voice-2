"""
NomadAI Voice Agent API - Flask backend for Vercel
Integrates GLM models with intelligent skill routing.
"""

import os
import sys
import json
import base64
import sqlite3
import logging
import tempfile
import asyncio
import traceback
from typing import Dict, Any, List
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
import requests

try:
    from zhipuai import ZhipuAI
except ImportError:
    ZhipuAI = None

# Load env vars
load_dotenv()

# Logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Paths
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'hotels.db')
PUBLIC_DIR = os.path.join(os.path.dirname(__file__), '..', 'public')

# Z.AI API config
ZAI_BASE_URL = os.getenv('ZAI_BASE_URL', 'https://open.bigmodel.cn')
ZAI_API_KEY = os.getenv('ZHIPUAI_API_KEY', '')
ZAI_HEADERS = {
    'Authorization': f'Bearer {ZAI_API_KEY}',
    'Content-Type': 'application/json'
}

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
# Initialize ZhipuAI client (optional - app runs in demo mode without it)
ZHIPU_API_KEY = os.getenv("ZHIPUAI_API_KEY")
if ZHIPU_API_KEY and ZhipuAI:
    client = ZhipuAI(api_key=ZHIPU_API_KEY)
else:
    client = None
    logger.warning("ZhipuAI client not initialized - running in demo mode")

# Initialize skills
SKILLS = get_all_skills()

# Conversation history (in production, use Redis/database)
conversations = {}

def get_hotel_context(hotel_id):
    """Retrieve hotel details and recommendations from SQLite."""
    try:
        if not os.path.exists(DB_PATH):
            return None, []
            
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Fetch hotel details
            cursor.execute("SELECT name, knowledge_base FROM hotels WHERE id = ?", (hotel_id,))
            hotel_row = cursor.fetchone()
            
            if not hotel_row:
                return None, []
                
            hotel = dict(hotel_row)
            
            # Fetch recommendations
            cursor.execute("SELECT name, category, description, opening_hours FROM recommendations WHERE hotel_id = ?", (hotel_id,))
            recs_rows = cursor.fetchall()
            recommendations = [dict(row) for row in recs_rows]
            
            return hotel, recommendations
    except Exception as e:
        print(f"Error fetching hotel context: {e}")
        return None, []


def get_user_friendly_error(exception):
    """Convert technical errors to user-friendly messages."""
    error_type = type(exception).__name__
    error_str = str(exception)
    
    # Handle specific error types
    if 'APITimeoutError' in error_type or 'timeout' in error_str.lower():
        return "⏱️ The AI service is taking too long to respond. Please check your internet connection and try again."
    
    if 'ConnectTimeout' in error_type or 'ConnectError' in error_type:
        return "🔌 Unable to connect to the AI service. Please check your internet connection or try again later."
    
    if 'AuthenticationError' in error_type or 'authentication' in error_str.lower():
        return "🔑 Authentication failed. Please check your API key configuration."
    
    if 'APIConnectionError' in error_type:
        return "🌐 Network connection error. Please check your internet and try again."
    
    if 'RateLimitError' in error_type or '429' in error_str or '1113' in error_str:
        return "⚠️ API quota exceeded. Running in demo mode."
    
    if 'InvalidRequestError' in error_type:
        return "❌ Invalid request. Please try rephrasing your message."
    
    # Generic fallback
    return f"⚠️ Something went wrong: {error_str[:100]}. Please try again."


def generate_demo_response(user_message, hotel_info=None, recommendations=None):
    """Generate a demo response when the API is unavailable (balance low, etc)."""
    msg_lower = user_message.lower()
    
    # Knowledge base queries
    if any(word in msg_lower for word in ['breakfast', 'morning', 'eat']):
        if hotel_info and hotel_info.get('knowledge_base'):
            kb = hotel_info['knowledge_base']
            # Extract breakfast info if present
            if 'breakfast' in kb.lower():
                import re
                match = re.search(r'breakfast[^.]*\.', kb, re.IGNORECASE)
                if match:
                    return f"📋 {match.group(0)} [Demo Mode]"
        return "Breakfast is typically served from 7:00 AM to 10:30 AM in our main dining room. [Demo Mode]"
    
    if any(word in msg_lower for word in ['wifi', 'internet', 'password']):
        return "The WiFi network is 'GrandBudapest_Guest' and the password is available at the front desk. [Demo Mode]"
    
    if any(word in msg_lower for word in ['checkout', 'check out', 'late']):
        return "Standard checkout is at 11:00 AM. Late checkout can be arranged for an additional fee - would you like me to request that? [Demo Mode]"
    
    if any(word in msg_lower for word in ['pool', 'gym', 'spa', 'fitness']):
        return "Our pool and fitness center are located on the 3rd floor and are open from 6:00 AM to 10:00 PM. [Demo Mode]"
    
    if any(word in msg_lower for word in ['restaurant', 'food', 'dining', 'dinner', 'lunch']):
        if recommendations:
            rec = next((r for r in recommendations if r['category'] == 'restaurant'), None)
            if rec:
                return f"I recommend {rec['name']}: {rec['description']} [Demo Mode]"
        return "We have excellent dining options available. The main restaurant serves lunch from 12-3 PM and dinner from 6-10 PM. [Demo Mode]"
    
    if any(word in msg_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good evening']):
        hotel_name = hotel_info['name'] if hotel_info else "our hotel"
        return f"Hello! Welcome to {hotel_name}. How may I assist you today? [Demo Mode]"
    
    # Default response
    return f"Thank you for your question. In demo mode, I can help with common queries about breakfast times, WiFi, checkout, and local recommendations. [Demo Mode]"


@app.route("/api/logs", methods=["POST"])
def client_logs():
    """Receive logs from the frontend."""
    try:
        data = request.get_json()
        log_level = data.get("level", "info").lower()
        message = data.get("message", "No message")
        context = data.get("context", {})
        
        log_msg = f"[FRONTEND] {message} | Context: {json.dumps(context)}"
        
        if log_level == "error":
            logger.error(log_msg)
        elif log_level == "warn":
            logger.warning(log_msg)
        else:
            logger.info(log_msg)
            
        return jsonify({"status": "logged"})
    except Exception as e:
        logger.error(f"Failed to process client log: {e}")
        return jsonify({"error": "Logging failed"}), 500


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


@app.route("/api/ping", methods=["GET"])
def ping():
    """Test API connectivity to ZhipuAI via raw HTTP (no SDK retries)."""
    import time
    import jwt

    results = {"api_key": "configured" if ZHIPU_API_KEY else "missing", "tests": []}

    if not ZAI_API_KEY:
        results["tests"].append({"model": "all", "status": "skip", "detail": "No API key configured"})
        return jsonify(results)

    # Generate JWT token (same way ZhipuAI SDK does it)
    def make_token(api_key):
        parts = api_key.split(".")
        if len(parts) != 2:
            return api_key  # fallback to raw key
        kid, secret = parts
        payload = {
            "api_key": kid,
            "exp": int(time.time()) + 300,
            "timestamp": int(time.time() * 1000),
        }
        return jwt.encode(payload, secret, algorithm="HS256", headers={"alg": "HS256", "sign_type": "SIGN"})

    try:
        token = make_token(ZAI_API_KEY)
    except Exception as e:
        results["tests"].append({"model": "auth", "status": "error", "detail": f"JWT generation failed: {e}"})
        return jsonify(results)

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Quick connectivity check first
    t0 = time.time()
    try:
        r = requests.get(f"{ZAI_BASE_URL}", timeout=(3, 5))
        ms = int((time.time() - t0) * 1000)
        results["network"] = {"status": "ok", "latency_ms": ms, "base_url": ZAI_BASE_URL}
    except requests.Timeout:
        ms = int((time.time() - t0) * 1000)
        results["network"] = {"status": "timeout", "latency_ms": ms, "base_url": ZAI_BASE_URL,
                              "detail": "Cannot reach API server. If outside China, this API may be geo-blocked."}
        return jsonify(results)
    except Exception as e:
        ms = int((time.time() - t0) * 1000)
        results["network"] = {"status": "error", "latency_ms": ms, "detail": str(e)[:200]}
        return jsonify(results)

    # Test chat models via raw HTTP (NO sdk retries)
    models = ["glm-4-plus", "glm-4.7", "glm-4-flash"]
    for model in models:
        t0 = time.time()
        try:
            r = requests.post(
                f"{ZAI_BASE_URL}/api/paas/v4/chat/completions",
                headers=headers,
                json={"model": model, "messages": [{"role": "user", "content": "Reply: pong"}], "max_tokens": 5},
                timeout=(3, 8),
            )
            ms = int((time.time() - t0) * 1000)
            if r.status_code == 200:
                data = r.json()
                results["tests"].append({
                    "model": model, "status": "ok",
                    "reply": data["choices"][0]["message"]["content"],
                    "tokens": data.get("usage", {}).get("total_tokens"),
                    "latency_ms": ms,
                })
            else:
                try:
                    body = r.json()
                    code = body.get("error", {}).get("code", "")
                    msg = body.get("error", {}).get("message", "")
                except Exception:
                    code = str(r.status_code)
                    msg = r.text[:150]
                results["tests"].append({
                    "model": model, "status": "error",
                    "code": code, "detail": msg,
                    "http": r.status_code, "latency_ms": ms,
                })
        except requests.Timeout:
            ms = int((time.time() - t0) * 1000)
            results["tests"].append({"model": model, "status": "error", "detail": "Timeout (>10s)", "latency_ms": ms})
        except Exception as e:
            ms = int((time.time() - t0) * 1000)
            results["tests"].append({"model": model, "status": "error", "detail": str(e)[:200], "latency_ms": ms})

    # Test ASR endpoint
    t0 = time.time()
    try:
        r = requests.post(
            f"{ZAI_BASE_URL}/api/paas/v4/audio/transcriptions",
            headers={"Authorization": f"Bearer {token}"},
            data={"model": "glm-asr-2512", "stream": "false"},
            files={"file": ("test.wav", b"\x00" * 100, "audio/wav")},
            timeout=(3, 8),
        )
        ms = int((time.time() - t0) * 1000)
        results["tests"].append({
            "model": "glm-asr-2512",
            "status": "ok" if r.status_code in (200, 400) else "error",
            "http": r.status_code,
            "detail": "reachable" if r.status_code in (200, 400) else r.text[:150],
            "latency_ms": ms,
        })
    except Exception as e:
        ms = int((time.time() - t0) * 1000)
        results["tests"].append({"model": "glm-asr-2512", "status": "error", "detail": str(e)[:200], "latency_ms": ms})

    return jsonify(results)


@app.route("/api/transcribe", methods=["POST"])
def transcribe():
    """Transcribe audio using GLM-ASR-2512 via Z.AI API."""
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

        # Transcribe with GLM-ASR-2512 using Z.AI API
        with open(temp_path, "rb") as audio_file:
            files = {"file": audio_file}
            form_data = {"model": "glm-asr-2512", "stream": "false"}
            
            response = requests.post(
                f"{ZAI_BASE_URL}/paas/v4/audio/transcriptions",
                headers={"Authorization": f"Bearer {ZAI_API_KEY}"},
                data=form_data,
                files=files,
                timeout=30.0
            )

        # Clean up
        os.unlink(temp_path)

        if response.status_code == 200:
            result = response.json()
            return jsonify({
                "text": result.get("text", ""),
                "success": True
            })
        else:
            return jsonify({
                "error": f"API error: {response.status_code}",
                "success": False
            }), response.status_code

    except Exception as e:
        error_msg = get_user_friendly_error(e)
        print(f"Error in /api/transcribe: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": error_msg, "success": False}), 500


@app.route("/api/chat", methods=["POST"])
def chat():
    """Text-based chat with skill routing (for testing without audio)."""
    try:
        data = request.get_json()

        if "message" not in data:
            return jsonify({"error": "message required"}), 400

        session_id = data.get("session_id", "default")
        hotel_id = data.get("hotel_id")
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
        error_msg = get_user_friendly_error(e)
        print(f"Error in /api/chat: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        traceback.print_exc()
        # Pop the user message if API call failed
        if session_id in conversations and len(conversations[session_id]) > 1:
            conversations[session_id].pop()
        
        # Fallback to demo mode if API is unavailable
        if 'quota' in error_msg.lower() or 'rate' in str(e).lower() or '1113' in str(e):
            hotel_info, recommendations = None, []
            if hotel_id:
                hotel_info, recommendations = get_hotel_context(hotel_id)
            demo_response = generate_demo_response(user_message, hotel_info, recommendations)
            return jsonify({
                "response": demo_response,
                "skill_used": "demo_mode",
                "success": True
            })
        
        return jsonify({"error": error_msg, "success": False}), 500


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
            files = {"file": audio_file}
            form_data = {"model": "glm-asr-2512", "stream": "false"}
            
            asr_response = requests.post(
                f"{ZAI_BASE_URL}/paas/v4/audio/transcriptions",
                headers={"Authorization": f"Bearer {ZAI_API_KEY}"},
                data=form_data,
                files=files,
                timeout=30.0
            )

        os.unlink(temp_path)
        
        if asr_response.status_code != 200:
            return jsonify({"error": "Transcription failed", "success": False}), 500
            
        transcription = asr_response.json().get("text", "")

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
        error_msg = get_user_friendly_error(e)
        print(f"Error in /api/voice-chat: {str(e)}")
        traceback.print_exc()
        
        # Fallback to demo mode if API unavailable but we have transcription
        if 'quota' in error_msg.lower() or 'rate' in str(e).lower() or '1113' in str(e):
            # If we got a transcription before the error, use demo mode
            if 'transcription' in dir() and transcription:
                demo_response = generate_demo_response(transcription)
                return jsonify({
                    "transcription": transcription,
                    "response": demo_response,
                    "skill_used": "demo_mode",
                    "success": True
                })
        
        return jsonify({"error": error_msg, "success": False}), 500
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
        error_msg = get_user_friendly_error(e)
        print(f"Error in /api/voice-chat: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": error_msg, "success": False}), 500


@app.route("/api/reset", methods=["POST"])
def reset():
    """Reset conversation history."""
    data = request.get_json() or {}
    session_id = data.get("session_id", "default")

    if session_id in conversations:
        del conversations[session_id]

    return jsonify({"success": True, "message": "Conversation reset"})


@app.route("/api/translate", methods=["POST"])
def translate():
    """Translate text using Z.AI Translation Agent API."""
    try:
        data = request.get_json()
        
        if "text" not in data:
            return jsonify({"error": "text required"}), 400
        
        text = data["text"]
        source_lang = data.get("source_lang", "auto")
        target_lang = data.get("target_lang", "en")  # Use language codes
        strategy = data.get("strategy", "general")
        
        # Map frontend language names to Z.AI language codes
        lang_map = {
            "auto": "auto",
            "Auto-detect": "auto",
            "English": "en",
            "Chinese": "zh-CN",
            "Spanish": "es",
            "French": "fr",
            "German": "de",
            "Japanese": "ja",
            "Korean": "ko"
        }
        
        source_lang_code = lang_map.get(source_lang, source_lang)
        target_lang_code = lang_map.get(target_lang, target_lang)
        
        # Use Z.AI Translation Agent API
        payload = {
            "agent_id": "general_translation",
            "messages": [{
                "role": "user",
                "content": [{"type": "text", "text": text}]
            }],
            "stream": False,
            "custom_variables": {
                "source_lang": source_lang_code,
                "target_lang": target_lang_code,
                "strategy": strategy
            }
        }
        
        response = requests.post(
            f"{ZAI_BASE_URL}/v1/agents",
            headers=ZAI_HEADERS,
            json=payload,
            timeout=30.0
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Check if response has the expected structure
            if "choices" in result and len(result["choices"]) > 0:
                translation = result["choices"][0]["messages"][0]["content"]["text"]
                
                return jsonify({
                    "translation": translation,
                    "source_lang": source_lang,
                    "target_lang": target_lang,
                    "strategy": strategy,
                    "success": True
                })
            else:
                # Log the actual response for debugging
                print(f"Unexpected translation response format: {result}")
                return jsonify({
                    "error": "Translation response format error",
                    "success": False,
                    "details": str(result)
                }), 500
        else:
            error_text = response.text
            print(f"Translation API error {response.status_code}: {error_text}")
            return jsonify({
                "error": f"Translation API error: {response.status_code}",
                "success": False,
                "details": error_text
            }), response.status_code
    
    except Exception as e:
        error_msg = get_user_friendly_error(e)
        print(f"Error in /api/translate: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": error_msg, "success": False}), 500


@app.route("/api/generate-slides", methods=["POST"])
def generate_slides():
    """Generate slides/presentation using Z.AI Slide Agent API."""
    try:
        data = request.get_json()
        
        if "topic" not in data:
            return jsonify({"error": "topic required"}), 400
        
        topic = data["topic"]
        num_slides = data.get("num_slides", 10)
        
        # Use Z.AI Slide/Poster Agent
        payload = {
            "agent_id": "glm_slide_poster_agent",
            "messages": [{
                "role": "user",
                "content": [{"type": "text", "text": topic}]
            }],
            "stream": False,
            "custom_variables": {
                "create_type": "slide",
                "num_slides": num_slides
            }
        }
        
        response = requests.post(
            f"{ZAI_BASE_URL}/v1/agents",
            headers=ZAI_HEADERS,
            json=payload,
            timeout=60.0  # Slides may take longer
        )
        
        if response.status_code == 200:
            result = response.json()
            slides_content = result["choices"][0]["messages"][0]["content"]["text"]
            
            return jsonify({
                "slides": slides_content,
                "topic": topic,
                "num_slides": num_slides,
                "success": True
            })
        else:
            return jsonify({
                "error": f"Slides API error: {response.status_code}",
                "success": False
            }), response.status_code
    
    except Exception as e:
        error_msg = get_user_friendly_error(e)
        print(f"Error in /api/generate-slides: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": error_msg, "success": False}), 500


@app.route("/api/generate-video", methods=["POST"])
def generate_video():
    """Generate video effects using Z.AI Video Template Agent API."""
    try:
        data = request.get_json()
        
        if "image_base64" not in data:
            return jsonify({"error": "image_base64 required"}), 400
        
        image_base64 = data["image_base64"]
        template = data.get("template", "french_kiss")
        
        # Use Z.AI Video Template Agent
        payload = {
            "agent_id": "popular_special_effects_videos",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Generate video with {template} template"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                ]
            }],
            "stream": False,
            "custom_variables": {
                "template": template
            }
        }
        
        response = requests.post(
            f"{ZAI_BASE_URL}/v1/agents",
            headers=ZAI_HEADERS,
            json=payload,
            timeout=90.0  # Video generation takes longer
        )
        
        if response.status_code == 200:
            result = response.json()
            video_url = result.get("video_url", "Processing...")
            
            return jsonify({
                "video_url": video_url,
                "template": template,
                "status": "completed" if video_url != "Processing..." else "processing",
                "success": True
            })
        else:
            return jsonify({
                "error": f"Video API error: {response.status_code}",
                "success": False
            }), response.status_code
    
    except Exception as e:
        error_msg = get_user_friendly_error(e)
        print(f"Error in /api/generate-video: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": error_msg, "success": False}), 500


# Serve static files (for local development; Vercel handles this via routes)
@app.route("/<path:filename>")
def serve_static(filename):
    """Serve static files from public directory."""
    return send_from_directory(PUBLIC_DIR, filename)


# Export for Vercel
handler = app

if __name__ == "__main__":
    import sys
    debug_mode = os.environ.get('FLASK_DEBUG', '1') == '1'
    print(f"📁 Serving static files from: {PUBLIC_DIR}")
    print(f"🌐 Frontend: http://localhost:8000")
    print(f"🌐 Features: http://localhost:8000/features")
    print(f"📡 API Docs: http://localhost:8000/api/health")
    print(f"🔧 Debug mode: {'ON' if debug_mode else 'OFF'}")
    app.run(debug=debug_mode, host='0.0.0.0', port=8000, use_reloader=debug_mode)
