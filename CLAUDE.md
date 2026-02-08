# CLAUDE.md - Project Context for Claude Code

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
| Speech-to-Text | GLM-ASR-2512 | 20+ languages, dialect support |
| Conversation | GLM-4.7 | Intent handling, RAG, reasoning |
| Text-to-Speech | Browser TTS / GLM-4-Voice | Voice output |
| Image Generation | CogView-4 | Destination previews |
| Video Generation | CogVideoX | Tour videos |
| Backend | Flask (Python 3.11+) | API server |
| Frontend | Vanilla HTML/CSS/JS | Mobile-first web UI |
| Deployment | Vercel | Serverless hosting |

### API Provider

All AI models are from **Z.AI** (ZhipuAI):
- API Base: `https://open.z.ai/api/paas/v4/`
- SDK: `zhipuai` Python package
- Auth: `ZHIPUAI_API_KEY` environment variable

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
- `POST /api/transcribe` - Audio → Text (GLM-ASR)
- `POST /api/chat` - Text → Response (GLM-4.7)
- `POST /api/voice-chat` - Audio → Response (combined)
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
export ZHIPUAI_API_KEY='your_key_here'

# Run locally
python api/index.py
# Opens at http://localhost:3000

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

### Calling Z.AI APIs

```python
from zhipuai import ZhipuAI
import os

client = ZhipuAI(api_key=os.getenv('ZHIPUAI_API_KEY'))

# Chat
response = client.chat.completions.create(
    model='glm-4.7',
    messages=[{'role': 'user', 'content': 'Hello'}]
)

# Transcribe
with open('audio.wav', 'rb') as f:
    result = client.audio.transcriptions.create(
        model='glm-asr-2512',
        file=f
    )

# Image generation
result = client.images.generations.create(
    model='cogview-4',
    prompt='Beautiful sunset'
)
```

### Modifying the UI

The UI is in `public/index.html`. Key sections:
- CSS variables in `:root` for theming
- Media queries for responsive design
- JavaScript at bottom for interactivity

---

## Current Status

### Version: 0.1.0 (MVP)

### Completed (Phase 1)
- [x] Voice pipeline (GLM-ASR → GLM-4.7)
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
- [ ] CogView-4 image generation
- [ ] CogVideoX video generation

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
| `ZHIPUAI_API_KEY` | Yes | Z.AI API authentication |
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
vercel env add ZHIPUAI_API_KEY

# View logs
vercel logs
```

### Local Development

```bash
# Run Flask dev server
python api/index.py

# Access at http://localhost:3000
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ZHIPUAI_API_KEY not set` | `export ZHIPUAI_API_KEY='...'` |
| Microphone not working | Check browser permissions |
| Slow responses | Check Z.AI API latency |
| Skill not triggering | Verify `can_handle()` logic |
| Vercel timeout | Keep functions under 10s |

---

## Links

- **Z.AI Docs**: https://docs.z.ai
- **GLM-ASR**: https://docs.z.ai/guides/audio/glm-asr-2512
- **GLM-4.7**: https://docs.z.ai/api/glm-4
- **CogView-4**: https://docs.z.ai/api/cogview
- **Vercel Docs**: https://vercel.com/docs

---

## Notes for Claude

1. **Always check VERSION and CHANGELOG.md** for current state
2. **Read PRD.md** for business requirements
3. **Read ARCHITECTURE.md** for technical design
4. **Use the skill system** in `src/skills/` for new features
5. **Test changes** with `pytest` and `scripts/demo.py`
6. **Mobile-first** - test UI on Galaxy S21 FE viewport (360x800)
7. **Z.AI models only** - don't suggest OpenAI/Anthropic alternatives
8. **Commit often** with descriptive messages
9. **Update docs** when adding features

---

**Last Updated:** 2026-02-08
**Version:** 0.1.0
