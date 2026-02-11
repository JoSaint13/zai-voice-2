# Changelog

All notable changes to NomadAI Voice Agent will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- Intent router with Chutes.ai classification
- Functional concierge skills (room service, housekeeping)
- Sightseeing skills with RAG
- Image generation (provider TBD)
- Video generation (provider TBD)

---

## [0.2.0] - 2026-02-11

### Added
- **Agentic Architecture**: OpenClaw-inspired tool-calling agent loop (brain_llm = MiMo-V2-Flash)
- **Named LLM Roles**: brain_llm (reasoning), voice_listen_llm (STT/Whisper), speech_llm (TTS/Kokoro)
- **Voice Call Skill**: Mock telephony with simulated restaurant conversations
- **Wake Word Detection**: Browser-based trigger word detection ("hey nomad", "привет номад")
- **TTS Streaming**: SSE-based sentence-by-sentence audio streaming
- **Language Selector**: Voice tab language picker (EN/RU/ZH/JA/KO/ES/FR/DE/AR)
- **Dynamic Version**: Version read from VERSION file, displayed in UI via /api/health

### Fixed
- STT list response parsing (Whisper returns array, not dict)
- TTS direct Kokoro endpoint integration (binary WAV, not JSON)
- TTS voice parameter mapping (kokoro → af_heart)
- Vercel deployment crash (removed `handler = app` triggering vc_init issubclass bug)
- LLM responds in guest's language (explicit lang instruction in system prompt)

---

## [0.1.0] - 2026-02-08

### Added
- **Voice Pipeline**: ASR placeholder endpoints (speech-to-text not yet configured)
- **Conversation**: Chutes.ai chat integration for intelligent responses
- **Web UI**: Hold-to-speak interface with browser TTS
- **Skill System**: BaseSkill, SkillRegistry, ConversationContext architecture
- **Concierge Skills** (stubs): Room service, housekeeping, amenities, WiFi, check-out, complaints, wake-up, billing
- **Sightseeing Skills** (stubs): Recommendations, itinerary, directions, events, booking, translation, image preview, video tour
- **Media Skills** (stubs): Image/video generation placeholders
- **API Endpoints**: `/api/transcribe`, `/api/chat`, `/api/voice-chat`, `/api/reset`
- **Deployment**: Vercel configuration with auto-deploy
- **Testing**: pytest framework, demo script, API tests
- **Documentation**: PRD, Architecture, Roadmap, Team composition, Developer/Business/Operations guides

### Technical
- Flask backend with session management
- Chutes.ai HTTP integration
- Mobile-responsive web interface
- Multi-language input support (chat); ASR not yet configured

---

## Version History

| Version | Date | Highlights |
|---------|------|------------|
| 0.1.0 | 2026-02-08 | Initial MVP with voice pipeline and skill system |

---

## Upcoming Versions

### 0.2.0 (Target: Week 4)
- Functional intent routing
- Working concierge skills
- Multi-language validation

### 0.3.0 (Target: Month 2)
- PMS integration (Mews/Cloudbeds)
- Guest profile personalization

### 0.4.0 (Target: Month 3)
- WhatsApp channel
- SMS gateway
- Staff dashboard

### 1.0.0 (Target: Month 4)
- Production-ready release
- Revenue optimization features
- Full analytics dashboard
