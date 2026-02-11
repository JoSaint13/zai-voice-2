# Phase 3: Production Hardening — v0.3.0

> Stabilize the agentic voice platform for production use with real error handling, skill wiring, and multi-language validation.

**Target Version:** 0.3.0
**Prerequisites:** v0.2.0 (agentic architecture, voice chat, TTS streaming)
**Status:** 📋 PLANNED

---

## Goals

1. **Reliable deployment** — Vercel deploys without errors, handles cold starts
2. **Resilient API** — STT/TTS/LLM failures are retried and gracefully degraded
3. **Real skill execution** — Wire `src/skills/` classes into agent_loop (replace inline stubs)
4. **Multi-language quality** — Validate all 9 languages end-to-end
5. **Performance** — Response caching, rate limiting, session persistence

---

## Sprint 1: Deploy & Resilience

### 1.1 Vercel Deployment Fix
- [ ] Verify current code deploys to Vercel successfully
- [ ] Test all endpoints on production URL (chat, voice-chat, transcribe, translate, health)
- [ ] Add `CHUTES_STT_ENDPOINT` and `CHUTES_TTS_ENDPOINT` to Vercel env vars
- [ ] Test cold start latency (<5s target)
- [ ] Add `/api/health` deep check (actually ping STT/TTS endpoints)

### 1.2 Error Recovery & Retry Logic
- [ ] Add retry with exponential backoff for `call_chutes_stt()` (max 3 retries)
- [ ] Add retry with exponential backoff for `call_chutes_tts()` (max 3 retries)
- [ ] Add retry for `brain_chat()` / agent_loop LLM calls (max 2 retries)
- [ ] Graceful fallback: if TTS fails after retries, return text-only response (no 502)
- [ ] Graceful fallback: if STT fails, return user-friendly error message
- [ ] Add timeout configuration per endpoint (STT: 30s, TTS: 15s, LLM: 60s)

### 1.3 Rate Limiting & Security
- [ ] Add per-session rate limiting (max 20 requests/minute)
- [ ] Add global rate limiting (max 100 requests/minute total)
- [ ] Validate `audio_base64` size (reject >10MB payloads)
- [ ] Sanitize user input before passing to LLM (prevent prompt injection basics)
- [ ] Add CORS configuration for production domain only

---

## Sprint 2: Skill Wiring & Enhancement

### 2.1 Wire `src/skills/` into Agent Loop
- [ ] Refactor `_execute_tool()` to dispatch to skill classes from `src/skills/`
- [ ] `room_service` → `ConciergeSkill.handle_room_service()`
- [ ] `housekeeping` → `ConciergeSkill.handle_housekeeping()`
- [ ] `amenities_info` → `ConciergeSkill.handle_amenities()`
- [ ] `wifi_info` → `ConciergeSkill.handle_wifi()`
- [ ] `local_recommendations` → `SightseeingSkill.handle_recommendations()`
- [ ] `itinerary_plan` → `SightseeingSkill.handle_itinerary()`
- [ ] Update `chat_provider.py` to use `brain_chat()` instead of old DeepSeek slug

### 2.2 New Tools
- [ ] Add `check_out` tool — guest checkout flow (currently stub)
- [ ] Add `complaints` tool — log and acknowledge guest complaints
- [ ] Add `wake_up_call` tool — schedule wake-up (mock → real later)
- [ ] Add `billing_inquiry` tool — guest folio summary (mock data)
- [ ] Update `SKILL_TOOLS` array with new tool schemas

### 2.3 Knowledge Base per Hotel
- [ ] Add `knowledge_base` field to hotel config (JSON with FAQ, menu, hours, policies)
- [ ] Inject knowledge base into system prompt when hotel_id is provided
- [ ] Create sample knowledge base for default hotel (2ada3c2b...)
- [ ] Skills read from knowledge base instead of hardcoded responses

---

## Sprint 3: Multi-Language & TTS Quality

