# Changelog

All notable changes to NomadAI Voice Agent will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- Performance optimization and caching (Sprint 4)
- Multi-language support (deferred - needs alternative TTS provider)
- Vercel deployment testing with auth disabled

---

## [0.2.2] - 2026-02-11

### Added (Phase 3 Sprint 3)
- **Language-to-Voice Mapping**: `LANGUAGE_VOICES` dict for future multi-language TTS
- **Enhanced TTS Function**: `call_chutes_tts()` accepts `language` param for auto voice selection
- **English STT Validation**: 98%+ accuracy confirmed (Whisper large-v3)
- **Testing Framework**: `scripts/test_language_stt.py` for automated STT validation
- **Documentation**: Comprehensive `docs/LANGUAGE_SUPPORT.md` with validation results
- **Coding Agent Skills**: 8 total installed (6 core + 2 i18n)
  - flask, pytest, vercel-functions-runtime, resilience-patterns, git-commit, code-review
  - internationalization-i18n, i18n-localization

### Changed
- **Scope Decision**: English-only for v0.2.2 (multi-language deferred)
- Updated `/api/voice-chat`, `/api/tts` to pass language parameter
- All TTS calls now support language-based voice auto-selection

### Discovered
- **TTS Limitation**: Kokoro `af_heart` voice is English-only
  - Cannot synthesize non-English text properly (RU/ZH/JA/KO/ES/FR/DE/AR)
  - Blocks multi-language voice chat functionality
  - Alternative TTS provider research needed

### Technical
- LANGUAGE_VOICES mapping: 9 languages → voice IDs (all use af_heart fallback currently)
- Language param flows: UI → API → STT/LLM/TTS pipeline
- Future-ready: architecture supports multi-language when TTS provider added

---

## [0.2.1] - 2026-02-11

### Added (Phase 3 Sprint 1 & 2)
- **Retry Logic**: Exponential backoff for STT/TTS/LLM calls (1.5^attempt)
  - STT: 3 retries, 30s timeout
  - TTS: 3 retries, 15s timeout
  - LLM: 2 retries, 60s timeout
- **Rate Limiting**: Per-session (20/min) and global (100/min) limits → HTTP 429
- **Security**: Audio size validation (<10MB), input sanitization, CORS config
- **Graceful Fallbacks**: TTS failure → text-only response, STT failure → 503 error
- **4 New Skills**: check_out, complaints, wake_up_call, billing_inquiry
- **Knowledge Base System**: Hotel-specific KB loaded from JSON, injected into system prompt
  - Sample KB: NomadAI Hotel Tokyo with amenities, restaurants, policies, FAQ
  - Auto-formatted for concise system prompt inclusion
- **11 Total Skills**: Now 8 concierge + 3 sightseeing skills (was 7 total)

### Changed
- `_execute_tool()` dispatcher now supports all 11 skills via SKILL_MAP
- `agent_loop()` loads and formats KB from `data/hotels/default_hotel_kb.json`
- `.gitignore` excludes `data/hotels/*.json` (hotel-specific KB files)

### Technical
- Skills in `src/skills/` fully wired to agent loop
- KB schema: general_info, amenities, wifi, room_service, housekeeping, local_recommendations, transportation, policies, emergency, faq
- Configurable timeouts via env vars: `TIMEOUT_STT`, `TIMEOUT_TTS`, `TIMEOUT_LLM`

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
