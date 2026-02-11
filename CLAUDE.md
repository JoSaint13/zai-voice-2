# CLAUDE.md - Project Context for Claude Code

## MANDATORY: Use td for Task Management

You must run td usage --new-session at conversation start (or after /clear) to see current work.
Use td usage -q for subsequent reads.

> This file provides context for Claude when working on the NomadAI Voice Agent project.

---

## Project Overview

**NomadAI** is a voice-first AI assistant for hotels using an **OpenClaw-inspired agentic architecture** with tool-calling:
- Digital concierge (room service, housekeeping, amenities, WiFi)
- Sightseeing expert (local recommendations, itineraries)
- Voice calls (simulated restaurant/venue calls)

### Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| 🧠 Brain LLM | MiMo-V2-Flash (via Chutes.ai) | Reasoning, routing, tool-calling agent loop |
| 🎧 Speech-to-Text | Whisper Large V3 (via Chutes.ai) | Voice transcription |
| 🔊 Text-to-Speech | Kokoro (via Chutes.ai) | Voice synthesis (raw WAV) |
| Backend | Flask (Python 3.11+) | API server |
| Frontend | Vanilla HTML/CSS/JS | Mobile-first web UI |
| Deployment | Vercel | Serverless hosting |

### API Provider

All AI models are served via **Chutes.ai** (decentralized inference on Bittensor):
- Brain LLM: `https://llm.chutes.ai/v1/chat/completions` (model: `XiaomiMiMo/MiMo-V2-Flash`)
- STT: `https://chutes-whisper-large-v3.chutes.ai/transcribe`
- TTS: `https://chutes-kokoro.chutes.ai/speak` (returns raw WAV)
- Auth: `CHUTES_API_KEY` environment variable (Bearer token)

---

## Project Structure

```
zai-voice-2/
├── api/
│   ├── index.py              # Flask API server (~1370 lines, agent loop + all logic)
│   └── requirements.txt      # Vercel Python dependencies
├── public/
│   └── index.html            # Web UI (~1200 lines, mobile-first)
├── src/
│   └── skills/               # Skill implementations
│       ├── __init__.py
│       ├── base.py           # BaseSkill, SkillRegistry, Context
│       ├── chat_provider.py  # Shared Chutes.ai chat function
│       ├── concierge.py      # Hotel service skills
│       ├── sightseeing.py    # Local exploration skills
│       └── media.py          # Image/video generation
├── tests/
│   ├── test_api.py           # API endpoint tests
│   └── test_skills.py        # Skill unit tests
├── scripts/
│   └── demo.py               # Pipeline validation script
├── docs/
│   ├── INDEX.md              # Documentation hub
│   ├── PRD.md                # Product requirements
│   ├── ARCHITECTURE.md       # System design
│   ├── ROADMAP.md            # Implementation plan
│   ├── TEAM.md               # AI agent team structure
│   └── readers/              # Audience-specific guides
│       ├── BUSINESS.md       # For stakeholders
│       ├── DEVELOPER.md      # For engineers
│       └── OPERATIONS.md     # For DevOps
├── CLAUDE.md                 # This file
├── README.md                 # Project overview
├── CHANGELOG.md              # Version history
├── VERSION                   # Current version (0.2.0)
├── Makefile                  # Build/dev commands
├── requirements.txt          # Local development deps
├── vercel.json               # Vercel configuration
└── pytest.ini                # Test configuration
```

---

## Key Files to Understand

### 1. API Server (`api/index.py`)

Main Flask application (~1370 lines) with agentic architecture:

**Core function: `agent_loop()`** — sends messages with `tools` array to brain LLM (MiMo-V2-Flash). If model returns `tool_calls`, executes them and loops (max 5 iterations).

**8 tool schemas:** `room_service`, `housekeeping`, `amenities_info`, `wifi_info`, `local_recommendations`, `itinerary_plan`, `voice_call`, `translate`.

**`brain_chat()`** — calls brain LLM endpoint with messages + tools.

**`_execute_voice_call()`** — simulates calling restaurants with reservation/menu/hours responses.

API endpoints:
- `POST /api/chat` — Text chat via agent_loop
- `POST /api/chat-stream` — Streaming text chat via SSE
- `POST /api/voice-chat` — STT → agent_loop → TTS (supports `stream_tts` SSE)
- `POST /api/transcribe` — Standalone STT (Whisper Large V3)
- `POST /api/translate` — Translation via brain LLM
- `GET /api/health` — Health check with version, model info
- `GET /api/providers` — List available models
- `POST /api/reset` — Clear session

