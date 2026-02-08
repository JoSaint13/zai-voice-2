# Clawdbot

Voice assistant powered by Z.AI's GLM-ASR + GLM-4.7 stack.

## Features

- **Speech Recognition**: GLM-ASR-2512 (cloud) or GLM-ASR-Nano-2512 (local)
- **Conversation**: GLM-4.7 for intelligent responses
- **Text-to-Speech**: Browser-native TTS
- **Deployment**: Vercel-ready

## Quick Start

### Web (Vercel)

1. Deploy to Vercel
2. Set environment variable: `ZHIPUAI_API_KEY`
3. Open the deployed URL

### Local CLI

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key
export ZHIPUAI_API_KEY='your_key_here'

# Run
python clawdbot.py
```

## Architecture

```
[User Speech] → GLM-ASR-2512 → [Text] → GLM-4.7 → [Response] → TTS → [Audio]
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/transcribe` | POST | Transcribe audio to text |
| `/api/chat` | POST | Chat with GLM-4.7 |
| `/api/voice-chat` | POST | Combined transcribe + chat |
| `/api/reset` | POST | Reset conversation |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ZHIPUAI_API_KEY` | Yes | Z.AI API key from [open.z.ai](https://open.z.ai) |

## Project Structure

```
├── api/
│   ├── index.py          # Flask API for Vercel
│   └── requirements.txt  # API dependencies
├── public/
│   └── index.html        # Web UI
├── clawdbot.py           # CLI version
├── requirements.txt      # CLI dependencies
└── vercel.json           # Vercel config
```

## License

MIT
