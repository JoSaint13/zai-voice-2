# NomadAI Voice Agent

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![Status](https://img.shields.io/badge/status-MVP-orange)
![License](https://img.shields.io/badge/license-MIT-green)

> Voice-first hotel smart assistant powered by Z.AI

**[Documentation](docs/INDEX.md)** | **[Changelog](CHANGELOG.md)** | **[Roadmap](docs/ROADMAP.md)**

---

## What is NomadAI?

NomadAI is an AI-powered voice assistant for hotels that combines:
- **Digital Concierge**: Room service, housekeeping, check-in/out
- **Sightseeing Expert**: Local recommendations, itineraries, bookings
- **Media Generation**: Destination previews with AI images/videos

## Tech Stack

| Component | Model | Purpose |
|-----------|-------|---------|
| Speech Recognition | GLM-ASR-2512 | 20+ languages, dialect support |
| Conversation | GLM-4.7 | Intelligent responses |
| Image Generation | CogView-4 | Destination previews |
| Video Generation | CogVideoX | Tour videos |

---

## Quick Start

### Web (Vercel)

```bash
# Deploy
vercel --prod

# Set API key
vercel env add ZHIPUAI_API_KEY
```

### Local

```bash
# Install
pip install -r requirements.txt

# Configure
export ZHIPUAI_API_KEY='your_key_here'

# Run
python api/index.py

# Open http://localhost:3000
```

---

## Features

### Voice Skills (18 total)

| Category | Skills |
|----------|--------|
| **Concierge** | Room service, housekeeping, amenities, WiFi, check-out, complaints, wake-up, billing |
| **Sightseeing** | Recommendations, itinerary, directions, events, booking, translation |
| **Media** | Image preview, video tour |
| **System** | Language switch, human handoff, repeat, slow down, reset |

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/transcribe` | POST | Audio → Text |
| `/api/chat` | POST | Text → Response |
| `/api/voice-chat` | POST | Audio → Response |
| `/api/reset` | POST | Clear session |

---

## Project Structure

```
zai-voice-2/
├── api/index.py           # Flask API
├── public/index.html      # Web UI
├── src/skills/            # Skill implementations
│   ├── base.py            # BaseSkill, Registry
│   ├── concierge.py       # Hotel services
│   ├── sightseeing.py     # Local exploration
│   └── media.py           # Image/video generation
├── tests/                 # Test suite
├── scripts/demo.py        # Pipeline demo
├── docs/                  # Documentation
│   ├── PRD.md             # Product requirements
│   ├── ARCHITECTURE.md    # System design
│   ├── ROADMAP.md         # Implementation plan
│   └── TEAM.md            # Team composition
├── CHANGELOG.md           # Version history
└── VERSION                # Current version
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
| Skill Implementation | ⏳ In Progress | Week 3-4 |
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

**Current:** `0.1.0` (2026-02-08)

See [CHANGELOG.md](CHANGELOG.md) for version history.

---

## License

MIT
