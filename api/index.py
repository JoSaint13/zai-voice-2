"""
NomadAI Voice Agent API - Flask backend for Vercel
Chutes.ai is the single AI provider (chat + tools).
"""

import os
import sys
import json
import sqlite3
import logging
import asyncio
import traceback
from typing import Dict, Any, List
from flask import Flask, request, jsonify, send_from_directory
from flask import Response
from dotenv import load_dotenv
import requests

# Load env vars
load_dotenv()

# Logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Paths
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'hotels.db')
PUBLIC_DIR = os.path.join(os.path.dirname(__file__), '..', 'public')

# Chutes.ai API config (sole provider)
CHUTES_API_KEY = os.getenv('CHUTES_API_KEY', '')
# Guard against truncated/non-ASCII keys (common copy/paste issue with ellipsis)
if any(ord(c) > 127 for c in CHUTES_API_KEY):
    raise ValueError("CHUTES_API_KEY contains non-ASCII characters (maybe '…'). Paste the full ASCII key without ellipsis.")

CHUTES_BASE = os.getenv("CHUTES_BASE", "https://api.chutes.ai")
CHUTES_HEADERS = {
    'Authorization': f'Bearer {CHUTES_API_KEY}',
    'Content-Type': 'application/json'
}
CHUTES_STT_MODEL = os.getenv("CHUTES_STT_MODEL", "openai/whisper-large-v3")
CHUTES_STT_ENDPOINT = os.getenv("CHUTES_STT_ENDPOINT")  # optional direct chute endpoint (e.g., https://chutes-whisper-large-v3.chutes.ai/transcribe)
CHUTES_TTS_MODEL = os.getenv("CHUTES_TTS_MODEL", "kokoro")
CHUTES_TTS_ENDPOINT = os.getenv("CHUTES_TTS_ENDPOINT", "https://chutes-kokoro.chutes.ai/speak")

# ── Named LLM Roles ──
# 🧠 brain_llm — reasoning, routing, chat
BRAIN_LLM_MODEL = os.getenv("BRAIN_LLM_MODEL", "XiaomiMiMo/MiMo-V2-Flash")
BRAIN_LLM_ENDPOINT = os.getenv("BRAIN_LLM_ENDPOINT", "https://llm.chutes.ai/v1/chat/completions")
# 🎧 voice_listen_llm — STT (Whisper)
VOICE_LISTEN_LLM = CHUTES_STT_ENDPOINT or f"{CHUTES_BASE}/v1/audio/transcriptions"
# 🔊 speech_llm — TTS (Kokoro)
SPEECH_LLM = CHUTES_TTS_ENDPOINT


class ChutesHTTPError(Exception):
    """HTTP error wrapper for Chutes API."""
    def __init__(self, status_code: int, message: str):
        super().__init__(message)
        self.status_code = status_code
        self.message = message

# ── Provider Registry ──
PROVIDERS = {
    'chutes': {
        'name': 'Chutes.ai',
        'api_key': CHUTES_API_KEY,
        'models': [
            {'id': 'deepseek-ai/DeepSeek-V3-0324', 'slug': 'chutes-deepseek-ai-deepseek-v3-0324-tee', 'name': 'DeepSeek V3', 'desc': 'Strong open-source reasoning'},
            {'id': 'deepseek-ai/DeepSeek-V3.1', 'slug': 'chutes-deepseek-ai-deepseek-v3-1-tee', 'name': 'DeepSeek V3.1', 'desc': 'Hybrid thinking/non-thinking'},
            {'id': 'deepseek-ai/DeepSeek-V3.2', 'slug': 'chutes-deepseek-ai-deepseek-v3-2-tee', 'name': 'DeepSeek V3.2', 'desc': 'Efficient reasoning & agents'},
            {'id': 'deepseek-ai/DeepSeek-R1-0528', 'slug': 'chutes-deepseek-ai-deepseek-r1-0528-tee', 'name': 'DeepSeek R1', 'desc': 'Deep reasoning (long CoT)'},
            {'id': 'Qwen/Qwen3-32B', 'slug': 'chutes-qwen-qwen3-32b', 'name': 'Qwen3 32B', 'desc': 'Reasoning, coding, multilingual'},
            {'id': 'Qwen/Qwen3-235B-A22B-Instruct-2507', 'slug': 'chutes-qwen-qwen3-235b-a22b-instruct-2507-tee', 'name': 'Qwen3 235B', 'desc': 'Top-tier MoE instruct'},
            {'id': 'NousResearch/Hermes-4-70B', 'slug': 'chutes-nousresearch-hermes-4-70b', 'name': 'Hermes 4 70B', 'desc': 'Steerable reasoning model'},
            {'id': 'chutesai/Mistral-Small-3.1-24B-Instruct-2503', 'slug': 'chutes-chutesai-mistral-small-3-1-24b-instruct-2503', 'name': 'Mistral Small 3.1', 'desc': 'Fast, vision, function calling'},
            {'id': 'openai/gpt-oss-120b', 'slug': 'chutes-openai-gpt-oss-120b-tee', 'name': 'GPT-OSS 120B', 'desc': 'Open-source 120B'},
        ],
        'default_model': 'deepseek-ai/DeepSeek-V3-0324',
        'auth_type': 'bearer',  # simple Bearer token
    },
}

