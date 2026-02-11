# Sprint 3 & Sprint 4 — Detailed Implementation Plan

> Phase 3 continuation: Multi-Language Quality + Performance & Caching
> **Current Version:** 0.2.1 | **Target Version:** 0.3.0

---

## Sprint 3: Multi-Language & TTS Quality

**Goal:** Validate and optimize all 9 supported languages end-to-end (STT → LLM → TTS).

### 3.1 Language-to-Voice Mapping

**Problem:** Currently all languages use `af_heart` (English female). Kokoro supports multiple language voices.

**Implementation:**

```python
# api/index.py — add after line ~53
LANGUAGE_VOICES = {
    "en": "af_heart",       # English — American female
    "ru": "af_heart",       # Russian — test available, fallback to af_heart
    "zh": "zf_xiaobei",     # Chinese — native female (if available)
    "ja": "jf_alpha",       # Japanese — native female (if available)
    "ko": "af_heart",       # Korean — fallback (test first)
    "es": "ef_dora",        # Spanish — native female (if available)
    "fr": "ff_siwis",       # French — native female (if available)
    "de": "af_heart",       # German — fallback (test first)
    "ar": "af_heart",       # Arabic — fallback (test first)
}
```

**Tasks:**
- [ ] Research Kokoro available voices via API (`GET /voices` or docs)
- [ ] Create `LANGUAGE_VOICES` mapping dict in `api/index.py`
- [ ] Update `call_chutes_tts()` to accept `language` param and auto-select voice
- [ ] Update `voice_chat()` to pass detected language to TTS
- [ ] Test each language voice — document which work vs fallback needed
- [ ] Add voice override in frontend settings (optional)

**Files:** `api/index.py` (TTS function + voice-chat endpoint)

---

### 3.2 STT Language Accuracy Validation

**Problem:** Whisper large-v3 supports all 9 languages but accuracy varies.

**Tasks:**
- [ ] Create test audio samples for each language (or use browser TTS to generate)
- [ ] Test STT transcription accuracy per language:
  - EN (English) — baseline
  - RU (Russian)
  - ZH (Chinese Mandarin)
  - JA (Japanese)
  - KO (Korean)
  - ES (Spanish)
  - FR (French)
  - DE (German)
  - AR (Arabic)
- [ ] Pass `language` hint to Whisper API (if supported) for better accuracy
- [ ] Document results in `docs/LANGUAGE_SUPPORT.md`
- [ ] Mark languages as: ✅ Production-ready / ⚠️ Usable / ❌ Not recommended

**Files:** `api/index.py` (STT function), `docs/LANGUAGE_SUPPORT.md` (new)

---

### 3.3 LLM Response Language Enforcement

**Problem:** MiMo-V2-Flash sometimes responds in English regardless of guest language.

**Current state:** System prompt says `"Reply in the same language the guest uses"` but this is not always respected.

**Implementation:**
```python
# In agent_loop() — after getting LLM response
def _detect_response_language(text: str) -> str:
    """Simple heuristic language detection based on character ranges."""
    # Check for CJK, Cyrillic, Arabic, etc.
    ...

def _enforce_language(response: str, expected_lang: str) -> str:
    """If response language doesn't match expected, retry with stronger prompt."""
    detected = _detect_response_language(response)
    if detected != expected_lang:
        # Retry with explicit instruction
        ...
```

**Tasks:**
- [ ] Add lightweight language detection function (character-range heuristic, no external lib)
- [ ] Add language enforcement check after `agent_loop()` response
- [ ] If mismatch: retry LLM call with stronger language instruction (max 1 retry)
- [ ] Log language mismatches for monitoring: `[lang_mismatch] expected=ru detected=en`
- [ ] Test with Russian, Chinese, Japanese, Arabic prompts
- [ ] Consider `BRAIN_LLM_FALLBACK` env var — use DeepSeek V3 for non-CN/EN if MiMo fails

**Files:** `api/index.py` (agent_loop, new helper functions)

---

### 3.4 Frontend Language Improvements

**Tasks:**
- [ ] Show detected language in chat messages (small badge)
- [ ] Add "auto-detect" option to language selector (let STT determine language)
- [ ] Persist language choice in localStorage
- [ ] Update placeholder text per language (e.g., "Введите сообщение..." for RU)

**Files:** `public/index.html`

---

### 3.5 Agent Skills for Sprint 3

Install before starting:
```bash
npx skills add aj-geddes/useful-ai-prompts@internationalization-i18n
npx skills add vudovn/antigravity-kit@i18n-localization
```

---

### Sprint 3 Deliverables

