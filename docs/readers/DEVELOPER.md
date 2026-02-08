# NomadAI - Developer Guide

> Technical guide for engineers building and extending NomadAI

**Version:** 0.1.0 | **Python:** 3.11+ | **Last Updated:** 2026-02-08

---

## Quick Links

| Resource | Description |
|----------|-------------|
| [CLAUDE.md](../../CLAUDE.md) | AI assistant context file |
| [Architecture](../ARCHITECTURE.md) | System design document |
| [API Reference](#api-layer-apiindexpy) | Endpoint documentation |
| [Skill Guide](#adding-new-skills) | How to add new skills |

---

## Quick Start

```bash
# Clone and setup
git clone https://github.com/JoSaint13/zai-voice-2.git
cd zai-voice-2

# Install dependencies
pip install -r requirements.txt

# Set API key
export ZHIPUAI_API_KEY='your_key_here'

# Run locally
python api/index.py

# Open http://localhost:3000
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Web/Mobile Client                       │
│                    (public/index.html)                       │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP/WebSocket
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      Flask API Layer                         │
│                      (api/index.py)                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ /transcribe │  │   /chat     │  │    /voice-chat      │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Skill Router                              │
│                 (src/skills/base.py)                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Intent Classification                    │   │
│  │         concierge | sightseeing | media | system      │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┬───────────────┐
          ▼               ▼               ▼               ▼
     ┌─────────┐    ┌──────────┐   ┌─────────┐    ┌─────────┐
     │Concierge│    │Sightseeing│  │  Media  │    │ System  │
     │  Skills │    │  Skills   │  │  Skills │    │ Skills  │
     └─────────┘    └──────────┘   └─────────┘    └─────────┘
          │               │               │               │
          ▼               ▼               ▼               ▼
     ┌─────────┐    ┌──────────┐   ┌─────────┐    ┌─────────┐
     │   PMS   │    │ RAG + Maps│  │CogView/ │    │ Config  │
     │  APIs   │    │   APIs   │   │CogVideo │    │  Store  │
     └─────────┘    └──────────┘   └─────────┘    └─────────┘
```

---

## Core Components

### 1. API Layer (`api/index.py`)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/transcribe` | POST | Audio → Text (GLM-ASR) |
| `/api/chat` | POST | Text → Response (GLM-4.7) |
| `/api/voice-chat` | POST | Audio → Response (combined) |
| `/api/reset` | POST | Clear session |

**Example Request:**
```python
import requests

response = requests.post('http://localhost:3000/api/chat', json={
    'message': 'What time is breakfast?',
    'session_id': 'guest-123'
})
print(response.json()['response'])
```

### 2. Skill System (`src/skills/`)

**BaseSkill Class:**
```python
from src.skills.base import BaseSkill, SkillResponse

class MySkill(BaseSkill):
    name = "my_skill"
    description = "Does something useful"

    def can_handle(self, intent: str, entities: dict) -> bool:
        return intent == "my_intent"

    async def execute(self, context: ConversationContext) -> SkillResponse:
        # Your logic here
        return SkillResponse.text("Here's the answer!")
```

**Registering Skills:**
```python
from src.skills.base import SkillRegistry
from src.skills.concierge import RoomServiceSkill

registry = SkillRegistry()
registry.register(RoomServiceSkill())
```

### 3. Z.AI Integration

**Speech-to-Text:**
```python
from zhipuai import ZhipuAI

client = ZhipuAI(api_key=os.getenv('ZHIPUAI_API_KEY'))

# Transcribe audio
with open('audio.wav', 'rb') as f:
    result = client.audio.transcriptions.create(
        model='glm-asr-2512',
        file=f
    )
print(result.text)
```

**Chat Completion:**
```python
response = client.chat.completions.create(
    model='glm-4.7',
    messages=[
        {'role': 'system', 'content': 'You are a hotel assistant.'},
        {'role': 'user', 'content': 'What time is checkout?'}
    ]
)
print(response.choices[0].message.content)
```

**Image Generation:**
```python
response = client.images.generations.create(
    model='cogview-4',
    prompt='Beautiful view of Tokyo Tower at sunset'
)
print(response.data[0].url)
```

---

## Adding New Skills

### Step 1: Create Skill File

```python
# src/skills/my_feature.py

from .base import BaseSkill, SkillResponse, ConversationContext

class MyFeatureSkill(BaseSkill):
    name = "my_feature"
    description = "Handles my feature requests"

    # Utterance patterns this skill handles
    patterns = [
        r"my feature",
        r"do the thing",
    ]

    def can_handle(self, intent: str, entities: dict) -> bool:
        return intent in ["my_feature_intent"]

    async def execute(self, context: ConversationContext) -> SkillResponse:
        user_input = context.current_message

        # Your business logic
        result = self.process(user_input)

        return SkillResponse.text(result)

    def process(self, input: str) -> str:
        # Implementation
        return f"Processed: {input}"
```

### Step 2: Register Skill

```python
# src/skills/__init__.py

from .my_feature import MyFeatureSkill

def register_all_skills(registry):
    # ... existing skills
    registry.register(MyFeatureSkill())
```

### Step 3: Add Tests

```python
# tests/test_my_feature.py

import pytest
from src.skills.my_feature import MyFeatureSkill

def test_can_handle():
    skill = MyFeatureSkill()
    assert skill.can_handle("my_feature_intent", {})
    assert not skill.can_handle("other_intent", {})

@pytest.mark.asyncio
async def test_execute():
    skill = MyFeatureSkill()
    context = MockContext(message="do the thing")
    response = await skill.execute(context)
    assert "Processed" in response.text
```

---

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_skills.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run demo script
python scripts/demo.py
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ZHIPUAI_API_KEY` | Yes | Z.AI API key |
| `FLASK_ENV` | No | development/production |
| `LOG_LEVEL` | No | DEBUG/INFO/WARNING |

---

## Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod

# Set environment variable
vercel env add ZHIPUAI_API_KEY
```

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "api/index.py"]
```

```bash
docker build -t nomadai .
docker run -p 3000:3000 -e ZHIPUAI_API_KEY=xxx nomadai
```

---

## Code Style

- Python: PEP 8, type hints
- Max line length: 100
- Docstrings: Google style
- Tests: pytest with async support

```bash
# Format code
black src/ tests/

# Lint
flake8 src/ tests/

# Type check
mypy src/
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ZHIPUAI_API_KEY not set` | `export ZHIPUAI_API_KEY='...'` |
| Audio not recording | Check browser microphone permissions |
| Slow responses | Check network latency to Z.AI API |
| Skill not triggering | Verify `can_handle()` logic |

---

## Resources

- [Z.AI Documentation](https://docs.z.ai)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Architecture Doc](ARCHITECTURE.md)
- [PRD](PRD.md)
