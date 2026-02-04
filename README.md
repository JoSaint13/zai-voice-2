# Z.AI Voice Assistant

A full-stack voice assistant powered by Z.AI's GLM-ASR (speech recognition) and GLM-4.7 (language model). Features voice chat, translation, slide generation, and video effects - all in one unified interface.

![Z.AI](https://img.shields.io/badge/Powered%20by-Z.AI-blue)
![Python](https://img.shields.io/badge/Python-3.9+-green)
![Flask](https://img.shields.io/badge/Flask-3.0-lightgrey)

## Features

| Feature | Description | Pricing |
|---------|-------------|---------|
| **Voice Chat** | Speech-to-text + AI chat + text-to-speech | Standard API rates |
| **Translation** | 40+ languages, 6 translation strategies | $3 per 1M tokens |
| **Slides** | AI-generated presentations | $0.7 per 1M tokens |
| **Video Effects** | Transform photos into effect videos | $0.2 per video |

### Voice Assistant
- **GLM-ASR-2512**: Accurate speech recognition
- **GLM-4.7**: Intelligent conversational AI
- **Browser TTS**: Voice responses read aloud
- **Session Memory**: Maintains conversation context

### Translation Strategies
| Strategy | Best For |
|----------|----------|
| General | Standard translations |
| Paraphrased | Natural, fluent output |
| Two-Step | Literal → refined expression |
| Three-Stage | "Faithfulness, expressiveness, elegance" |
| Reflective | Expert feedback optimization |
| COT | Complex texts with reasoning |

### Slide Generator
- Professional presentations from any topic
- 3-30 slides per generation
- Styles: Professional, Creative, Minimal, Corporate

### Video Effects
| Template | Description |
|----------|-------------|
| French Kiss | Two people gradually kiss (2-person photo) |
| Body Shake | Rhythmic dance sequence |
| Sexy Me | Clothing transformation effect |

## Quick Start

### Prerequisites
- Python 3.9+
- Z.AI API Key ([Get one here](https://api.z.ai))

### Installation

```bash
# Clone repository
git clone <your-repo-url>
cd zai-voice-2

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r api/requirements.txt

# Set API key
export ZHIPUAI_API_KEY="your-api-key-here"

# Start server
python api/index.py
```

### Access

Open http://localhost:8000 in your browser.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Browser (http://localhost:8000)             │
│  ┌─────────┐ ┌───────────┐ ┌────────┐ ┌───────────────┐ │
│  │  Voice  │ │Translation│ │ Slides │ │ Video Effects │ │
│  │  Chat   │ │           │ │        │ │               │ │
│  └────┬────┘ └─────┬─────┘ └───┬────┘ └───────┬───────┘ │
└───────┼────────────┼───────────┼──────────────┼─────────┘
        │            │           │              │
        └────────────┴─────┬─────┴──────────────┘
                           │
┌──────────────────────────┼──────────────────────────────┐
│              Flask Server (api/index.py)                 │
│                     Port 8000                            │
├──────────────────────────┼──────────────────────────────┤
│                     Z.AI API                             │
│                 https://api.z.ai                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────────┐ │
│  │ GLM-ASR  │ │ GLM-4.7  │ │Translate │ │Slide/Video  │ │
│  │ (Speech) │ │  (Chat)  │ │  Agent   │ │   Agents    │ │
│  └──────────┘ └──────────┘ └──────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## API Reference

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main application |
| `/health` | GET | Health check |
| `/api/chat` | POST | Text chat |
| `/api/voice-chat` | POST | Voice → transcribe → chat |
| `/api/transcribe` | POST | Audio transcription |
| `/api/translate` | POST | Text translation |
| `/api/generate-slides` | POST | Create presentation |
| `/api/generate-video` | POST | Generate video effect |
| `/api/reset` | POST | Clear session |

### Examples

**Chat**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "session_id": "my-session"}'
```

**Translation**
```bash
curl -X POST http://localhost:8000/api/translate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello world",
    "source_lang": "English",
    "target_lang": "Chinese",
    "strategy": "general"
  }'
```

**Generate Slides**
```bash
curl -X POST http://localhost:8000/api/generate-slides \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "AI Market Analysis 2024",
    "num_slides": 10,
    "style": "professional"
  }'
```

## Project Structure

```
zai-voice-2/
├── api/
│   ├── index.py           # Flask server (API + static files)
│   └── requirements.txt   # Server dependencies
├── public/
│   └── index.html         # Unified frontend (all features)
├── clawdbot.py            # CLI version (local ASR model)
├── requirements.txt       # CLI dependencies
├── vercel.json            # Vercel deployment config
├── test_api.py            # API tests
└── test_voice_flow.py     # Voice flow tests
```

## Deployment

### Vercel

1. **Install Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **Add environment variable**
   ```bash
   vercel env add ZHIPUAI_API_KEY
   ```

3. **Deploy**
   ```bash
   vercel --prod
   ```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ZHIPUAI_API_KEY` | Yes | Z.AI API key |

## Development

### Running Tests

```bash
python test_api.py
python test_voice_flow.py
```

### CLI Version

For local development with on-device ASR:

```bash
pip install -r requirements.txt  # Includes PyTorch
python clawdbot.py
```

Note: Downloads GLM-ASR-Nano model (~1GB) on first run.

## Troubleshooting

| Error | Solution |
|-------|----------|
| `401 Unauthorized` | Check API key is set correctly |
| `Connection refused` | Start server with `python api/index.py` |
| `Port in use` | Kill existing process: `lsof -ti :8000 \| xargs kill` |
| `Microphone denied` | Allow microphone access in browser |
| `Timeout` | Check internet connection, try VPN |

## Browser Support

| Browser | Support |
|---------|---------|
| Chrome/Edge | Full |
| Firefox | Full |
| Safari | Partial (HTTPS required for mic) |

## Tech Stack

- **Backend**: Python, Flask, Flask-CORS
- **Frontend**: HTML5, CSS3, Vanilla JS
- **APIs**: Z.AI GLM-ASR-2512, GLM-4.7
- **Deployment**: Vercel (serverless)

## License

MIT

## Credits

Powered by [Z.AI](https://z.ai)
- GLM-4.7 language model
- GLM-ASR-2512 speech recognition
- Translation Agent
- Slide/Video Agents
