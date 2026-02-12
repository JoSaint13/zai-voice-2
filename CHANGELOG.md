# Changelog

All notable changes to NomadAI Voice Agent will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- Multi-language support (deferred - needs alternative TTS provider)
- Vercel deployment testing with auth disabled
- Further latency optimizations (parallel processing, model selection)

---

## [0.3.1] - 2026-02-12 (UX Improvement - Meta-Query Handling)

### Fixed
- **Meta-Query UX Issue**: "show me your knowledge" no longer dumps entire knowledge base
  - Added `is_meta_query()`: pattern-based detection for capability questions
  - Added `generate_capabilities_summary()`: structured 4-category response
  - Detects queries like: "what can you do", "show me your knowledge", "give me an overview"
  - Returns friendly summary (Hotel Services, Dining, Local Exploration, Personal Assistance)
  - Bypasses LLM call: instant response (~0ms vs 1-3s)
  - Logged as `meta_query_handled` event with `bypassed_llm=true`
- **Markdown Rendering**: Bot responses now properly format markdown
  - Added marked.js v11.2.0 for parsing markdown in frontend
  - Bold text (`**text**`) now renders as bold instead of raw markdown
  - Line breaks preserved correctly
  - Emojis display properly (🏨 🍴 🗺️ 📞)

### Changed
- Agent loop now checks for meta-queries before calling LLM
- Specific questions (e.g., "what time is breakfast") still use normal LLM flow
- Meta-query responses are voice-optimized (concise, scannable, actionable)
- Frontend `addMsg()` now parses bot responses as markdown (user messages remain plain text)

### Added
- Test suite: `scripts/test_meta_query_fix.sh` (6 test scenarios)
- Test suite: `scripts/test_markdown_rendering.sh` (visual verification guide)
- Documentation: `docs/KNOWLEDGE_ACCESS_STRATEGY.md` (3-tier response strategy)
- 8 meta-query patterns: capabilities, knowledge, overview, features, help
- CSS styling for markdown elements: paragraphs, bold, lists, code, links

### Performance
- Meta-queries: <100ms (instant, no LLM call)
- Specific queries: unchanged (1.4-3s depending on complexity)

---

## [0.3.0] - 2026-02-11 (Sprint 4 Complete - Performance & Caching)

### Added (Phase 3 Sprint 4.3 — Observability)
- **Structured Logging**: JSON logs for all API calls with metadata
  - `log_structured(event, **kwargs)`: unified logging function
  - STT events: language, chars, latency_ms, success
  - LLM events: model, iteration, tool_calls, response_chars, latency_ms
  - TTS events: voice, chars, audio_bytes, latency_ms
  - Chat/Voice events: session_id, cached, e2e latency
- **Metrics Infrastructure**:
  - METRICS dict: requests, latencies, errors, cache tracking
  - `track_latency(category, ms)`: record latencies (last 100 samples)
  - `track_error(category)`: count errors by type
  - `get_avg_latency(category)`: calculate averages
- **Monitoring Endpoints**:
  - `/api/metrics`: live observability metrics (uptime, requests, latencies, errors, cache)
  - Response headers: `X-Latency-Total` on all responses
  - Request counting by endpoint type (chat, voice, stream)

### Added (Phase 3 Sprint 4.4 — Latency Optimization)
- **Adaptive max_tokens**: Query complexity detection
  - `estimate_query_complexity()`: analyzes user message
  - Simple queries (FAQ, greetings): 256 tokens
  - Medium queries (standard): 512 tokens
  - Complex queries (planning, multi-step): 1024 tokens
  - Logged as `query_complexity` for monitoring
- **Detailed Latency Headers**:
  - `X-Latency-STT`: speech-to-text latency
  - `X-Latency-LLM`: LLM/agent loop latency
  - `X-Latency-TTS`: text-to-speech latency
  - `X-Latency-Total`: end-to-end latency
- **Test Script**: `scripts/test_sprint44_optimization.sh` for validation

### Performance Improvements
- **Simple queries**: ~60% faster (1.4-1.6s vs 3-4s with adaptive tokens)
- **FAQ cache hit**: instant response (~0ms)
- **Medium queries**: ~3s (balanced 512 tokens)
- **E2E tracking**: all stages monitored via headers & logs
- **Target achieved**: Simple queries now under 2 seconds!

### Technical Details (Sprint 4 Complete)
- FAQ cache: LRU + TTL, thread-safe, 500 max entries
- Session persistence: survives cold starts via localStorage
- Structured logs: JSON format ready for log aggregators
- Metrics: real-time stats at `/api/metrics`
- Adaptive tokens: 256/512/1024 based on complexity

---

## [0.2.3] - 2026-02-11 (Sprint 4.1 & 4.2)

### Added (Phase 3 Sprint 4.1 — FAQ Caching)
- **FAQ Response Cache**: Thread-safe LRU cache with TTL (500 max, 1h expiry)
- **FAQ Detection**: 15 regex patterns (wifi, breakfast, pool, parking, hours, etc.)
- **Cache Headers**: `X-Cache: HIT/MISS` for debugging
- **Cache API**: `/api/cache/clear` endpoint for manual invalidation
- **Cache Stats**: Integrated into `/api/health` endpoint (hits, misses, evictions, hit_rate)
- **Performance**: Instant response on cache hit (~0ms), 50%+ hit rate on FAQ questions

### Added (Phase 3 Sprint 4.2 — Session Persistence)
- **Backend Session Management**:
  - New session structure: `{session_id: {"messages": [...], "last_activity": timestamp}}`
  - Session TTL: 30 minutes of inactivity → auto-cleanup
  - `restore_session_from_context()`: accepts last 10 messages from client
  - Helper functions: `touch_session()`, `get_session_messages()`, `set_session_messages()`
- **Frontend LocalStorage**:
  - Chat history stored per session in `localStorage`
  - `getSessionContext()`: retrieves last 10 messages
  - All API calls (`/api/chat`, `/api/voice-chat`, `/api/chat-stream`) send `context` field
  - Reset button clears `localStorage`
- **Session Stats**: Active sessions and message counts in `/api/health`
- **Test Script**: `scripts/test_session_persistence.sh` for validation

### Added (UX Improvement)
- **Voice Interrupt**: Stop TTS audio immediately when user presses mic button
- `stopAllAudio()`: pauses audio, resets playback, clears queue
- Cleaner hold-to-speak experience (no audio overlap)

### Technical Details
- Session persistence survives Vercel cold starts via client-side restore
- FAQ cache: MD5 key normalization, case-insensitive matching
- Maximum context payload: 10 messages, ~8KB limit
- Migration: Old session format (list) → new format (dict) handled transparently

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
