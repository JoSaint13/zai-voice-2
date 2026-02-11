# NomadAI Voice Agent - Architecture Design

**Version:** 2.0
**Date:** 2026-02-11
**Status:** Approved

---

## 1. System Overview

NomadAI Voice Agent is a voice-first digital concierge built on an **OpenClaw-inspired agentic architecture** with tool-calling. Instead of intent classification and skill routing, a brain LLM autonomously decides which tools to invoke in a loop — enabling flexible, multi-step task completion.

### Core Design Principles

1. **Agentic Autonomy**: The brain LLM decides which tools to call — no hardcoded routing
2. **Extensibility**: New capabilities are added as tool schemas, not code branches
3. **Graceful Degradation**: System remains functional when individual components fail
4. **Stateless Processing**: Request handlers are stateless; state is externalized
5. **Observable**: All operations are logged and traceable

---

## 2. Named LLM Roles

| Role | Model | Endpoint | Purpose |
|------|-------|----------|---------|
| 🧠 Brain LLM | MiMo-V2-Flash | `https://llm.chutes.ai/v1/chat/completions` | Reasoning, routing, tool-calling |
| 🎧 Voice Listen | Whisper Large V3 | `https://chutes-whisper-large-v3.chutes.ai/transcribe` | Speech-to-text |
| 🔊 Speech | Kokoro | `https://chutes-kokoro.chutes.ai/speak` | Text-to-speech (raw WAV) |

All models are served via **Chutes.ai** (decentralized inference on Bittensor), authenticated with `CHUTES_API_KEY` Bearer token.

---

## 3. Agent Loop Architecture

### 3.1 The Agent Loop (`agent_loop()`)

The core of the system is an iterative agent loop:

```
                    +------------------+
                    |   User Message   |
                    +--------+---------+
                             |
                             v
                    +------------------+
                    |   brain_chat()   |
                    |  (MiMo-V2-Flash) |
                    |  messages + tools |
                    +--------+---------+
                             |
                    +--------+---------+
                    |  tool_calls?     |
                    +--------+---------+
                      |              |
                   YES|              |NO
                      v              v
              +--------------+  +--------------+
              | Execute each |  | Return final |
              | tool_call    |  | text response|
              | Add results  |  +--------------+
              | to messages  |
              +--------------+
                      |
                      v
              +--------------+
              | Loop again   |
              | (max 5 iter) |
              +--------------+
```

### 3.2 Tool-Calling Flow

1. User message is added to conversation history
2. `brain_chat()` sends messages + 8 tool schemas to brain LLM
3. If response contains `tool_calls`:
   - Each tool call is dispatched to `_execute_tool(name, args)`
   - Tool results are appended as `tool` role messages
   - Loop back to step 2
4. If response is plain text: return to user
5. Max 5 iterations to prevent infinite loops

### 3.3 Tool Schemas (8 total)

| Tool | Parameters | Description |
|------|-----------|-------------|
| `room_service` | item, quantity, room, notes | Order food/drinks to room |
| `housekeeping` | request_type, room, urgency | Request cleaning, towels, supplies |
| `amenities_info` | amenity_type | Pool, gym, spa hours and details |
| `wifi_info` | issue_type | Network name, password, troubleshooting |
| `local_recommendations` | category, preferences, budget | Restaurants, attractions, shopping |
| `itinerary_plan` | duration, interests, pace | Day plans and activity scheduling |
| `voice_call` | venue, purpose | Simulated calls to restaurants/venues |
| `translate` | text, target_language | Translate text between languages |

### 3.4 Tool Execution

```python
def _execute_tool(name: str, args: dict) -> str:
    """Dispatch tool call to handler function."""
    handlers = {
        "room_service": _execute_room_service,
        "housekeeping": _execute_housekeeping,
        "amenities_info": _execute_amenities_info,
        "wifi_info": _execute_wifi_info,
        "local_recommendations": _execute_local_recommendations,
        "itinerary_plan": _execute_itinerary_plan,
        "voice_call": _execute_voice_call,
        "translate": _execute_translate,
    }
    return handlers[name](args)
```

---

## 4. Voice Pipeline

### 4.1 Voice Chat Flow

```
Guest                 Web App              API Server           Chutes.ai
  |                      |                    |                    |
  |---(1) Hold-to-speak->|                    |                    |
  |  (audio + VAD)       |                    |                    |
  |                      |---(2) POST /api/voice-chat------------>|
  |                      |       audio file   |                    |
  |                      |                    |---(3) Whisper STT->|
  |                      |                    |<---(4) Text--------|
  |                      |                    |                    |
  |                      |                    |---(5) agent_loop-->|
  |                      |                    |  (may loop with    |
  |                      |                    |   tool calls)      |
  |                      |                    |<---(6) Response----|
  |                      |                    |                    |
  |                      |                    |---(7) Kokoro TTS-->|
  |                      |<---(8) SSE audio---|<---(8) WAV---------|
  |<---(9) Play audio----|  (sentence chunks) |                    |
```

