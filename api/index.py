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
CHUTES_HEADERS = {
    'Authorization': f'Bearer {CHUTES_API_KEY}',
    'Content-Type': 'application/json'
}

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

    logger.info(f"[provider_chat] {prov['name']} / {mid} — {len(messages)} msgs")

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
    })


@app.route("/api/health", methods=["GET"])
def health():
    """Simple health check."""
    return jsonify({
        "status": "ok",
        "active_provider": active_provider,
        "active_model": active_model,
        "provider_configured": bool(PROVIDERS.get(active_provider, {}).get("api_key"))
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

    # Use provider_chat for intent routing
    try:
        result_text = provider_chat(messages, temperature=0.1, max_tokens=50)
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
    """Transcribe audio — currently not available (no ASR provider)."""
    return jsonify({
        "error": "Speech-to-text is not currently available (ASR provider not available). Please use the Chat tab to type your message.",
        "success": False,
        "reason": "no_asr_provider"
    }), 501


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

            # Use provider_chat (Chutes-only)
            provider_id = data.get("provider")
            model_id = data.get("model")
            assistant_message = provider_chat(
                conversations[session_id],
                provider_id=provider_id,
                model_id=model_id,
            )

            conversations[session_id].append({
                "role": "assistant",
                "content": assistant_message
            })

            return jsonify({
                "response": assistant_message,
                "skill_used": "general_chat",
                "provider": provider_id or active_provider,
                "model": model_id or active_model,
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
    """Voice chat — currently not available (no ASR provider)."""
    return jsonify({
        "error": "Voice chat requires speech-to-text which is not currently available (ASR provider not available). Please use the Chat tab to type your message.",
        "success": False,
        "reason": "no_asr_provider"
    }), 501
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
        
        translation = provider_chat(messages, temperature=0.3, max_tokens=2048)
        
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
