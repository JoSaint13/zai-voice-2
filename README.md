# Z.AI Voice Assistant with Multiple Features

A comprehensive voice assistant application powered by Z.AI (ZhipuAI) featuring:
- 🎤 Voice Chat with GLM-ASR + GLM-4.7
- 🌐 Translation Agent with 6 strategies
- 📊 Slide/Presentation Generator
- 🎥 Video Effects Templates

## Features

### 1. Voice Assistant
- **Speech-to-Text**: GLM-ASR-2512 for accurate transcription
- **AI Chat**: GLM-4.7 for intelligent responses
- **Text-to-Speech**: Browser-based TTS for voice responses
- Real-time conversation with session management

### 2. Translation Agent
Supports 40+ languages with 6 professional translation strategies:
- **General Translation**: Basic literal translation with cultural context
- **Paraphrased Translation**: Natural adaptation to target language
- **Two-Step Translation**: Literal first, then refined expression
- **Three-Stage Translation**: Follows "faithfulness, expressiveness, elegance"
- **Reflective Translation**: Expert feedback and optimization
- **COT Translation**: Chain-of-thought reasoning for complex texts

**Pricing**: $3 per 1M tokens

### 3. Slide/Presentation Generator
- One-click professional slide generation
- Smart information gathering
- Elegant visual design suggestions
- Customizable slide count and style
- Perfect for reports, presentations, portfolios

**Pricing**: $0.7 per 1M tokens

### 4. Video Effects Templates
Three popular special effects templates:
- **French Kiss** 💋: Two people gradually kiss (requires 2-person photo)
- **Body Shake** 💃: Rhythmic dance sequence (single person)
- **Sexy Me** ✨: Clothing transformation effect (single person)

**Pricing**: $0.2 per video

## Setup

### Prerequisites
- Python 3.11+
- ZhipuAI API key
- Node.js (for development)

### Installation

1. Clone the repository:
```bash
git clone <your-repo>
cd zai-voice-2
```

2. Create virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r api/requirements.txt
```

4. Set environment variable:
```bash
export ZHIPUAI_API_KEY="your-api-key-here"
```

5. Run the backend:
```bash
python api/index.py
```

6. Serve the frontend (in a separate terminal):
```bash
cd public
python -m http.server 8080
```

7. Open in browser:
- Main features: http://localhost:8080/zai-features.html
- Original voice chat: http://localhost:8080/index.html

## API Endpoints

### Chat & Voice
- `POST /api/chat` - Text chat with AI
- `POST /api/transcribe` - Audio transcription
- `POST /api/voice-chat` - Complete voice interaction
- `POST /api/reset` - Reset conversation

### Z.AI Features
- `POST /api/translate` - Translate text with strategies
- `POST /api/generate-slides` - Generate presentation slides
- `POST /api/generate-video` - Create video effects
- `GET /api/health` - Health check

## Deployment to Vercel

### Requirements
1. Remove the root `requirements.txt` (heavy ML dependencies not needed)
2. Keep `api/requirements.txt` minimal:
```txt
flask==3.0.0
flask-cors
zhipuai>=2.0.0
```

3. Set environment variable in Vercel:
```
ZHIPUAI_API_KEY=your-api-key
```

4. Deploy:
```bash
vercel --prod
```

## Configuration

### Frontend Configuration
Edit the API base URL in HTML files:
```javascript
const API_BASE = 'http://localhost:3000';  // Local
// const API_BASE = 'https://your-app.vercel.app';  // Production
```

### Backend Configuration
The backend automatically handles CORS and timeout settings:
- Timeout: 60 seconds for API calls
- CORS: Enabled for all routes
- Error handling: User-friendly messages

## Usage Examples

### Translation
```javascript
POST /api/translate
{
  "text": "Hello world",
  "source_lang": "English",
  "target_lang": "Chinese",
  "strategy": "general"
}
```

### Slide Generation
```javascript
POST /api/generate-slides
{
  "topic": "AI Market Analysis",
  "num_slides": 10,
  "style": "professional"
}
```

### Video Generation
```javascript
POST /api/generate-video
{
  "image_base64": "base64_image_data...",
  "template": "french_kiss"
}
```

## Troubleshooting

### API Timeout Issues
If you encounter timeout errors:
1. Check your internet connection
2. Verify API key is valid
3. Try with a VPN if in restricted regions
4. Check Z.AI service status

### CORS Issues
Make sure both servers are running:
- Backend: http://localhost:3000
- Frontend: http://localhost:8080

### Connection Errors
User-friendly error messages will appear:
- ⏱️ Timeout: "The AI service is taking too long..."
- 🔌 Connection: "Unable to connect to the AI service..."
- 🔑 Auth: "Authentication failed. Check your API key..."

## Features Roadmap

- [ ] Real ASR recording with GLM-ASR-2512
- [ ] Actual Z.AI video generation API integration
- [ ] PDF export for generated slides
- [ ] Multi-language UI
- [ ] Voice cloning features
- [ ] Image generation with CogView

## License

MIT

## Credits

Powered by [Z.AI](https://z.ai) (ZhipuAI)
- GLM-4.7 language model
- GLM-ASR-2512 speech recognition
- Z.AI Translation Agent
- Z.AI Slide Generator
- Z.AI Video Template Agent