| Deliverable | Acceptance Criteria |
|-------------|-------------------|
| Voice mapping | Each language uses best available Kokoro voice |
| STT validation | 7/9 languages marked production-ready |
| Language enforcement | LLM responds in guest's language 95%+ of time |
| Language docs | `docs/LANGUAGE_SUPPORT.md` with test results |
| Version bump | v0.2.2 released |

---

## Sprint 4: Performance & Caching

**Goal:** Reduce latency, persist sessions, add observability for production monitoring.

### 4.1 Response Caching

**Problem:** Repeated questions (WiFi password, breakfast hours) hit LLM every time. FAQ answers are static per hotel.

**Implementation:**
```python
# api/index.py — FAQ cache using knowledge base
from functools import lru_cache
import hashlib

# In-memory cache for FAQ-type responses
_faq_cache = {}  # key: (hotel_id, question_hash) → value: (response, timestamp)
FAQ_CACHE_TTL = 3600  # 1 hour

def _check_faq_cache(hotel_id: str, question: str) -> str | None:
    """Return cached response if question matches a known FAQ pattern."""
    key = (hotel_id, hashlib.md5(question.lower().strip().encode()).hexdigest())
    if key in _faq_cache:
        resp, ts = _faq_cache[key]
        if time.time() - ts < FAQ_CACHE_TTL:
            return resp
        del _faq_cache[key]
    return None

FAQ_PATTERNS = [
    "wifi", "password", "breakfast", "check.?out", "pool",
    "gym", "parking", "restaurant", "room service", "checkout"
]
```

**Tasks:**
- [ ] Add FAQ pattern matching (regex list for common hotel questions)
- [ ] Implement in-memory LRU cache with TTL (1 hour, max 500 entries)
- [ ] Cache hit: skip LLM call, return cached response directly
- [ ] Cache invalidation: on hotel KB update or manual `/api/cache/clear`
- [ ] Add `X-Cache: HIT/MISS` header to responses for debugging
- [ ] Add `Cache-Control` headers for static assets (`public/index.html`)
- [ ] Log cache hit rate: `[cache] hotel=xxx hit_rate=0.35 total=100`

**Files:** `api/index.py` (new cache module, agent_loop integration)

---

### 4.2 Session Persistence

**Problem:** `conversations` dict is in-memory — lost on Vercel cold starts and redeploys.

**Current state:**
```python
conversations = {}  # line 259 — volatile, serverless-hostile
```

**Options evaluated:**

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| Vercel KV (Redis) | Server-side, persistent | Paid plan, added dependency | Skip for now |
| Client-side restore | Free, simple | Larger payloads, privacy | ✅ Implement |
| SQLite on /tmp | Works locally | Vercel /tmp is ephemeral | No benefit |

**Implementation — Client-side session restore:**
```javascript
// Frontend: send last N messages with each request
const MAX_CONTEXT_MESSAGES = 10;

function getSessionContext() {
    const history = chatHistory.slice(-MAX_CONTEXT_MESSAGES);
    return history.map(m => ({role: m.role, content: m.content}));
}

// Include in API call
fetch('/api/chat', {
    body: JSON.stringify({
        message: text,
        session_id: sessionId,
        context: getSessionContext()  // restore on cold start
    })
});
```

```python
# Backend: restore context from client payload
def agent_loop(user_message, session_id, ..., client_context=None):
    if session_id not in conversations and client_context:
        conversations[session_id] = [
            {"role": "system", "content": system_prompt},
            *client_context[-MAX_CONTEXT_MESSAGES:]
        ]
```

**Tasks:**
- [ ] Frontend: store chat history in `localStorage` (per session_id)
- [ ] Frontend: send last 10 messages as `context` field in API requests
- [ ] Backend: accept `context` param in `/api/chat` and `/api/voice-chat`
- [ ] Backend: restore conversation from client context on cold start
- [ ] Add session TTL — expire after 30 min of inactivity (server-side cleanup)
- [ ] Add `/api/session/status` endpoint — check if session is warm
- [ ] Limit context payload size (max 10 messages, max 8KB total)
- [ ] Test: cold start → send message with context → verify continuity

**Files:** `api/index.py` (agent_loop, chat endpoint), `public/index.html` (localStorage, context sending)

---

### 4.3 Observability & Structured Logging

**Problem:** Current logs are unstructured `logger.info()` strings — hard to query, no metrics.

**Implementation:**
```python
import json, time

def log_structured(event: str, **kwargs):
    """Emit structured JSON log line for observability."""
    entry = {
        "ts": time.time(),
        "event": event,
        **kwargs
    }
    logger.info(json.dumps(entry))

# Usage:
log_structured("stt_complete",
    session_id=sid, hotel_id=hid,
    language="ru", latency_ms=1250,
    chars=42, cached=False
)
```