### 4.2 TTS Streaming

When `stream_tts=true`, the response is streamed via SSE:
- Text is split into sentences
- Each sentence is sent to Kokoro TTS independently
- Audio chunks (base64 WAV) are streamed as SSE events
- Client plays chunks sequentially for low-latency output

### 4.3 Wake Word Detection

The web UI uses Web Speech API for continuous listening:
- Configurable trigger phrases: "hey nomad", "привет номад"
- On detection, automatically starts recording
- Language-aware (matches selected language)

---

## 5. State Management

### 5.1 Session State

Session state is stored **in-memory** on the server:

```python
sessions = {}  # session_id -> {messages: [], language: "en", ...}
```

- Conversation history (messages array for brain LLM)
- Selected language
- Session metadata

> **Note:** In-memory state does not persist across Vercel cold starts.

### 5.2 Context Flow

The conversation context follows OpenAI chat format:
- `system` message: hotel concierge persona + language instruction
- `user` messages: guest utterances
- `assistant` messages: brain LLM responses
- `tool` messages: tool execution results

---

## 6. API Design

### 6.1 Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | Text chat via agent_loop |
| `/api/chat-stream` | POST | Streaming text chat via SSE |
| `/api/voice-chat` | POST | STT → agent_loop → TTS |
| `/api/transcribe` | POST | Standalone STT |
| `/api/translate` | POST | Translation via brain LLM |
| `/api/health` | GET | Health check with version, model info |
| `/api/providers` | GET | List available models |
| `/api/reset` | POST | Clear session |

### 6.2 Mock Voice Call

`_execute_voice_call()` simulates calling restaurants/venues:
- Returns mock responses for reservations, menus, hours
- Structured as a realistic phone call transcript
- Planned: replace with real telephony integration

---

## 7. Error Handling Strategy

### 7.1 Error Categories

| Category | Examples | Response Strategy |
|----------|----------|-------------------|
| `recognition_error` | STT failure, unclear audio | "I didn't catch that, could you repeat?" |
| `tool_error` | Tool execution failure | Brain LLM informed via tool result, retries |
| `backend_error` | API/service unavailable | "I'm having trouble connecting. Please try again." |
| `loop_limit` | Agent loop hits max iterations | Return best partial response |

### 7.2 Graceful Degradation

```
Level 1: Tool Execution Fails
  -> Tool returns error message to brain LLM
  -> Brain LLM responds conversationally without tool

Level 2: Brain LLM Unavailable
  -> Return static "experiencing difficulties" message

Level 3: STT/TTS Unavailable
  -> Fall back to text-only chat mode
```

---

## 8. Component Diagram

```
+------------------------------------------------------------------+
|                        NomadAI Voice Agent                        |
+------------------------------------------------------------------+
|                                                                    |
|  +------------------+       +------------------+                   |
|  |    Interfaces    |       |   Agent Engine   |                   |
|  +------------------+       +------------------+                   |
|  | - Web App (HTML) |       | - agent_loop()   |                   |
|  | - Chat tab       |  -->  | - brain_chat()   |                   |
|  | - Voice tab      |       | - _execute_tool()|                   |
|  | - Translate tab  |       | - Tool schemas   |                   |
|  +------------------+       +------------------+                   |
|                                    |                               |
|                                    v                               |
|  +------------------+       +------------------+                   |
|  |   AI Services    |       |   Tool Handlers  |                   |
|  +------------------+       +------------------+                   |
|  | - 🧠 MiMo-V2    |  <->  | - room_service   |                   |
|  | - 🎧 Whisper     |       | - housekeeping   |                   |
|  | - 🔊 Kokoro      |       | - amenities_info |                   |
|  +------------------+       | - wifi_info      |                   |
|                             | - local_recs     |                   |
|                             | - itinerary_plan |                   |
|                             | - voice_call     |                   |
|                             | - translate      |                   |
|                             +------------------+                   |
|                                                                    |
+------------------------------------------------------------------+
```

---

## 9. Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.11+ |
| Web Framework | Flask |
| AI Platform | Chutes.ai (REST API) |
| Brain LLM | MiMo-V2-Flash |
| STT | Whisper Large V3 |
| TTS | Kokoro |
| Deployment | Vercel (serverless, `@vercel/python`) |
| Frontend | Vanilla HTML/CSS/JS |

---

## 10. Extensibility

### Adding a New Tool

1. Define JSON schema in `TOOLS` array (OpenAI function-calling format)
2. Implement `_execute_<tool_name>(args)` handler
3. Add case to `_execute_tool()` dispatch
4. Brain LLM automatically discovers and uses the new tool

### Future Extensions

- **Real telephony**: Replace mock `voice_call` with Twilio/VAPI
- **PMS integration**: Add `check_reservation`, `post_charge` tools
- **External APIs**: Add `book_restaurant`, `get_directions` tools
- **Multi-modal**: Add image/video generation tools when available

---

**Document Owner:** NomadAI Engineering Team
**Last Updated:** 2026-02-11