# Active provider state (in production, per-session via DB/Redis)
active_provider = 'chutes'
active_model = PROVIDERS[active_provider]['default_model']

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


# ── Chutes helpers ──
def chutes_post_json(path: str, payload: dict, stream: bool = False):
    """Minimal JSON POST wrapper to Chutes with error handling."""
    if not CHUTES_API_KEY:
        raise ValueError("Chutes API key not configured")

    url = f"{CHUTES_BASE}{path}"
    log_payload = {k: v for k, v in payload.items() if k not in ("audio", "audio_base64", "input")}
    logger.info(f"[chutes] POST {path} stream={stream} payload={log_payload}")
    r = requests.post(url, headers=CHUTES_HEADERS, json=payload, timeout=(5, 60), stream=stream)
    logger.info(f"[chutes] {path} -> HTTP {r.status_code}")
    if not stream and r.status_code != 200:
        try:
            body = r.json()
            msg = body.get("error", body.get("detail", r.text))
        except Exception:
            msg = r.text
        raise ChutesHTTPError(r.status_code, str(msg)[:400])
    return r


def call_chutes_stt(audio_base64: str, language: str | None = None) -> str:
    """Call Chutes STT (Whisper v3). Returns transcription string."""
    # If direct chute endpoint provided, use it (expects audio_b64)
    if CHUTES_STT_ENDPOINT:
        payload = {
            "audio_b64": audio_base64,
            "language": language,
        }
        # clean None keys
        payload = {k: v for k, v in payload.items() if v is not None}
        headers = {
            "Authorization": f"Bearer {CHUTES_API_KEY}",
            "Content-Type": "application/json",
        }
        logger.info(f"[stt] endpoint={CHUTES_STT_ENDPOINT} payload_keys={list(payload.keys())}")
        r = requests.post(CHUTES_STT_ENDPOINT, headers=headers, json=payload, timeout=(5, 60))
        if r.status_code != 200:
            try:
                msg = r.json()
            except Exception:
                msg = r.text
            raise ChutesHTTPError(r.status_code, f"Direct STT endpoint error: {msg}")
        data = r.json()
        if isinstance(data, list):
            data = data[0] if data else {}
        if isinstance(data, str):
            text = data
        else:
            text = data.get("text") or data.get("transcription") or data.get("transcript") or ""
        logger.info(f"[stt] endpoint chars={len(text)}")
        return text

    # Default: central API
    payload = {
        "model": CHUTES_STT_MODEL,
        "audio": audio_base64,
    }
    if language:
        payload["language"] = language

    resp = chutes_post_json("/v1/audio/transcriptions", payload)
    data = resp.json()
    text = data.get("text") or data.get("transcription") or ""
    logger.info(f"[stt] model={CHUTES_STT_MODEL} lang={language or 'auto'} chars={len(text)}")
    return text


def call_chutes_tts(text: str, voice: str | None = None) -> str:
    """Call Chutes TTS, return audio base64 (wav)."""
    # Kokoro voice IDs are like "af_heart", not model names
    if not voice or voice in ("kokoro", "csm-1b"):
        voice_model = "af_heart"
    else:
        voice_model = voice
    if CHUTES_TTS_ENDPOINT:
        payload = {
            "text": text,
            "speed": 1,
            "voice": voice_model,
        }
        headers = {
            "Authorization": f"Bearer {CHUTES_API_KEY}",
            "Content-Type": "application/json",
        }
        logger.info(f"[tts] endpoint={CHUTES_TTS_ENDPOINT} voice={voice_model} chars={len(text)}")
        r = requests.post(CHUTES_TTS_ENDPOINT, headers=headers, json=payload, timeout=(5, 60))
        if r.status_code != 200:
            try:
                msg = r.json()
            except Exception:
                msg = r.text[:200]
            raise ChutesHTTPError(r.status_code, f"Direct TTS endpoint error: {msg}")

        # Kokoro returns raw audio bytes (WAV) or JSON with base64
        content_type = r.headers.get("Content-Type", "")
        if "application/json" in content_type:
            data = r.json()
            if isinstance(data, list):
                data = data[0] if data else {}
            if isinstance(data, str):
                audio_b64 = data
            else:
                audio_b64 = data.get("audio") or data.get("audio_base64") or data.get("data") or ""
        else:
            # Raw binary audio — encode to base64
            import base64
            audio_b64 = base64.b64encode(r.content).decode("utf-8")

        if not audio_b64:
            raise RuntimeError(f"TTS response missing audio data (content-type: {content_type})")
        logger.info(f"[tts] endpoint voice={voice_model} chars={len(text)} audio_len={len(audio_b64)}")
        return audio_b64

    # Fallback: central API
    payload = {
        "model": CHUTES_TTS_MODEL,
        "input": text,
        "format": "wav",
    }
    resp = chutes_post_json("/v1/audio/speech", payload)
    data = resp.json()
    audio_b64 = data.get("audio") or data.get("audio_base64") or data.get("data")
    if not audio_b64:
        raise RuntimeError("TTS response missing audio data")
    logger.info(f"[tts] model={CHUTES_TTS_MODEL} chars={len(text)} audio_len={len(audio_b64)}")
    return audio_b64


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