**Tasks:**
- [ ] Create `log_structured()` helper function
- [ ] Add structured logging to all critical paths:
  - STT call (latency, language, success/error)
  - LLM call (latency, model, token_count, tool_calls)
  - TTS call (latency, voice, chars, success/error)
  - Cache hit/miss
  - Rate limit triggers
  - Session create/restore/expire
- [ ] Add request-level timing middleware (total e2e latency)
- [ ] Create `/api/metrics` endpoint returning:
  ```json
  {
    "uptime_s": 3600,
    "requests": {"total": 500, "chat": 300, "voice": 200},
    "avg_latency_ms": {"stt": 1200, "llm": 2500, "tts": 800},
    "errors": {"stt": 5, "llm": 2, "tts": 8},
    "cache_hit_rate": 0.35,
    "active_sessions": 12
  }
  ```
- [ ] Add error tracking: count errors per type, surface in `/api/metrics`
- [ ] Consider Vercel Analytics integration (web vitals, function duration)

**Files:** `api/index.py` (logging helper, metrics endpoint, middleware)

---

### 4.4 Latency Optimization

**Problem:** Voice chat e2e is ~6-8s (STT ~1.5s + LLM ~3-4s + TTS ~1.5s). Target: <5s.

**Tasks:**
- [ ] Profile each stage with precise timing
- [ ] Optimize LLM calls:
  - Reduce max_tokens for simple FAQ (256 vs 1024)
  - Use faster model for FAQ (Hermes 4 70B or DeepSeek V3 for simple queries)
  - Skip agent_loop for cached responses
- [ ] Optimize TTS:
  - Shorter sentences = faster audio generation
  - Pre-generate common phrases ("Your WiFi password is...")
- [ ] Optimize imports: lazy-load heavy modules on first use
- [ ] Add response time headers: `X-Latency-STT`, `X-Latency-LLM`, `X-Latency-TTS`
- [ ] Cold start optimization: measure and reduce import time on Vercel

**Files:** `api/index.py`

---

### 4.5 Agent Skills for Sprint 4

Install before starting:
```bash
npx skills add yonatangross/orchestkit@caching-strategies
npx skills add andrelandgraf/fullstackrecipes@observability-monitoring
```

---

### Sprint 4 Deliverables

| Deliverable | Acceptance Criteria |
|-------------|-------------------|
| FAQ caching | Common questions served from cache (hit rate >30%) |
| Session restore | Conversation survives cold starts via client context |
| Structured logs | All API calls logged as JSON with latency |
| Metrics endpoint | `/api/metrics` returns live stats |
| Latency reduction | Voice e2e < 6s (from ~8s) |
| Version bump | v0.3.0 released |

---

## Timeline Overview

```
Sprint 1 ✅  Deploy & Resilience (v0.2.0)
  └─ Retry logic, rate limiting, input validation

Sprint 2 ✅  Skill Wiring & KB (v0.2.1)
  └─ 11 tools, knowledge base, 4 new skills

Sprint 3 ⬜  Multi-Language & TTS (v0.2.2)
  └─ Voice mapping, STT validation, language enforcement

Sprint 4 ⬜  Performance & Caching (v0.3.0)
  └─ FAQ cache, session persistence, observability, latency
```

---

## Risk Register

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Kokoro lacks voices for RU/KO/AR | Medium | High | Use `af_heart` fallback — English voice still works |
| MiMo-V2-Flash poor quality in non-EN/ZH | High | Medium | Add `BRAIN_LLM_FALLBACK` → DeepSeek V3 |
| Client-side context too large | Low | Low | Cap at 10 messages / 8KB |
| FAQ cache serves stale data | Medium | Low | 1h TTL + manual invalidation endpoint |
| Vercel cold starts break sessions | High | High | Client-side restore eliminates dependency |
| Language detection false positives | Medium | Medium | Only enforce for non-Latin scripts; log-only for ambiguous |

---

## Success Metrics (Phase 3 Complete — v0.3.0)

| Metric | Current | Sprint 3 Target | Sprint 4 Target |
|--------|---------|-----------------|-----------------|
| Languages validated | 2 (EN, RU) | 7/9 | 7/9 |
| TTS voice coverage | 1 (af_heart) | 5+ voices | 5+ voices |
| Language accuracy | ~80% | 95%+ | 95%+ |
| Voice e2e latency | ~8s | ~7s | <6s |
| FAQ cache hit rate | 0% | — | >30% |
| Session persistence | None | — | Client-side restore |
| Structured logging | None | — | All API calls |
| Uptime monitoring | None | — | `/api/metrics` live |

---

**Created:** 2026-02-11
**Last Updated:** 2026-02-11
**Parent Plan:** [docs/PHASE3_PLAN.md](./PHASE3_PLAN.md)
