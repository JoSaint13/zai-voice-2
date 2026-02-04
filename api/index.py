"""
Clawdbot API - Flask backend for Vercel
Uses Z.AI API directly (https://api.z.ai)
"""

import os
import base64
import tempfile
import traceback
import sqlite3
import json
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Load env vars
load_dotenv()

# Get the project root directory (parent of api/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC_DIR = os.path.join(PROJECT_ROOT, 'public')
DB_PATH = os.path.join(PROJECT_ROOT, 'hotel_assistant.db')

app = Flask(__name__, static_folder=PUBLIC_DIR, static_url_path='')
CORS(app)  # Enable CORS for all routes
app.config['PROPAGATE_EXCEPTIONS'] = True  # Show full error traces

# Z.AI API Configuration
ZAI_API_KEY = os.getenv("ZHIPUAI_API_KEY")  # Keeping var name for compatibility
if not ZAI_API_KEY:
    raise ValueError("ZHIPUAI_API_KEY environment variable is required")

ZAI_BASE_URL = "https://api.z.ai/api"
ZAI_HEADERS = {
    "Authorization": f"Bearer {ZAI_API_KEY}",
    "Content-Type": "application/json",
    "Accept-Language": "en-US,en"
}

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
    
    if 'RateLimitError' in error_type:
        return "⚠️ Too many requests. Please wait a moment and try again."
    
    if 'InvalidRequestError' in error_type:
        return "❌ Invalid request. Please try rephrasing your message."
    
    # Generic fallback
    return f"⚠️ Something went wrong: {error_str[:100]}. Please try again."


@app.route("/", methods=["GET"])
def home():
    """Serve the main frontend page."""
    return send_from_directory(PUBLIC_DIR, 'index.html')


@app.route("/features", methods=["GET"])
def features():
    """Redirect to main page (features are now merged)."""
    return send_from_directory(PUBLIC_DIR, 'index.html')


@app.route("/<path:filename>", methods=["GET"])
def serve_static(filename):
    """Serve static files from public directory."""
    if os.path.exists(os.path.join(PUBLIC_DIR, filename)):
        return send_from_directory(PUBLIC_DIR, filename)
    return jsonify({"error": "Not found"}), 404


