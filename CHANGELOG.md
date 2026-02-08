# Changelog

All notable changes to NomadAI Voice Agent will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- Intent router with GLM-4.7 classification
- Functional concierge skills (room service, housekeeping)
- Sightseeing skills with RAG
- CogView-4 destination images
- CogVideoX tour videos

---

## [0.1.0] - 2026-02-08

### Added
- **Voice Pipeline**: GLM-ASR-2512 speech recognition with 20+ language support
- **Conversation**: GLM-4.7 chat integration for intelligent responses
- **Web UI**: Hold-to-speak interface with browser TTS
- **Skill System**: BaseSkill, SkillRegistry, ConversationContext architecture
- **Concierge Skills** (stubs): Room service, housekeeping, amenities, WiFi, check-out, complaints, wake-up, billing
- **Sightseeing Skills** (stubs): Recommendations, itinerary, directions, events, booking, translation, image preview, video tour
- **Media Skills** (stubs): CogView-4 image generation, CogVideoX video generation
- **API Endpoints**: `/api/transcribe`, `/api/chat`, `/api/voice-chat`, `/api/reset`
- **Deployment**: Vercel configuration with auto-deploy
- **Testing**: pytest framework, demo script, API tests
- **Documentation**: PRD, Architecture, Roadmap, Team composition, Developer/Business/Operations guides

### Technical
- Flask backend with session management
- Z.AI SDK integration (zhipuai)
- Mobile-responsive web interface
- Multi-language input support via GLM-ASR

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
