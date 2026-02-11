# NomadAI Voice Agent

![Version](https://img.shields.io/badge/version-0.2.0-blue)
![Status](https://img.shields.io/badge/status-Alpha-orange)
![License](https://img.shields.io/badge/license-MIT-green)

> Voice-first hotel smart assistant powered by Chutes.ai

**[Documentation](docs/INDEX.md)** | **[Changelog](CHANGELOG.md)** | **[Roadmap](docs/ROADMAP.md)**

---

## What is NomadAI?

NomadAI is an AI-powered voice assistant for hotels using an **OpenClaw-inspired agentic architecture** with tool-calling. A brain LLM decides which tools to invoke (room service, housekeeping, recommendations, etc.) in an autonomous agent loop — no hardcoded intent routing.

- **Digital Concierge**: Room service, housekeeping, amenities, WiFi info
- **Sightseeing Expert**: Local recommendations, itinerary planning
- **Voice Calls**: Simulated restaurant/venue calls with reservation handling

## Tech Stack

| Component | Provider | Purpose |
|-----------|----------|---------|
| 🧠 Brain LLM | Chutes.ai (MiMo-V2-Flash) | Reasoning, routing, tool-calling agent loop |
| 🎧 Speech-to-Text | Chutes.ai (Whisper Large V3) | Voice transcription |
| 🔊 Text-to-Speech | Chutes.ai (Kokoro) | Voice synthesis (raw WAV) |
| Translation | Brain LLM | Multilingual chat/translate |
| Backend | Flask (Python 3.11+) | API server |
| Frontend | Vanilla HTML/CSS/JS | Mobile-first web UI |
| Deployment | Vercel | Serverless hosting |

---

## Quick Start

### Web (Vercel)

```bash
# Deploy
vercel --prod

# Set API key
vercel env add CHUTES_API_KEY
```

### Local

```bash
# Install
pip install -r requirements.txt

# Configure
export CHUTES_API_KEY='cpk_your_key_here'

# Run
python api/index.py

# Open http://localhost:8088
```

---

## Features

### Agentic Tool-Calling

The brain LLM (MiMo-V2-Flash) receives 8 tool schemas and autonomously decides which to call:

| Tool | Description |
|------|-------------|
| `room_service` | Order food/drinks to room |
| `housekeeping` | Request cleaning, towels, supplies |
| `amenities_info` | Pool, gym, spa hours and details |
| `wifi_info` | Network name, password, troubleshooting |
| `local_recommendations` | Restaurants, attractions, shopping |
| `itinerary_plan` | Day plans and activity scheduling |
| `voice_call` | Simulated calls to restaurants/venues |
| `translate` | Translate text between languages |

### Voice Features

- **Hold-to-speak** recording with VAD (auto-stop on silence)
- **Wake word detection** via Web Speech API ("hey nomad", "привет номад")
- **Language selector**: EN, RU, ZH, JA, KO, ES, FR, DE, AR
- **TTS streaming** via SSE (sentence-by-sentence audio chunks)
- **Collapsible settings** drawer in voice tab

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | Text → Response (agent loop) |
| `/api/chat-stream` | POST | Streaming text chat via SSE |
| `/api/voice-chat` | POST | STT → agent loop → TTS |
| `/api/transcribe` | POST | Standalone STT |
| `/api/translate` | POST | Translation via brain LLM |
| `/api/health` | GET | Health check with version, model info |
| `/api/providers` | GET | List available models |
| `/api/reset` | POST | Clear session |

---

## Project Structure

```
zai-voice-2/
├── api/
│   ├── index.py           # Flask API (~1370 lines, agent loop + all logic)
│   └── requirements.txt   # Vercel Python dependencies
├── public/index.html      # Web UI (~1200 lines, mobile-first)
├── src/skills/            # Skill implementations
│   ├── base.py            # BaseSkill, SkillRegistry, Context
│   ├── chat_provider.py   # Shared Chutes.ai chat function
│   ├── concierge.py       # Hotel service skills
│   ├── sightseeing.py     # Local exploration skills
│   └── media.py           # Image/video generation
├── tests/                 # Test suite
├── scripts/demo.py        # Pipeline demo
├── docs/                  # Documentation
├── CHANGELOG.md           # Version history
├── Makefile               # Build/dev commands
└── VERSION                # Current version (0.2.0)
```

---

## Documentation

| Document | Audience |
|----------|----------|
| [PRD](docs/PRD.md) | Product/Business |
| [Architecture](docs/ARCHITECTURE.md) | Engineers |
| [Developer Guide](docs/readers/DEVELOPER.md) | Developers |
| [Operations Guide](docs/readers/OPERATIONS.md) | DevOps |
| [Business Overview](docs/readers/BUSINESS.md) | Stakeholders |

---

## Roadmap

| Phase | Status | Timeline |
|-------|--------|----------|
| Foundation | ✅ Done | Week 1-2 |
| Agentic Skills | ✅ Done | Week 3-4 |
| PMS Integration | 📋 Planned | Month 2 |
| Omnichannel | 📋 Planned | Month 3 |
| Revenue Optimization | 📋 Planned | Month 4 |

See [ROADMAP.md](docs/ROADMAP.md) for details.

---

## Team

| Agent | Model | Role |
|-------|-------|------|
| Brain | Opus 4.5 | Architecture, strategy |
| Dev | Sonnet 4.5 | Implementation |
| Runner | Haiku 4.5 | Testing, validation |

See [TEAM.md](docs/TEAM.md) for details.

---

## Version

**Current:** `0.2.0` (2026-02-11)

See [CHANGELOG.md](CHANGELOG.md) for version history.

---

## License

MIT