def provider_chat(messages, provider_id=None, model_id=None, temperature=0.7, max_tokens=1024):
    """
    Chat completion via Chutes.ai. Returns the assistant message text.
    Raises on error.
    """
    global active_provider, active_model
    pid = provider_id or active_provider
    mid = model_id or active_model
    prov = PROVIDERS.get(pid)

    if not prov:
        raise ValueError(f"Unknown provider: {pid}")
    if not prov['api_key']:
        raise ValueError(f"No API key configured for {prov['name']}")

    # Find slug for this model
    model_entry = next((m for m in prov['models'] if m['id'] == mid), None)
    if not model_entry or 'slug' not in model_entry:
        raise ValueError(f"No chute slug configured for model {mid}")
    url = f"https://{model_entry['slug']}.chutes.ai/v1/chat/completions"

    headers = {'Authorization': f'Bearer {prov["api_key"]}', 'Content-Type': 'application/json'}

    payload = {
        'model': mid,
        'messages': messages,
        'temperature': temperature,
        'max_tokens': max_tokens,
    }

    logger.info(f"[provider_chat] {prov['name']} / {mid} — msgs={len(messages)} temp={temperature} max_tokens={max_tokens}")

    r = requests.post(url, headers=headers, json=payload, timeout=(5, 60))

    if r.status_code != 200:
        try:
            body = r.json()
            code = body.get("error", {}).get("code", "")
            msg = body.get("error", {}).get("message", r.text[:200])
        except Exception:
            code = str(r.status_code)
            msg = r.text[:200]
        raise RuntimeError(f"[{prov['name']}] HTTP {r.status_code} — {code}: {msg}")

    data = r.json()
    msg_obj = data['choices'][0]['message']
    content = msg_obj.get('content') or msg_obj.get('reasoning_content') or ''

    # Strip <think>...</think> blocks from reasoning models (DeepSeek R1, Qwen thinking, etc.)
    import re
    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()

    return content


def brain_chat(messages, temperature=0.7, max_tokens=1024):
    """
    🧠 brain_llm — primary reasoning via MiMo-V2-Flash (or configured brain model).
    Uses dedicated endpoint, bypassing the slug-based provider registry.
    """
    import re
    headers = {
        'Authorization': f'Bearer {CHUTES_API_KEY}',
        'Content-Type': 'application/json',
    }
    payload = {
        'model': BRAIN_LLM_MODEL,
        'messages': messages,
        'temperature': temperature,
        'max_tokens': max_tokens,
    }
    logger.info(f"[brain_chat] {BRAIN_LLM_MODEL} — msgs={len(messages)} temp={temperature} max_tokens={max_tokens}")

    r = requests.post(BRAIN_LLM_ENDPOINT, headers=headers, json=payload, timeout=(5, 60))
    if r.status_code != 200:
        try:
            body = r.json()
            msg = body.get("error", {}).get("message", r.text[:200]) if isinstance(body.get("error"), dict) else str(body.get("error", r.text[:200]))
        except Exception:
            msg = r.text[:200]
        raise RuntimeError(f"[brain_llm] HTTP {r.status_code}: {msg}")

    data = r.json()
    msg_obj = data['choices'][0]['message']
    content = msg_obj.get('content') or msg_obj.get('reasoning_content') or ''
    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
    return content


# Default hotel config (used when no DB is available)
DEFAULT_HOTELS = {
    "2ada3c2b-b208-4599-9c46-f32dc16ff950": {
        "id": "2ada3c2b-b208-4599-9c46-f32dc16ff950",
        "name": "NomadAI Hotel",
        "description": "Your AI-powered hotel concierge",
        "theme_color": "#1a1a2e",
    }
}


