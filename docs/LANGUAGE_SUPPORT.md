# Language Support Documentation

> Multi-language validation results for NomadAI Voice Agent (Phase 3, Sprint 3)

**Last Updated:** 2026-02-11  
**Version:** 0.2.2 (in development)

---

## Supported Languages

| Code | Language | STT Status | LLM Status | TTS Voice | Overall |
|------|----------|------------|------------|-----------|---------|
| `en` | English | ✅ Production | ✅ Production | `af_heart` | ✅ Production Ready |
| `ru` | Russian | ⚠️ Testing | ⚠️ Testing | `af_heart` (fallback) | ⚠️ Validation Needed |
| `zh` | Chinese (Mandarin) | ⚠️ Testing | ⚠️ Testing | `af_heart` (fallback) | ⚠️ Validation Needed |
| `ja` | Japanese | ⚠️ Testing | ⚠️ Testing | `af_heart` (fallback) | ⚠️ Validation Needed |
| `ko` | Korean | ⚠️ Testing | ⚠️ Testing | `af_heart` (fallback) | ⚠️ Validation Needed |
| `es` | Spanish | ⚠️ Testing | ⚠️ Testing | `af_heart` (fallback) | ⚠️ Validation Needed |
| `fr` | French | ⚠️ Testing | ⚠️ Testing | `af_heart` (fallback) | ⚠️ Validation Needed |
| `de` | German | ⚠️ Testing | ⚠️ Testing | `af_heart` (fallback) | ⚠️ Validation Needed |
| `ar` | Arabic | ⚠️ Testing | ⚠️ Testing | `af_heart` (fallback) | ⚠️ Validation Needed |

**Legend:**
- ✅ **Production Ready** — Validated, performs well, recommended
- ⚠️ **Validation Needed** — Not yet tested, status unknown
- ❌ **Not Recommended** — Poor quality, frequent failures

---

## Language-to-Voice Mapping

The system automatically selects appropriate TTS voices based on detected language:

```python
# api/index.py — LANGUAGE_VOICES
{
    "en": "af_heart",       # English — American female (default)
    "ru": "af_heart",       # Russian — fallback (native voice TBD)
    "zh": "af_heart",       # Chinese — fallback (test zf_xiaobei if available)
    "ja": "af_heart",       # Japanese — fallback (test jf_alpha if available)
    "ko": "af_heart",       # Korean — fallback
    "es": "af_heart",       # Spanish — fallback (test ef_dora if available)
    "fr": "af_heart",       # French — fallback (test ff_siwis if available)
    "de": "af_heart",       # German — fallback
    "ar": "af_heart",       # Arabic — fallback
}
```

**Current State:** All languages use `af_heart` (English female voice) as fallback until native Kokoro voices are validated.

---

## Component Details

### 1. Speech-to-Text (STT) — Whisper Large V3

**Endpoint:** `https://chutes-whisper-large-v3.chutes.ai/transcribe`

| Language | Model Support | Accuracy (Expected) | Notes |
|----------|---------------|---------------------|-------|
| English | ✅ Native | >95% | Baseline, highest quality |
| Russian | ✅ Native | >90% | Cyrillic script supported |
| Chinese | ✅ Native | >85% | Mandarin optimized |
| Japanese | ✅ Native | >85% | Hiragana/Katakana/Kanji |
| Korean | ✅ Native | >80% | Hangul supported |
| Spanish | ✅ Native | >90% | High quality |
| French | ✅ Native | >90% | High quality |
| German | ✅ Native | >85% | Compound words |
| Arabic | ✅ Native | >80% | RTL text, diacritics |

**Testing Required:** Generate test audio samples for each language and validate transcription accuracy.

---

### 2. LLM (Brain) — MiMo-V2-Flash

**Endpoint:** `https://llm.chutes.ai/v1/chat/completions`  
**Model:** `XiaomiMiMo/MiMo-V2-Flash`

| Language | Model Support | Response Quality | Language Drift |
|----------|---------------|------------------|----------------|
| English | ✅ Native | Excellent | Rare |
| Russian | ⚠️ Unknown | Unknown | Unknown |
| Chinese | ✅ Optimized | Excellent (expected) | Rare |
| Japanese | ⚠️ Unknown | Unknown | Unknown |
| Korean | ⚠️ Unknown | Unknown | Unknown |
| Spanish | ⚠️ Unknown | Unknown | Unknown |
| French | ⚠️ Unknown | Unknown | Unknown |
| German | ⚠️ Unknown | Unknown | Unknown |
| Arabic | ⚠️ Unknown | Unknown | Unknown |

**Known Issue:** MiMo-V2-Flash may respond in English even when user speaks another language.

**Mitigation Strategy:**
- System prompt explicitly instructs: *"Reply in the same language the guest uses"*
- Next sprint: Add language detection + retry mechanism if mismatch detected
- Fallback option: `BRAIN_LLM_FALLBACK` env var to use DeepSeek V3 for non-CN/EN languages

---

### 3. Text-to-Speech (TTS) — Kokoro

**Endpoint:** `https://chutes-kokoro.chutes.ai/speak`  
**Model:** `kokoro`

| Language | Voice ID | Voice Quality | Accent | Status |
|----------|----------|---------------|--------|--------|
| English | `af_heart` | Excellent | American female | ✅ Validated |
| Russian | `af_heart` | Fair | English accent | ⚠️ Non-native fallback |
| Chinese | `af_heart` | Fair | English accent | ⚠️ Non-native fallback |
| Japanese | `af_heart` | Fair | English accent | ⚠️ Non-native fallback |
| Korean | `af_heart` | Fair | English accent | ⚠️ Non-native fallback |
| Spanish | `af_heart` | Fair | English accent | ⚠️ Non-native fallback |
| French | `af_heart` | Fair | English accent | ⚠️ Non-native fallback |
| German | `af_heart` | Fair | English accent | ⚠️ Non-native fallback |
| Arabic | `af_heart` | Fair | English accent | ⚠️ Non-native fallback |

