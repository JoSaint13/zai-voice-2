# Recommended Coding Agent Skills for NomadAI

> Curated skills from [skills.sh](https://skills.sh) relevant to this project.
> Install: `npx skills add <owner/repo@skill>`

---

## ⭐ Tier 1 — Install Now (Core to Project)

These directly match our tech stack and current sprint work.

| # | Skill | Why It Matters | Install |
|---|-------|----------------|---------|
| 1 | **yonatangross/orchestkit@resilience-patterns** | Retry, circuit breaker, backoff — exactly what Sprint 1 implemented | `npx skills add yonatangross/orchestkit@resilience-patterns` |
| 2 | **yonatangross/orchestkit@streaming-api-patterns** | SSE/streaming patterns — our TTS streaming pipeline | `npx skills add yonatangross/orchestkit@streaming-api-patterns` |
| 3 | **bobmatnyc/claude-mpm-skills@vercel-functions-runtime** | Vercel serverless constraints, cold starts, timeouts | `npx skills add bobmatnyc/claude-mpm-skills@vercel-functions-runtime` |
| 4 | **jezweb/claude-skills@flask** | Flask best practices — our API framework | `npx skills add jezweb/claude-skills@flask` |
| 5 | **bobmatnyc/claude-mpm-skills@pytest** | pytest patterns — our test framework | `npx skills add bobmatnyc/claude-mpm-skills@pytest` |
| 6 | **aj-geddes/useful-ai-prompts@api-rate-limiting** | Rate limiting patterns — Sprint 1.3 hardening | `npx skills add aj-geddes/useful-ai-prompts@api-rate-limiting` |

### Quick install (Tier 1):
```bash
npx skills add yonatangross/orchestkit@resilience-patterns
npx skills add yonatangross/orchestkit@streaming-api-patterns
npx skills add bobmatnyc/claude-mpm-skills@vercel-functions-runtime
npx skills add jezweb/claude-skills@flask
npx skills add bobmatnyc/claude-mpm-skills@pytest
npx skills add aj-geddes/useful-ai-prompts@api-rate-limiting
```

---

## ⭐ Tier 2 — Install for Current Sprint

Skills matched to Phase 3 sprint work.

### Sprint 3: Multi-Language & i18n
| # | Skill | Why It Matters | Install |
|---|-------|----------------|---------|
| 7 | **aj-geddes/useful-ai-prompts@internationalization-i18n** | i18n patterns for 9-language support | `npx skills add aj-geddes/useful-ai-prompts@internationalization-i18n` |
| 8 | **vudovn/antigravity-kit@i18n-localization** | Localization implementation | `npx skills add vudovn/antigravity-kit@i18n-localization` |

### Sprint 4: Performance & Caching
| # | Skill | Why It Matters | Install |
|---|-------|----------------|---------|
| 9 | **yonatangross/orchestkit@caching-strategies** | LLM response caching, KB caching | `npx skills add yonatangross/orchestkit@caching-strategies` |
| 10 | **andrelandgraf/fullstackrecipes@observability-monitoring** | Logging, metrics, tracing patterns | `npx skills add andrelandgraf/fullstackrecipes@observability-monitoring` |

### Knowledge Base & RAG
| # | Skill | Why It Matters | Install |
|---|-------|----------------|---------|
| 11 | **jeffallan/claude-skills@rag-architect** | RAG architecture for hotel KB queries | `npx skills add jeffallan/claude-skills@rag-architect` |
| 12 | **giuseppe-trisciuoglio/developer-kit@rag-implementation** | Practical RAG implementation | `npx skills add giuseppe-trisciuoglio/developer-kit@rag-implementation` |

---

## ⭐ Tier 3 — Domain & Quality

Useful for improving quality and domain expertise.

### Voice & AI Agent
| # | Skill | Why It Matters | Install |
|---|-------|----------------|---------|
| 13 | **qodex-ai/ai-agent-skills@voice-ai-integration** | Voice AI integration patterns | `npx skills add qodex-ai/ai-agent-skills@voice-ai-integration` |
| 14 | **scientiacapital/skills@voice-ai** | Voice AI architecture | `npx skills add scientiacapital/skills@voice-ai` |
| 15 | **emzod/speak@speak-tts** | TTS implementation patterns | `npx skills add emzod/speak@speak-tts` |
| 16 | **jezweb/claude-skills@openai-api** | OpenAI-compatible API patterns (Chutes uses this) | `npx skills add jezweb/claude-skills@openai-api` |
| 17 | **melodic-software/claude-code-plugins@system-prompt-engineering** | System prompt design for agent loop | `npx skills add melodic-software/claude-code-plugins@system-prompt-engineering` |

### Hotel & Hospitality
| # | Skill | Why It Matters | Install |
|---|-------|----------------|---------|
| 18 | **skillhq/concierge@concierge** | Hotel concierge patterns | `npx skills add skillhq/concierge@concierge` |
| 19 | **personamanagmentlayer/pcl@hospitality-expert** | Hospitality domain knowledge | `npx skills add personamanagmentlayer/pcl@hospitality-expert` |

### Code Quality & Security
| # | Skill | Why It Matters | Install |
|---|-------|----------------|---------|
| 20 | **wshobson/agents@error-handling-patterns** | Error handling patterns for agents | `npx skills add wshobson/agents@error-handling-patterns` |
| 21 | **mrgoonie/claudekit-skills@code-review** | Code review patterns | `npx skills add mrgoonie/claudekit-skills@code-review` |
| 22 | **aj-geddes/useful-ai-prompts@api-security-hardening** | API security hardening | `npx skills add aj-geddes/useful-ai-prompts@api-security-hardening` |
| 23 | **fvadicamo/dev-agent-skills@git-commit** | Git commit conventions | `npx skills add fvadicamo/dev-agent-skills@git-commit` |
| 24 | **aj-geddes/useful-ai-prompts@responsive-web-design** | Mobile-first UI (Galaxy S21 FE target) | `npx skills add aj-geddes/useful-ai-prompts@responsive-web-design` |

### Async & Backend
| # | Skill | Why It Matters | Install |
|---|-------|----------------|---------|
| 25 | **bobmatnyc/claude-mpm-skills@asyncio** | Python asyncio patterns (skill execution) | `npx skills add bobmatnyc/claude-mpm-skills@asyncio` |
| 26 | **jeffallan/claude-skills@websocket-engineer** | WebSocket for future real-time voice | `npx skills add jeffallan/claude-skills@websocket-engineer` |

### Documentation
| # | Skill | Why It Matters | Install |
|---|-------|----------------|---------|
| 27 | **onewave-ai/claude-skills@technical-writer** | Technical documentation quality | `npx skills add onewave-ai/claude-skills@technical-writer` |

---

## 🚀 Recommended Install Order

### Phase 1 — Right now (6 skills)
Core stack skills that help with every task:
```bash
npx skills add yonatangross/orchestkit@resilience-patterns
npx skills add yonatangross/orchestkit@streaming-api-patterns
npx skills add bobmatnyc/claude-mpm-skills@vercel-functions-runtime
npx skills add jezweb/claude-skills@flask
npx skills add bobmatnyc/claude-mpm-skills@pytest
npx skills add aj-geddes/useful-ai-prompts@api-rate-limiting
```

### Phase 2 — Before Sprint 3 (4 skills)
Multi-language and knowledge base work:
```bash
npx skills add aj-geddes/useful-ai-prompts@internationalization-i18n
npx skills add vudovn/antigravity-kit@i18n-localization
npx skills add jeffallan/claude-skills@rag-architect
npx skills add melodic-software/claude-code-plugins@system-prompt-engineering
```

### Phase 3 — Before Sprint 4 (3 skills)
Performance and observability:
```bash
npx skills add yonatangross/orchestkit@caching-strategies
npx skills add andrelandgraf/fullstackrecipes@observability-monitoring
npx skills add bobmatnyc/claude-mpm-skills@asyncio
```

### Phase 4 — As needed (14 skills)
Domain and quality skills — install when working on specific areas.

---

## 📊 Summary

| Tier | Count | Focus |
|------|-------|-------|
| ⭐ Tier 1 — Install Now | 6 | Core stack: Flask, Vercel, pytest, resilience, streaming, rate limiting |
| ⭐ Tier 2 — Current Sprint | 6 | i18n, caching, observability, RAG |
| ⭐ Tier 3 — Domain & Quality | 15 | Voice AI, hospitality, security, code quality, docs |
| **Total** | **27** | |

---

**Searches performed**: voice AI, hotel concierge, Flask API, speech TTS, multilingual i18n, RAG knowledge base, Vercel serverless, error handling resilience, observability monitoring, caching performance, AI agent tool calling, prompt engineering, git commit conventions, HTML CSS mobile, JSON schema, OpenAI function calling, session state, documentation markdown, API rate limiting security

**Last Updated**: 2026-02-11