@app.route("/api/hotel/<hotel_id>", methods=["GET"])
def get_hotel(hotel_id):
    """Get hotel configuration by ID."""
    # Try database first
    hotel_info, recommendations = get_hotel_context(hotel_id)
    if hotel_info:
        return jsonify({
            "id": hotel_id,
            "name": hotel_info.get("name", "Hotel"),
            "description": "AI Concierge",
            "theme_color": hotel_info.get("theme_color", "#1a1a2e"),
            "recommendations": recommendations,
        })

    # Fallback to defaults
    if hotel_id in DEFAULT_HOTELS:
        return jsonify(DEFAULT_HOTELS[hotel_id])

    # Unknown hotel — return a generic config so the page still works
    return jsonify({
        "id": hotel_id,
        "name": "Hotel Concierge",
        "description": "AI-powered assistant",
        "theme_color": "#333333",
    })


@app.route("/api/providers", methods=["GET"])
def list_providers():
    """List available AI providers and their models."""
    global active_provider, active_model
    result = {}
    for pid, prov in PROVIDERS.items():
        result[pid] = {
            'name': prov['name'],
            'configured': bool(prov['api_key']),
            'models': prov['models'],
            'default_model': prov['default_model'],
        }
    return jsonify({
        'providers': result,
        'active_provider': active_provider,
        'active_model': active_model,
        'llm_roles': {
            'brain_llm': {'model': BRAIN_LLM_MODEL, 'endpoint': BRAIN_LLM_ENDPOINT, 'role': 'Reasoning, routing, chat'},
            'voice_listen_llm': {'model': CHUTES_STT_MODEL, 'endpoint': VOICE_LISTEN_LLM, 'role': 'Speech-to-text'},
            'speech_llm': {'model': CHUTES_TTS_MODEL, 'endpoint': SPEECH_LLM, 'role': 'Text-to-speech'},
        },
    })


@app.route("/api/health", methods=["GET"])
def health():
    """Simple health check."""
    return jsonify({
        "status": "ok",
        "brain_llm": BRAIN_LLM_MODEL,
        "voice_listen_llm": CHUTES_STT_MODEL,
        "speech_llm": CHUTES_TTS_MODEL,
        "provider_configured": bool(CHUTES_API_KEY),
        "asr_configured": bool(CHUTES_API_KEY),
        "tts_model": CHUTES_TTS_MODEL,
        "stt_endpoint": VOICE_LISTEN_LLM,
        "tts_endpoint": SPEECH_LLM,
    })


@app.route("/api/providers/switch", methods=["POST"])
def switch_provider():
    """Switch active provider and/or model."""
    global active_provider, active_model
    data = request.get_json() or {}

    new_provider = data.get('provider', active_provider)
    new_model = data.get('model')

    if new_provider not in PROVIDERS:
        return jsonify({'error': f'Unknown provider: {new_provider}'}), 400

    prov = PROVIDERS[new_provider]
    if not prov['api_key']:
        return jsonify({'error': f'No API key configured for {prov["name"]}'}), 400

    active_provider = new_provider
    if new_model:
        active_model = new_model
    else:
        active_model = prov['default_model']

    logger.info(f"Switched to provider={active_provider}, model={active_model}")
    return jsonify({
        'active_provider': active_provider,
        'active_model': active_model,
        'provider_name': prov['name'],
    })


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
    Route user utterance to the appropriate skill using the active Chutes LLM.

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

    # Use brain_llm for intent routing
    try:
        result_text = brain_chat(messages, temperature=0.1, max_tokens=50)
        skill_name = result_text.strip().lower()
    except Exception as e:
        logger.warning(f"Intent routing failed, falling back to general_chat: {e}")
        skill_name = "general_chat"

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


# ── Agentic Tool Definitions ──

