# CLAUDE.md - Project Context for Claude Code

## MANDATORY: Use td for Task Management

You must run td usage --new-session at conversation start (or after /clear) to see current work.
Use td usage -q for subsequent reads.

> This file provides context for Claude when working on the NomadAI Voice Agent project.

---

## Project Overview

**NomadAI** is a voice-first AI assistant for hotels, combining:
- Digital concierge (room service, housekeeping, check-in/out)
- Sightseeing expert (local recommendations, itineraries)
- Media generation (destination images/videos)

### Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Speech-to-Text | *Unavailable* | Requires Chutes.ai ASR (removed) |
| Conversation | DeepSeek V3 (via Chutes) | Intent handling, reasoning |
| Text-to-Speech | Browser TTS | Voice output |
| Image Generation | *Text fallback* | Image generation (not available) unavailable |
| Video Generation | *Text fallback* | Video generation (not available) unavailable |
| Backend | Flask (Python 3.11+) | API server |
| Frontend | Vanilla HTML/CSS/JS | Mobile-first web UI |
| Deployment | Vercel | Serverless hosting |

### API Provider

All AI models are served via **Chutes.ai** (decentralized inference on Bittensor):
- Per-model slug URLs: `https://{slug}.chutes.ai/v1/chat/completions`
- Auth: `CHUTES_API_KEY` environment variable (Bearer token)
- 11 models available: DeepSeek V3/V3.1/V3.2/R1, Qwen3-32B/235B, Chutes LLM/4.6, Hermes 4 70B, Mistral Small 3.1, GPT-OSS 120B

---

## Project Structure

```
zai-voice-2/
├── api/
│   ├── index.py              # Flask API server (main entry)
│   └── requirements.txt      # Vercel Python dependencies
├── public/
│   └── index.html            # Web UI (mobile-optimized)
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
├── VERSION                   # Current version (0.1.0)
├── requirements.txt          # Local development deps
├── vercel.json               # Vercel configuration
└── pytest.ini                # Test configuration
```

---

## Key Files to Understand

### 1. API Server (`api/index.py`)

Main Flask application with endpoints:
- `POST /api/chat` - Text → Response (via Chutes.ai)
- `POST /api/translate` - Translation (prompt-based via Chutes.ai)
- `POST /api/transcribe` - *501 stub* (requires Chutes.ai ASR)
- `POST /api/voice-chat` - *501 stub* (requires Chutes.ai ASR)
- `POST /api/generate-slides` - *501 stub* (requires Chutes.ai agent)
- `POST /api/generate-video` - *501 stub* (requires Chutes.ai agent)
- `GET /api/providers` - List available models
- `POST /api/reset` - Clear session

Session state is stored in-memory (note: won't persist across Vercel cold starts).

### 2. Skill System (`src/skills/base.py`)

Core abstractions:
- `BaseSkill` - Abstract class for all skills
- `SkillRegistry` - Discovers and manages skills
- `ConversationContext` - Tracks conversation state
- `SkillResponse` - Standardized response format

### 3. Web UI (`public/index.html`)

Mobile-first design optimized for Samsung Galaxy S21 FE:
- Hold-to-speak voice recording
- Haptic feedback
- Safe area insets for notch
- Browser TTS for responses

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

### Adding a New Skill

1. Create skill in `src/skills/`:
```python
from .base import BaseSkill, SkillResponse, ConversationContext

class MySkill(BaseSkill):
    name = "my_skill"
    description = "Does something"

    def can_handle(self, intent: str, entities: dict) -> bool:
        return intent == "my_intent"

    async def execute(self, context: ConversationContext) -> SkillResponse:
        return SkillResponse.text("Response here")
```

2. Register in `src/skills/__init__.py`

3. Add tests in `tests/test_skills.py`

### Calling Chutes.ai APIs

```python
from src.skills.chat_provider import skill_chat

# Chat (used by all skills)
messages = [
    {"role": "system", "content": "You are a hotel concierge."},
    {"role": "user", "content": "What time is breakfast?"}
]
result = skill_chat(messages)
```

> Note: Image generation (Image generation (not available)), video generation (Video generation (not available)),
> and speech-to-text (ASR) are not available via Chutes.ai.
> These skills provide text descriptions as fallback.

### Modifying the UI

The UI is in `public/index.html`. Key sections:
- CSS variables in `:root` for theming
- Media queries for responsive design
- JavaScript at bottom for interactivity

---

## Current Status

### Version: 0.1.0 (MVP)

### Completed (Phase 1)
- [x] Voice pipeline (ASR → Chutes LLM)
- [x] Web UI with hold-to-speak
- [x] Vercel deployment
- [x] Skill system architecture
- [x] 18 skill stubs defined
- [x] Test framework
- [x] Documentation suite

### In Progress (Phase 2)
- [ ] Intent router implementation
- [ ] Functional concierge skills
- [ ] Functional sightseeing skills
- [ ] Multi-language validation

### Planned
- [ ] PMS integration (Mews, Cloudbeds)
- [ ] WhatsApp/SMS channels
- [ ] Image generation (not available) image generation
- [ ] Video generation (not available) video generation

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

| Variable | Required | Description |
|----------|----------|-------------|
| `CHUTES_API_KEY` | Yes | Chutes.ai API authentication |
| `FLASK_ENV` | No | `development` or `production` |
| `LOG_LEVEL` | No | `DEBUG`, `INFO`, `WARNING` |

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
python scripts/demo.py --api-url http://localhost:3000
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
| Skill not triggering | Verify `can_handle()` logic |
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

**Last Updated:** 2026-02-08
**Version:** 0.1.0