Session state is stored in-memory (note: won't persist across Vercel cold starts).

### 2. Skill System (`src/skills/base.py`)

Core abstractions (used by index.py for skill metadata):
- `BaseSkill` - Abstract class for all skills
- `SkillRegistry` - Discovers and manages skills
- `ConversationContext` - Tracks conversation state
- `SkillResponse` - Standardized response format

### 3. Web UI (`public/index.html`)

Mobile-first design (~1200 lines) with tabs: Chat, Voice, Translate, Diagnostics.
- Hold-to-speak voice recording with VAD (auto-stop on silence)
- Wake word detection (Web Speech API, triggers: "hey nomad", "привет номад")
- Language selector (EN/RU/ZH/JA/KO/ES/FR/DE/AR)
- TTS streaming via SSE (sentence-by-sentence audio chunks)
- Collapsible settings drawer in voice tab
- Haptic feedback, safe area insets for notch

---

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key
export CHUTES_API_KEY='cpk_your_key_here'

# Run locally
python api/index.py
# Opens at http://localhost:8088

# Run tests
pytest tests/ -v

# Run demo
python scripts/demo.py

# Deploy to Vercel
vercel --prod
```

---

## Coding Conventions

### Python
- Python 3.11+
- Type hints on all functions
- Docstrings: Google style
- Async/await for I/O operations
- PEP 8 formatting

### JavaScript
- Vanilla JS (no frameworks)
- ES6+ features
- Async/await for API calls

### CSS
- CSS custom properties for theming
- Mobile-first media queries
- Flexbox for layouts

---

## Common Tasks

### Adding a New Tool

1. Define the tool schema in `api/index.py` (add to `TOOLS` array):
```python
{
    "type": "function",
    "function": {
        "name": "my_tool",
        "description": "Does something useful",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {"type": "string", "description": "..."}
            },
            "required": ["param1"]
        }
    }
}
```

2. Add handler function `_execute_my_tool(args)` in `api/index.py`

3. Add case to `_execute_tool()` dispatch in `api/index.py`

4. Add tests in `tests/test_api.py`

### Calling Chutes.ai APIs

```python
# Brain LLM chat (with tool-calling)
import requests
response = requests.post(
    "https://llm.chutes.ai/v1/chat/completions",
    headers={"Authorization": f"Bearer {CHUTES_API_KEY}"},
    json={
        "model": "XiaomiMiMo/MiMo-V2-Flash",
        "messages": messages,
        "tools": TOOLS  # optional tool schemas
    }
)

# STT (Whisper)
response = requests.post(
    "https://chutes-whisper-large-v3.chutes.ai/transcribe",
    headers={"Authorization": f"Bearer {CHUTES_API_KEY}"},
    files={"file": audio_data},
    data={"language": "en"}
)

# TTS (Kokoro) — returns raw WAV
response = requests.post(
    "https://chutes-kokoro.chutes.ai/speak",
    headers={"Authorization": f"Bearer {CHUTES_API_KEY}"},
    json={"text": "Hello", "language": "en"}
)
```

### Modifying the UI

The UI is in `public/index.html`. Key sections:
- CSS variables in `:root` for theming
- Media queries for responsive design
- JavaScript at bottom for interactivity

---

## Current Status

### Version: 0.2.0

### Completed (Phase 1 + Phase 2)
- [x] Voice pipeline (Whisper STT → MiMo brain → Kokoro TTS)
- [x] Web UI with hold-to-speak + VAD
- [x] Vercel deployment
- [x] Skill system architecture
- [x] Agentic tool-calling architecture (agent_loop)
- [x] 8 tool schemas implemented
- [x] Wake word detection (Web Speech API)
- [x] TTS streaming via SSE
- [x] Mock voice call simulation
- [x] Language selector (9 languages)
- [x] Test framework
- [x] Documentation suite

### Planned
- [ ] PMS integration (Mews, Cloudbeds)
- [ ] WhatsApp/SMS channels
- [ ] Real voice call integration
- [ ] Revenue optimization

---

## AI Agent Team

When working on this project, Claude operates as three specialized agents:

| Agent | Model | Role | Responsibilities |
|-------|-------|------|------------------|
| **Brain** | Opus | Architect | System design, complex problems, documentation |
| **Dev** | Sonnet | Developer | Feature implementation, bug fixes, integrations |
| **Runner** | Haiku | Tester | Tests, validation, quick tasks |

### Spawning Agents

```
Brain: Design the [feature] architecture considering [constraints]
Dev: Implement [feature] based on [design/spec]
Runner: Create tests for [feature] and validate
```

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CHUTES_API_KEY` | Yes | (none) | Chutes.ai API authentication |
| `BRAIN_LLM_MODEL` | No | `XiaomiMiMo/MiMo-V2-Flash` | Brain LLM model name |
| `BRAIN_LLM_ENDPOINT` | No | `https://llm.chutes.ai/v1/chat/completions` | Brain LLM endpoint |
| `CHUTES_STT_ENDPOINT` | No | `https://chutes-whisper-large-v3.chutes.ai/transcribe` | STT endpoint |
| `CHUTES_TTS_ENDPOINT` | No | `https://chutes-kokoro.chutes.ai/speak` | TTS endpoint |
| `CHUTES_TTS_MODEL` | No | `kokoro` | TTS model name |
| `CHUTES_STT_MODEL` | No | `openai/whisper-large-v3` | STT model name |

---

## Testing

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_skills.py -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Demo script (requires running API)
python scripts/demo.py --api-url http://localhost:8088
```

---

## Deployment

### Vercel (Production)

```bash
# Deploy
vercel --prod

# Set environment variable
vercel env add CHUTES_API_KEY

# View logs
vercel logs
```

### Local Development

```bash
# Run Flask dev server
python api/index.py

# Access at http://localhost:8088
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `CHUTES_API_KEY not set` | `export CHUTES_API_KEY='cpk_...'` |
| Microphone not working | Check browser permissions |
| Slow responses | Check Chutes.ai API latency |
| Skill not triggering | Check tool schema in `TOOLS` array, verify `_execute_tool()` dispatch |
| Vercel timeout | Keep functions under 10s |

---

## Links

- **Chutes.ai**: https://chutes.ai
- **Vercel Docs**: https://vercel.com/docs

---

## Notes for Claude

1. **Always check VERSION and CHANGELOG.md** for current state
2. **Read PRD.md** for business requirements
3. **Read ARCHITECTURE.md** for technical design
4. **Use the skill system** in `src/skills/` for new features
5. **Test changes** with `pytest` and `scripts/demo.py`
6. **Mobile-first** - test UI on Galaxy S21 FE viewport (360x800)
7. **Chutes.ai models only** - all inference goes through Chutes.ai provider
8. **Commit often** with descriptive messages
9. **Update docs** when adding features

---

**Last Updated:** 2026-02-11
**Version:** 0.2.0