SKILL_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "room_service",
            "description": "Order food and beverages to the guest's room",
            "parameters": {
                "type": "object",
                "properties": {
                    "request": {"type": "string", "description": "What the guest wants to order"},
                },
                "required": ["request"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "housekeeping",
            "description": "Request housekeeping services (towels, cleaning, supplies)",
            "parameters": {
                "type": "object",
                "properties": {
                    "request": {"type": "string", "description": "What the guest needs"},
                },
                "required": ["request"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "amenities_info",
            "description": "Get info about hotel amenities, hours, facilities (pool, gym, spa, restaurant)",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "What amenity or facility the guest is asking about"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "wifi_help",
            "description": "Provide WiFi password or help with connectivity issues",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue": {"type": "string", "description": "WiFi issue description"},
                },
                "required": ["issue"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "local_recommendations",
            "description": "Suggest local restaurants, attractions, points of interest",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "What kind of place or activity the guest wants"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "itinerary_planning",
            "description": "Create personalized day plans and sightseeing itineraries",
            "parameters": {
                "type": "object",
                "properties": {
                    "request": {"type": "string", "description": "What kind of day plan the guest wants"},
                },
                "required": ["request"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "directions",
            "description": "Help navigate to a destination with directions",
            "parameters": {
                "type": "object",
                "properties": {
                    "destination": {"type": "string", "description": "Where the guest wants to go"},
                },
                "required": ["destination"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "voice_call",
            "description": "Make a phone call on behalf of the guest (e.g., call a restaurant to make a reservation)",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["initiate_call", "speak", "end_call", "get_status"], "description": "Call action to perform"},
                    "to": {"type": "string", "description": "Phone number or place name to call"},
                    "message": {"type": "string", "description": "What to say on the call"},
                },
                "required": ["action"],
            },
        },
    },
]

# Map tool names to skill instances
SKILL_MAP = {}
for skill in SKILLS:
    SKILL_MAP[skill.name] = skill


def _execute_tool(tool_name: str, arguments: dict, session_id: str) -> str:
    """Execute a skill tool and return the result as a string."""
    # Voice call handled separately (Phase 3)
    if tool_name == "voice_call":
        return _execute_voice_call(arguments, session_id)

    skill = SKILL_MAP.get(tool_name)
    if not skill:
        return f"Unknown tool: {tool_name}"

    context = {
        "transcription": arguments.get("request") or arguments.get("query") or arguments.get("issue") or arguments.get("destination") or "",
        "session_id": session_id,
        "location": "Tokyo",
        "hotel_location": "NomadAI Hotel",
    }

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(skill.execute(context))
        loop.close()
        return result.get("response", str(result))
    except Exception as e:
        logger.error(f"[agent_loop] tool {tool_name} failed: {e}")
        return f"Error executing {tool_name}: {str(e)}"


def _execute_voice_call(arguments: dict, session_id: str) -> str:
    """Mock voice call execution (Phase 3 will add real telephony)."""
    action = arguments.get("action", "get_status")
    to = arguments.get("to", "unknown")
    message = arguments.get("message", "")

    if action == "initiate_call":
        return json.dumps({"status": "connected", "to": to, "call_id": f"mock_{session_id[:8]}", "message": f"Call connected to {to}. Ready to speak."})
    elif action == "speak":
        # Mock: simulate restaurant response
        mock_responses = {
            "reservation": f"Restaurant says: 'Sure, we can seat you. What time would you like?'",
            "menu": f"Restaurant says: 'Today's special is grilled salmon with truffle risotto. We also have a tasting menu available.'",
            "hours": f"Restaurant says: 'We're open from 11:30 AM to 10 PM today.'",
        }
        for keyword, response in mock_responses.items():
            if keyword in message.lower():
                return response
        return f"Restaurant says: 'How can I help you?' (You said: {message})"
    elif action == "end_call":
        return json.dumps({"status": "ended", "call_id": f"mock_{session_id[:8]}"})
    elif action == "get_status":
        return json.dumps({"status": "idle", "active_calls": 0})
    return f"Unknown voice_call action: {action}"


def agent_loop(user_message: str, session_id: str, hotel_info=None, max_iterations: int = 5) -> str:
    """
    🧠 Agentic tool-calling loop.
    brain_llm decides whether to call tools or respond directly.
    Supports multi-turn tool calls (up to max_iterations).
    """
    import re

    # Build system prompt
    hotel_context = ""
    if hotel_info:
        hotel_context = f"\nHotel: {hotel_info.get('name', 'NomadAI Hotel')}"
        if hotel_info.get('knowledge_base'):
            hotel_context += f"\nHotel Knowledge Base:\n{hotel_info['knowledge_base']}"

    system_prompt = f"""You are NomadAI, a voice-first AI hotel concierge assistant.{hotel_context}

You have tools to help guests with hotel services, local recommendations, and making phone calls.
Use tools when appropriate. Keep spoken responses concise (2-3 sentences).
If the guest asks you to call a place, use the voice_call tool to initiate and conduct the call, then report back.
For general conversation, just respond directly without tools."""

    # Init or continue conversation
    if session_id not in conversations:
        conversations[session_id] = [{"role": "system", "content": system_prompt}]

    conversations[session_id].append({"role": "user", "content": user_message})

    for iteration in range(max_iterations):
        # Call brain_llm with tools
        headers = {
            'Authorization': f'Bearer {CHUTES_API_KEY}',
            'Content-Type': 'application/json',
        }
        payload = {
            'model': BRAIN_LLM_MODEL,
            'messages': conversations[session_id],
            'temperature': 0.7,
            'max_tokens': 1024,
            'tools': SKILL_TOOLS,
            'tool_choice': 'auto',
        }

        logger.info(f"[agent_loop] iteration={iteration+1}/{max_iterations} msgs={len(conversations[session_id])}")
        r = requests.post(BRAIN_LLM_ENDPOINT, headers=headers, json=payload, timeout=(5, 60))

        if r.status_code != 200:
            logger.error(f"[agent_loop] brain_llm HTTP {r.status_code}: {r.text[:200]}")
            # Fallback to simple brain_chat without tools
            return brain_chat(conversations[session_id])

        data = r.json()
        choice = data['choices'][0]
        msg = choice['message']
        finish_reason = choice.get('finish_reason', '')

        # If model wants to call tools
        if msg.get('tool_calls'):
            conversations[session_id].append(msg)

            for tool_call in msg['tool_calls']:
                fn_name = tool_call['function']['name']
                try:
                    fn_args = json.loads(tool_call['function']['arguments'])
                except (json.JSONDecodeError, KeyError):
                    fn_args = {}

                logger.info(f"[agent_loop] tool_call: {fn_name}({fn_args})")
                result = _execute_tool(fn_name, fn_args, session_id)
                logger.info(f"[agent_loop] tool_result: {result[:200]}")

                conversations[session_id].append({
                    "role": "tool",
                    "tool_call_id": tool_call['id'],
                    "content": result,
                })

            continue  # Next iteration — let brain process tool results

        # Model gave a direct response (no tool calls)
        content = msg.get('content') or msg.get('reasoning_content') or ''
        content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
        conversations[session_id].append({"role": "assistant", "content": content})
        return content

    # Max iterations reached — force a final response
    logger.warning(f"[agent_loop] max iterations ({max_iterations}) reached")
    return brain_chat(conversations[session_id])


@app.route("/", methods=["GET"])
def home():
    return send_from_directory(PUBLIC_DIR, "index.html")


@app.route("/api/ping", methods=["GET"])
def ping():
    """Test API connectivity to Chutes.ai provider."""
    import time

    results = {
        "active_provider": active_provider,
        "active_model": active_model,
        "providers": {}
    }

    # ── Test Chutes.ai ──
    chutes_results = {"api_key": "configured" if CHUTES_API_KEY else "missing", "tests": []}

    if CHUTES_API_KEY:
        chutes_headers = {"Authorization": f"Bearer {CHUTES_API_KEY}", "Content-Type": "application/json"}

        # Test a few models (using per-chute slug URLs)
        chutes_test_models = [
            {"model": "deepseek-ai/DeepSeek-V3-0324", "slug": "chutes-deepseek-ai-deepseek-v3-0324-tee"},
            {"model": "Qwen/Qwen3-32B", "slug": "chutes-qwen-qwen3-32b"},
        ]
        for tm in chutes_test_models:
            model = tm["model"]
            slug = tm["slug"]
            t0 = time.time()
            try:
                r = requests.post(
                    f"https://{slug}.chutes.ai/v1/chat/completions",
                    headers=chutes_headers,
                    json={"model": model, "messages": [{"role": "user", "content": "Reply: pong"}], "max_tokens": 20},
                    timeout=(5, 15),
                )
                ms = int((time.time() - t0) * 1000)
                if r.status_code == 200:
                    data = r.json()
                    msg_obj = data["choices"][0]["message"]
                    reply = msg_obj.get("content") or msg_obj.get("reasoning_content") or ""
                    reply = reply[:50]
                    # Strip thinking tags from reply
                    import re as _re
                    reply = _re.sub(r'<think>.*?</think>', '', reply, flags=_re.DOTALL).strip()
                    chutes_results["tests"].append({
                        "model": model, "status": "ok",
                        "reply": reply,
                        "latency_ms": ms,
                    })
                else:
                    try:
                        msg = r.json().get("detail", r.text[:150])
                    except Exception:
                        msg = r.text[:150]
                    chutes_results["tests"].append({"model": model, "status": "error", "detail": str(msg)[:200], "http": r.status_code, "latency_ms": ms})
            except requests.Timeout:
                ms = int((time.time() - t0) * 1000)
                chutes_results["tests"].append({"model": model, "status": "error", "detail": "Timeout", "latency_ms": ms})
            except Exception as e:
                ms = int((time.time() - t0) * 1000)
                chutes_results["tests"].append({"model": model, "status": "error", "detail": str(e)[:200], "latency_ms": ms})
    else:
        chutes_results["tests"].append({"model": "all", "status": "skip", "detail": "No API key"})

    results["providers"]["chutes"] = chutes_results

    return jsonify(results)


@app.route("/api/transcribe", methods=["POST"])
def transcribe():
    """Transcribe audio via Chutes STT."""
    try:
        data = request.get_json() or {}
        audio_b64 = data.get("audio_base64")
        language = data.get("language")
        if not audio_b64:
            return jsonify({"error": "audio_base64 required"}), 400
        text = call_chutes_stt(audio_b64, language=language)
        return jsonify({"success": True, "text": text, "language": language or "auto"})
    except ChutesHTTPError as e:
        logger.error(f"STT error {e.status_code}: {e.message}")
        return jsonify({"error": e.message, "success": False, "reason": f"stt_{e.status_code}"}), 502
    except Exception as e:
        error_msg = get_user_friendly_error(e)
        logger.error(f"STT error: {e}")
        return jsonify({"error": error_msg, "success": False, "reason": "stt_failed"}), 500


@app.route("/api/chat", methods=["POST"])
def chat():
    """Text-based chat with agentic tool-calling loop."""
    try:
        data = request.get_json()

        if "message" not in data:
            return jsonify({"error": "message required"}), 400

        session_id = data.get("session_id", "default")
        hotel_id = data.get("hotel_id")
        user_message = data["message"]
        logger.info(f"[chat] session={session_id} brain={BRAIN_LLM_MODEL} len={len(user_message)}")

        # Get hotel context if available
        hotel_info = None
        if hotel_id:
            hotel_info, _ = get_hotel_context(hotel_id)
            if not hotel_info:
                hotel_info = DEFAULT_HOTELS.get(hotel_id)

        # Run agentic loop
        assistant_message = agent_loop(user_message, session_id, hotel_info=hotel_info)

        return jsonify({
            "response": assistant_message,
            "brain_llm": BRAIN_LLM_MODEL,
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


def _sse(data: Dict[str, Any]) -> str:
    """Format SSE event line."""
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


def stream_chat(messages, provider_id=None, model_id=None):
    """Streamed chat (fake-stream via word chunks)."""
    try:
        full = brain_chat(messages)
        words = full.split()
        for w in words:
            yield _sse({"delta": w + " "})
        yield _sse({"done": True, "text": full})
    except Exception as e:
        yield _sse({"error": get_user_friendly_error(e)})


@app.route("/api/chat-stream", methods=["POST"])
def chat_stream():
    """SSE streaming chat via agent_loop."""
    data = request.get_json() or {}
    if "message" not in data:
        return jsonify({"error": "message required"}), 400

    session_id = data.get("session_id", "default-stream")
    hotel_id = data.get("hotel_id")
    user_message = data["message"]

    hotel_info = None
    if hotel_id:
        hotel_info, _ = get_hotel_context(hotel_id)
        if not hotel_info:
            hotel_info = DEFAULT_HOTELS.get(hotel_id)

    def generate():
        try:
            full = agent_loop(user_message, session_id, hotel_info=hotel_info)
            words = full.split()
            for w in words:
                yield _sse({"delta": w + " "})
            yield _sse({"done": True, "text": full})
        except Exception as e:
            yield _sse({"error": get_user_friendly_error(e)})

    headers = {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
    }
    return Response(generate(), headers=headers)


@app.route("/api/voice-chat", methods=["POST"])
def voice_chat():
    """Voice chat: STT -> LLM -> TTS."""
    try:
        data = request.get_json() or {}
        audio_b64 = data.get("audio_base64")
        session_id = data.get("session_id", "default")
        hotel_id = data.get("hotel_id")
        language = data.get("language")
        tts_voice = data.get("tts_voice")

        if not audio_b64:
            return jsonify({"error": "audio_base64 required"}), 400

        logger.info(f"[voice] session={session_id} hotel={hotel_id} brain={BRAIN_LLM_MODEL} tts={tts_voice or CHUTES_TTS_MODEL}")

        # 1) STT (voice_listen_llm)
        transcription = call_chutes_stt(audio_b64, language=language)

        # 2) Agent loop (brain_llm) — with tool calling
        hotel_info = None
        if hotel_id:
            hotel_info, _ = get_hotel_context(hotel_id)
            if not hotel_info:
                hotel_info = DEFAULT_HOTELS.get(hotel_id)

        assistant_message = agent_loop(transcription, session_id, hotel_info=hotel_info)

        # 3) TTS (speech_llm) — stream by sentences if requested
        stream_mode = data.get("stream_tts", False)

        if stream_mode:
            # SSE streaming: split into sentences, TTS each, stream audio chunks
            import re as _re
            sentences = _re.split(r'(?<=[.!?])\s+', assistant_message)
            sentences = [s.strip() for s in sentences if s.strip()]

            def generate_voice_stream():
                yield f"data: {json.dumps({'type': 'transcription', 'text': transcription})}\n\n"
                yield f"data: {json.dumps({'type': 'response', 'text': assistant_message})}\n\n"
                for i, sentence in enumerate(sentences):
                    try:
                        chunk_audio = call_chutes_tts(sentence, voice=tts_voice)
                        yield f"data: {json.dumps({'type': 'audio_chunk', 'index': i, 'audio_base64': chunk_audio, 'text': sentence})}\n\n"
                    except Exception as e:
                        logger.error(f"[tts_stream] chunk {i} failed: {e}")
                yield f"data: {json.dumps({'type': 'done', 'total_chunks': len(sentences)})}\n\n"

            return Response(generate_voice_stream(), headers={
                "Content-Type": "text/event-stream",
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            })

        # Non-streaming: single TTS call
        audio_reply_b64 = call_chutes_tts(assistant_message, voice=tts_voice)

        return jsonify({
            "success": True,
            "transcription": transcription,
            "response": assistant_message,
            "audio_base64": audio_reply_b64,
            "brain_llm": BRAIN_LLM_MODEL,
            "hotel_id": hotel_id,
            "session_id": session_id
        })

    except ChutesHTTPError as e:
        # Specific handling for missing STT chute
        logger.error(f"Chutes error {e.status_code}: {e.message}")
        reason = "voice_chat_failed"
        status = 502
        if e.status_code == 404:
            reason = "stt_not_available"
            return jsonify({
                "success": False,
                "error": "Speech-to-text model not available on this Chutes account. Set CHUTES_STT_MODEL to a chute you own or create a transcription chute.",
                "reason": reason
            }), status
        return jsonify({"success": False, "error": e.message, "reason": reason}), status
    except Exception as e:
        error_msg = get_user_friendly_error(e)
        logger.error(f"Error in /api/voice-chat: {e}")
        traceback.print_exc()
        return jsonify({"error": error_msg, "success": False, "reason": "voice_chat_failed"}), 500
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
    """Translate text using Chutes.ai chat model."""
    try:
        data = request.get_json()
        
        if "text" not in data:
            return jsonify({"error": "text required"}), 400
        
        text = data["text"]
        source_lang = data.get("source_lang", "auto")
        target_lang = data.get("target_lang", "en")
        strategy = data.get("strategy", "general")
        
        # Map frontend language names to full names for the prompt
        lang_map = {
            "auto": "auto-detect",
            "Auto-detect": "auto-detect",
            "en": "English",
            "zh-CN": "Chinese (Simplified)",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "ja": "Japanese",
            "ko": "Korean",
            "English": "English",
            "Chinese": "Chinese (Simplified)",
            "Spanish": "Spanish",
            "French": "French",
            "German": "German",
            "Japanese": "Japanese",
            "Korean": "Korean",
        }
        
        source_name = lang_map.get(source_lang, source_lang)
        target_name = lang_map.get(target_lang, target_lang)
        
        source_instruction = f"from {source_name}" if source_name != "auto-detect" else "(auto-detect the source language)"
        
        messages = [
            {
                "role": "system",
                "content": f"You are a professional translator. Translate the following text {source_instruction} to {target_name}. "
                           f"Translation strategy: {strategy}. "
                           "Output ONLY the translated text, nothing else — no explanations, no quotes, no labels."
            },
            {"role": "user", "content": text}
        ]
        
        translation = brain_chat(messages, temperature=0.3, max_tokens=2048)
        
        return jsonify({
            "translation": translation,
            "translated_text": translation,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "strategy": strategy,
            "success": True
        })
    
    except Exception as e:
        error_msg = get_user_friendly_error(e)
        print(f"Error in /api/translate: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": error_msg, "success": False}), 500


@app.route("/api/tts", methods=["POST"])
def tts():
    """Text-to-speech via Chutes."""
    try:
        data = request.get_json() or {}
        text = data.get("text")
        voice = data.get("voice")
        if not text:
            return jsonify({"error": "text required"}), 400
        audio_b64 = call_chutes_tts(text, voice=voice)
        return jsonify({"success": True, "audio_base64": audio_b64, "voice": voice or CHUTES_TTS_MODEL, "format": "wav"})
    except ChutesHTTPError as e:
        logger.error(f"TTS error {e.status_code}: {e.message}")
        return jsonify({"error": e.message, "success": False, "reason": f"tts_{e.status_code}"}), 502
    except Exception as e:
        error_msg = get_user_friendly_error(e)
        logger.error(f"TTS error: {e}")
        traceback.print_exc()
        return jsonify({"error": error_msg, "success": False, "reason": "tts_failed"}), 500


@app.route("/api/generate-slides", methods=["POST"])
def generate_slides():
    """Generate slides — currently not available with the current provider."""
    return jsonify({
        "error": "Slide generation is not currently available with the current provider.",
        "success": False,
        "reason": "no_slides_agent"
    }), 501


@app.route("/api/generate-video", methods=["POST"])
def generate_video():
    """Generate video — currently not available with the current provider."""
    return jsonify({
        "error": "Video generation is not currently available with the current provider.",
        "success": False,
        "reason": "no_video_agent"
    }), 501


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
    print(f"🌐 Frontend: http://localhost:8088")
    print(f"🌐 Features: http://localhost:8088/features")
    print(f"📡 API Docs: http://localhost:8088/api/health")
    print(f"🔧 Debug mode: {'ON' if debug_mode else 'OFF'}")
    app.run(debug=debug_mode, host='0.0.0.0', port=8088, use_reloader=debug_mode)