### 3.1 Language Validation
- [ ] Test STT accuracy per language: EN, RU, ZH, JA, KO, ES, FR, DE, AR
- [ ] Test LLM response quality per language (MiMo-V2-Flash is Chinese-optimized)
- [ ] Document which languages work well vs need fallback
- [ ] If MiMo fails for a language, add `BRAIN_LLM_FALLBACK` env var (e.g., DeepSeek V3)

### 3.2 TTS Voice Per Language
- [ ] Map Kokoro voice IDs to languages:
  - EN → `af_heart` (default)
  - RU → test available Russian voices
  - ZH → test Chinese voices
  - JA → test Japanese voices
  - Other → find best matching voice or use `af_heart` fallback
- [ ] Pass language-appropriate voice to `call_chutes_tts()` automatically
- [ ] Add voice preview in settings drawer (play sample for selected voice)

### 3.3 Response Language Enforcement
- [ ] Verify system prompt language instruction works for all 9 languages
- [ ] Add language detection on LLM response — if wrong language, retry with stronger prompt
- [ ] Log language mismatches for monitoring

---

## Sprint 4: Performance & Caching

### 4.1 Response Caching
- [ ] Cache common STT results (identical audio → same text, skip re-transcription)
- [ ] Cache FAQ-type responses (wifi password, breakfast hours) per hotel
- [ ] Add `Cache-Control` headers for static assets
- [ ] Implement in-memory LRU cache (or Vercel KV if available)

### 4.2 Session Persistence
- [ ] Current: in-memory `conversations` dict (lost on cold start)
- [ ] Option A: Vercel KV for session storage
- [ ] Option B: Client-side session restore (send last N messages with each request)
- [ ] Implement chosen option
- [ ] Add session TTL (expire after 30 minutes of inactivity)

### 4.3 Observability
- [ ] Add structured logging (JSON format) for all API endpoints
- [ ] Log: session_id, hotel_id, language, latency_ms, tool_calls, error
- [ ] Add `/api/metrics` endpoint (request counts, avg latency, error rate)
- [ ] Add Vercel Analytics integration (if available)

---

## Success Criteria

| Metric | Target |
|--------|--------|
| Vercel deploy | ✅ No errors, all endpoints respond |
| Cold start latency | < 5 seconds |
| Voice chat e2e latency | < 8 seconds (STT + LLM + TTS) |
| STT retry success | > 95% after retries |
| TTS retry success | > 95% after retries |
| Language accuracy | 7/9 languages validated working |
| Skill coverage | 12 tools wired (8 existing + 4 new) |
| Knowledge base | 1 hotel with full FAQ/menu/hours |

---

## Dependencies

| Dependency | Status | Blocker? |
|------------|--------|----------|
| Chutes.ai API stability | ✅ Working | No |
| Kokoro multi-language voices | ❓ Unknown | Test needed |
| MiMo-V2-Flash multi-lang quality | ❓ Unknown | Test needed |
| Vercel KV (for sessions) | 📋 Optional | No — fallback exists |

---

## Risks

| Risk | Mitigation |
|------|------------|
| MiMo-V2-Flash poor quality in non-CN/EN languages | Add BRAIN_LLM_FALLBACK to DeepSeek V3 |
| Kokoro no voices for some languages | Use af_heart as universal fallback |
| Vercel cold starts too slow | Optimize imports, lazy-load heavy modules |
| In-memory sessions lost on deploy | Implement client-side session restore |

---

## File Changes Expected

| File | Changes |
|------|---------|
| `api/index.py` | Retry logic, rate limiting, skill dispatch refactor, new tools |
| `src/skills/concierge.py` | Implement real handlers (room_service, housekeeping, etc.) |
| `src/skills/sightseeing.py` | Implement real handlers (recommendations, itinerary) |
| `src/skills/chat_provider.py` | Switch from DeepSeek slug to brain_chat() |
| `public/index.html` | Voice preview, language-voice mapping |
| `data/hotels/` | Knowledge base JSON files per hotel |
| `tests/test_api.py` | Tests for retry, rate limit, new tools |

---

**Created:** 2026-02-11
**Next Review:** After Sprint 1 completion