**Action Required:** Research Kokoro API for available voices per language:
- Check if native voices exist for RU, ZH, JA, KO, ES, FR, DE, AR
- Test voice quality for each language
- Update `LANGUAGE_VOICES` mapping with validated voices

**Possible Kokoro Voices (to verify):**
- `zf_xiaobei` — Chinese female
- `jf_alpha` — Japanese female
- `ef_dora` — Spanish female
- `ff_siwis` — French female

---

## Testing Checklist

### Phase 1: STT Validation (⬜ Not Started)

For each language:
- [ ] Generate or record 5-10 test audio samples
- [ ] Test transcription via `/api/transcribe`
- [ ] Calculate word error rate (WER) or subjective accuracy
- [ ] Document results in this file

### Phase 2: LLM Validation (⬜ Not Started)

For each language:
- [ ] Send prompts in target language via `/api/chat`
- [ ] Verify response is in same language (not English)
- [ ] Test hotel-specific queries (WiFi, breakfast, room service)
- [ ] Document language drift issues

### Phase 3: TTS Validation (⬜ Not Started)

For each language:
- [ ] Research available Kokoro voices via API docs
- [ ] Test each voice with sample text in target language
- [ ] Rate voice quality: Excellent / Good / Fair / Poor
- [ ] Update `LANGUAGE_VOICES` mapping with best voices

### Phase 4: End-to-End (⬜ Not Started)

For each language:
- [ ] Test full voice chat flow: speak → transcribe → LLM → TTS
- [ ] Measure total latency
- [ ] Verify language consistency throughout pipeline
- [ ] Mark language as ✅ Production / ⚠️ Usable / ❌ Not Recommended

---

## Known Issues

| Issue | Impact | Workaround | Planned Fix |
|-------|--------|------------|-------------|
| MiMo responds in English | High | Retry with stronger prompt | Sprint 3.3 — Language enforcement |
| No native TTS voices | Medium | Use af_heart for all | Sprint 3.2 — Voice validation |
| Whisper accents vary | Low | Language hint in API call | Already implemented |
| Arabic RTL rendering | Low | Frontend CSS fix | Sprint 3.4 |

---

## Configuration

### Environment Variables

```bash
# Primary brain LLM (default: MiMo-V2-Flash)
BRAIN_LLM_MODEL="XiaomiMiMo/MiMo-V2-Flash"

# Fallback brain LLM for non-CN/EN languages (optional)
BRAIN_LLM_FALLBACK="deepseek-ai/DeepSeek-V3"

# STT model (default: Whisper Large V3)
CHUTES_STT_MODEL="openai/whisper-large-v3"

# TTS model (default: Kokoro)
CHUTES_TTS_MODEL="kokoro"
```

### Frontend Language Selector

Languages available in UI (`public/index.html`):
- English (en)
- Русский (ru)
- 中文 (zh)
- 日本語 (ja)
- 한국어 (ko)
- Español (es)
- Français (fr)
- Deutsch (de)
- العربية (ar)

User-selected language is passed to:
- STT API (`language` param)
- LLM system prompt ("Reply in same language")
- TTS API (`language` param for voice auto-selection)

---

## API Usage

### Voice Chat with Language

```bash
curl -X POST http://localhost:8088/api/voice-chat \
  -H "Content-Type: application/json" \
  -d '{
    "audio_base64": "<base64_audio>",
    "language": "ru",
    "session_id": "test-123",
    "hotel_id": "2ada3c2b-b208-4599-9c46-f32dc16ff950"
  }'
```

### TTS with Language Auto-Selection

```bash
curl -X POST http://localhost:8088/api/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Привет мир",
    "language": "ru"
  }'
```

System will:
1. Look up `language` in `LANGUAGE_VOICES` mapping
2. Select appropriate voice (e.g., `af_heart` for Russian)
3. Generate speech using selected voice

---

## Success Criteria

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Languages validated | 7/9 | 1/9 (EN only) | ⬜ In Progress |
| Native TTS voices | 5+ | 1 (EN) | ⬜ In Progress |
| STT accuracy (avg) | >85% | Unknown | ⬜ Testing needed |
| LLM language consistency | >95% | Unknown | ⬜ Testing needed |
| E2E latency (per lang) | <8s | ~6-8s (EN) | ✅ Meets target |

---

## Next Steps (Sprint 3)

1. **3.1 Language-to-Voice Mapping** ✅ COMPLETE
   - [x] Add `LANGUAGE_VOICES` dict
   - [x] Update `call_chutes_tts()` to accept `language` param
   - [x] Auto-select voice based on language
   - [x] Test with Russian text

2. **3.2 STT Validation** ⬜ TODO
   - [ ] Generate test audio for 9 languages
   - [ ] Test transcription accuracy
   - [ ] Document results

3. **3.3 LLM Language Enforcement** ⬜ TODO
   - [ ] Add language detection function
   - [ ] Retry with stronger prompt if mismatch
   - [ ] Test with non-English prompts

4. **3.4 Frontend Improvements** ⬜ TODO
   - [ ] Show detected language badge
   - [ ] Add auto-detect option
   - [ ] Persist language in localStorage

---

**Status:** Sprint 3 in progress — 3.1 complete, 3.2-3.4 pending