@app.route("/health", methods=["GET"])
@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint to verify API connectivity."""
    try:
        # Quick test with Z.AI API
        response = requests.get(
            f"{ZAI_BASE_URL}/paas/v4/models",
            headers=ZAI_HEADERS,
            timeout=5.0
        )
        return jsonify({
            "status": "healthy" if response.status_code == 200 else "degraded",
            "api_configured": True,
            "api_version": "Z.AI v4"
        })
    except Exception as e:
        return jsonify({
            "status": "degraded",
            "api_configured": bool(ZAI_API_KEY),
            "error": str(e)
        }), 503


@app.route("/api/hotel/<hotel_id>", methods=["GET"])
def get_hotel_config(hotel_id):
    """Get public hotel configuration for the frontend widget."""
    try:
        hotel_info, _ = get_hotel_context(hotel_id)
        if not hotel_info:
            return jsonify({"error": "Hotel not found"}), 404
            
        return jsonify({
            "name": hotel_info['name'],
            "description": hotel_info.get('description', 'AI Concierge Service'),
            # In a real app, these would come from a 'branding' JSON column
            "theme_color": "#2c3e50" 
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
    """Chat with GLM-4.7 via Z.AI API - Hotel Assistant Mode."""
    try:
        data = request.get_json()

        if "message" not in data:
            return jsonify({"error": "message required"}), 400

        session_id = data.get("session_id", "default")
        hotel_id = data.get("hotel_id")
        user_message = data["message"]

        # Get hotel context if available
        hotel_info = None
        recommendations = []
        if hotel_id:
            hotel_info, recommendations = get_hotel_context(hotel_id)

        # Build System Prompt
        system_prompt = "You are a helpful and professional Hotel Concierge AI."
        if hotel_info:
            system_prompt += f"\nYou work at {hotel_info['name']}."
            if hotel_info['knowledge_base']:
                system_prompt += f"\n\nHOTEL KNOWLEDGE BASE:\n{hotel_info['knowledge_base']}"
            
            if recommendations:
                rec_text = "\n".join([f"- {r['name']} ({r['category']}): {r['description']}" for r in recommendations])
                system_prompt += f"\n\nLOCAL RECOMMENDATIONS:\n{rec_text}"
                
            system_prompt += "\n\nINSTRUCTIONS:\n"
            system_prompt += "- Answer questions based ONLY on the provided Knowledge Base and Recommendations.\n"
            system_prompt += "- If you don't know the answer, politely say you will check with the front desk.\n"
            system_prompt += "- Be polite, warm, and brief."
        else:
            system_prompt += " You are currently in demo mode with no specific hotel data."

        # Get or create conversation history
        if session_id not in conversations:
            conversations[session_id] = [{
                "role": "system",
                "content": system_prompt
            }]
        else:
            # Update system prompt if it's the first message (in case hotel changed context)
            if conversations[session_id][0]['role'] == 'system':
                conversations[session_id][0]['content'] = system_prompt

        # Add user message
        conversations[session_id].append({
            "role": "user",
            "content": user_message
        })

        # Tools definition
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "request_late_checkout",
                    "description": "Request a late checkout for the guest.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "time": {"type": "string", "description": "Requested time (e.g. 2:00 PM)"},
                            "reason": {"type": "string", "description": "Reason (optional)"}
                        },
                        "required": ["time"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "contact_front_desk",
                    "description": "Escalate complex issues or requests to human staff.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "issue": {"type": "string", "description": "Description of the issue or request"}
                        },
                        "required": ["issue"]
                    }
                }
            }
        ]

        # Call GLM-4.7 via Z.AI API
        print(f"Calling GLM-4.7 API for session {session_id}...")
        
        payload = {
            "model": "glm-4.7",
            "messages": conversations[session_id],
            "temperature": 0.7, 
            "top_p": 0.7,
            "max_tokens": 500,
            "stream": False,
            "tools": tools
        }
        
        response = requests.post(
            f"{ZAI_BASE_URL}/paas/v4/chat/completions",
            headers=ZAI_HEADERS,
            json=payload,
            timeout=30.0
        )
        
        print(f"API response status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            message = result["choices"][0]["message"]
            
            # Handle Tool Calls
            tool_calls = message.get("tool_calls")
            if tool_calls:
                # Append assistant message with tool calls to history
                conversations[session_id].append(message)
                
                for tool_call in tool_calls:
                    function_name = tool_call['function']['name']
                    args = json.loads(tool_call['function']['arguments'])
                    print(f"Tool Executed: {function_name} with {args}")
                    
                    # Mock execution result
                    tool_result = f"Request received for {function_name}. Staff notified."
                    if function_name == "request_late_checkout":
                         # In a real app, you'd insert into DB here
                        tool_result = f"Late checkout request for {args.get('time')} confirmed. Cost is €50. Added to bill."
                    
                    conversations[session_id].append({
                        "role": "tool",
                        "tool_call_id": tool_call['id'],
                        "content": tool_result
                    })
                
                # Follow-up call to get final answer
                payload["messages"] = conversations[session_id]
                del payload["tools"] # Don't loop infinitely
                
                follow_up = requests.post(
                    f"{ZAI_BASE_URL}/paas/v4/chat/completions",
                    headers=ZAI_HEADERS, json=payload, timeout=30.0
                )
                
                if follow_up.status_code == 200:
                    message = follow_up.json()["choices"][0]["message"]
                    # fall through to normal processing

            # GLM-4.7 logic for content vs reasoning
            reasoning = message.get("reasoning_content", "")
            content = message.get("content", "")
            
            if not content and reasoning:
                import re
                quotes = re.findall(r'"([^"]+)"', reasoning)
                if quotes:
                    assistant_message = quotes[-1]
                else:
                    lines = [l.strip() for l in reasoning.split('\n') if l.strip()]
                    assistant_message = lines[-1] if lines else reasoning[:200]
            else:
                assistant_message = content or reasoning
            
            print(f"Assistant message: {assistant_message}")

            # Save to history
            conversations[session_id].append({
                "role": "assistant",
                "content": assistant_message
            })

            return jsonify({
                "response": assistant_message,
                "success": True
            })
        else:
            error_detail = response.text
            print(f"API Error: {error_detail}")
            return jsonify({
                "error": f"API error: {response.status_code}",
                "success": False
            }), response.status_code

    except Exception as e:
        error_msg = get_user_friendly_error(e)
        print(f"Error in /api/chat: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        traceback.print_exc()
        # Pop the user message if API call failed
        if session_id in conversations and len(conversations[session_id]) > 1:
            conversations[session_id].pop()
        return jsonify({"error": error_msg, "success": False}), 500


@app.route("/api/voice-chat", methods=["POST"])
def voice_chat():
    """Complete voice chat: transcribe + respond using Z.AI API."""
    try:
        data = request.get_json()

        if "audio_base64" not in data:
            return jsonify({"error": "audio_base64 required"}), 400

        session_id = data.get("session_id", "default")

        # Step 1: Transcribe with Z.AI API
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

        # Step 2: Chat with GLM-4.7 via Z.AI API
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

        payload = {
            "model": "glm-4.7",
            "messages": conversations[session_id],
            "temperature": 0.95,
            "stream": False
        }
        
        chat_response = requests.post(
            f"{ZAI_BASE_URL}/paas/v4/chat/completions",
            headers=ZAI_HEADERS,
            json=payload,
            timeout=30.0
        )
        
        if chat_response.status_code != 200:
            return jsonify({"error": "Chat failed", "success": False}), 500

        assistant_message = chat_response.json()["choices"][0]["message"]["content"]

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


# Export for Vercel
handler = app

if __name__ == "__main__":
    print(f"📁 Serving static files from: {PUBLIC_DIR}")
    print(f"🌐 Frontend: http://localhost:8000")
    print(f"🌐 Features: http://localhost:8000/features")
    print(f"📡 API Docs: http://localhost:8000/api/health")
    app.run(debug=True, host='0.0.0.0', port=8000)
