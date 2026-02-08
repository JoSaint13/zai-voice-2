# Product Requirements Document (PRD)
# NomadAI Voice Agent

**Version:** 1.0
**Date:** 2026-02-08
**Status:** Draft

---

## 1. Executive Summary

**NomadAI Voice Agent** is the voice-first interface for the NomadAI hotel smart assistant platform. It enables guests to interact naturally using speech in 20+ languages, powered by Z.AI's GLM model stack. The voice agent serves as the foundation for a full-featured digital concierge and sightseeing expert system.

### Vision
> "Speak to your hotel like you'd speak to a local friend"

### Z.AI Model Stack
| Capability | Model | Purpose |
|------------|-------|---------|
| Speech Recognition | GLM-ASR-2512 | 20+ languages, dialect support |
| Conversation | GLM-4.7 | Intent handling, RAG, reasoning |
| Voice Synthesis | GLM-4-Voice | Natural speech output |
| Image Generation | CogView-4 | Destination previews |
| Video Generation | CogVideoX | Personalized tour videos |

---

## 2. Problem Statement

### Guest Pain Points
| Problem | Impact | Current Solution |
|---------|--------|------------------|
| Language barriers | Guests can't communicate needs | Staff scrambles, miscommunication |
| Wait times at reception | 12+ min average response | Frustration, negative reviews |
| Finding local gems | Tourists miss authentic experiences | Generic TripAdvisor lists |
| Information overload | Decision paralysis | Hours wasted researching |

### Hotel Pain Points
| Problem | Impact | Current Solution |
|---------|--------|------------------|
| Staff shortages | 30-35% labor costs | Overworked staff, poor service |
| Repetitive queries | Staff answers "WiFi password?" 50x/day | Manual, unscalable |
| Upsell opportunities missed | Lost revenue on spa, dining, tours | Passive brochures |
| OTA commission fees | 15-25% per booking | No alternative |

---

## 3. Goals & Success Metrics

### Primary Goals
| Goal | Metric | Target |
|------|--------|--------|
| Reduce front desk load | % of queries handled by AI | 70-90% |
| Faster response time | Avg response latency | < 2 seconds |
| Guest satisfaction | NPS score delta | +15 points |
| Revenue uplift | Ancillary spend per guest | +23% |

### Voice-Specific Goals
| Goal | Metric | Target |
|------|--------|--------|
| Speech recognition accuracy | Word Error Rate (WER) | < 5% |
| Language coverage | Supported languages | 20+ |
| Dialect support | Regional variants | Cantonese, regional accents |
| Low-volume speech | Whisper recognition rate | > 90% |

---

## 4. Target Users

### Primary: Hotel Guests
| Persona | Description | Key Needs |
|---------|-------------|-----------|
| **Business Traveler** | Frequent flyer, time-poor | Quick answers, efficiency |
| **Family Tourist** | Planning group activities | Recommendations, directions |
| **Digital Nomad** | Extended stays, local immersion | Hidden gems, local tips |
| **Elderly Guest** | Less tech-savvy | Voice-first, simple interaction |

### Secondary: Hotel Staff
| Persona | Description | Key Needs |
|---------|-------------|-----------|
| **Front Desk** | Overwhelmed with queries | Offload routine questions |
| **Concierge** | Expertise bottleneck | AI assistance for complex requests |
| **Management** | Revenue & efficiency focused | Analytics, upsell automation |

---

## 5. Voice Skills Specification

### 5.1 Core Voice Infrastructure

| Skill | Input | Output | Models |
|-------|-------|--------|--------|
| **Listen** | Guest speech (any language) | Transcribed text | GLM-ASR-2512 |
| **Understand** | Text + context | Intent + entities | GLM-4.7 |
| **Respond** | Response text | Natural speech | GLM-4-Voice |
| **Visualize** | Description | Image | CogView-4 |
| **Animate** | Scene description | Video clip | CogVideoX |

### 5.2 Hotel Concierge Skills

| Skill ID | Skill Name | Example Utterances | Backend Action |
|----------|------------|-------------------|----------------|
| `CON-001` | Room Service | "I'd like to order breakfast" | Menu lookup → PMS order |
| `CON-002` | Housekeeping | "Can I get extra towels?" | Create housekeeping ticket |
| `CON-003` | Amenities Info | "What time does the pool close?" | Knowledge base lookup |
| `CON-004` | WiFi Help | "What's the WiFi password?" | Return credentials |
| `CON-005` | Check-out | "I want to check out" | PMS checkout flow |
| `CON-006` | Complaints | "The AC isn't working" | Create ticket → escalate |
| `CON-007` | Wake-up Call | "Wake me at 7am" | Schedule alarm |
| `CON-008` | Billing | "Show me my bill" | PMS billing lookup |

### 5.3 Sightseeing Expert Skills

| Skill ID | Skill Name | Example Utterances | Backend Action |
|----------|------------|-------------------|----------------|
| `SEE-001` | Local Recommendations | "Where's good ramen nearby?" | RAG search + ranking |
| `SEE-002` | Itinerary Planning | "Plan my day, I have 4 hours" | Route optimization |
| `SEE-003` | Directions | "How do I get to Shibuya?" | OpenStreetMap routing |
| `SEE-004` | Events | "What's happening today?" | Events API lookup |
| `SEE-005` | Booking | "Book that temple tour" | Partner API (Viator) |
| `SEE-006` | Translation | "How do I say thank you?" | Translate + pronounce |
| `SEE-007` | Destination Preview | "Show me what Kyoto looks like" | CogView-4 generation |
| `SEE-008` | Video Tour | "Create a video of my walking route" | CogVideoX generation |

### 5.4 System Skills

| Skill ID | Skill Name | Example Utterances | Backend Action |
|----------|------------|-------------------|----------------|
| `SYS-001` | Language Switch | "Speak to me in Japanese" | Change TTS language |
| `SYS-002` | Human Handoff | "I need to speak to someone" | Alert staff + transfer |
| `SYS-003` | Repeat | "Can you repeat that?" | Replay last response |
| `SYS-004` | Slow Down | "Speak slower please" | Adjust TTS rate |
| `SYS-005` | Conversation Reset | "Start over" | Clear context |

---

## 6. Technical Architecture

### 6.1 Voice Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                        GUEST INTERFACE                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │   Web    │  │ WhatsApp │  │   SMS    │  │ In-Room  │        │
│  │   App    │  │   Bot    │  │  Gateway │  │  Device  │        │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘        │
└───────┼─────────────┼─────────────┼─────────────┼───────────────┘
        │             │             │             │
        └─────────────┴──────┬──────┴─────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      VOICE PROCESSING                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   GLM-ASR-2512                          │   │
│  │         Speech Recognition (20+ languages)              │   │
│  └─────────────────────────┬───────────────────────────────┘   │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   INTENT ROUTER                         │   │
│  │    Classify → Concierge | Sightseeing | Media | System  │   │
│  └───────┬─────────────┬─────────────┬─────────────┬───────┘   │
└──────────┼─────────────┼─────────────┼─────────────┼────────────┘
           │             │             │             │
           ▼             ▼             ▼             ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  CONCIERGE   │ │ SIGHTSEEING  │ │    MEDIA     │ │   SYSTEM     │
│    AGENT     │ │    AGENT     │ │    AGENT     │ │   AGENT      │
│  (GLM-4.7)   │ │ (GLM-4.7+RAG)│ │(CogView/Vid) │ │  (GLM-4.7)   │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │                │
       ▼                ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│     PMS      │ │  Knowledge   │ │    Media     │ │   Config     │
│ Integration  │ │  Base (RAG)  │ │   Storage    │ │   Store      │
│ Mews/Cloud   │ │ + Maps API   │ │   S3/CDN     │ │              │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
           │             │             │             │
           └─────────────┴──────┬──────┴─────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      VOICE OUTPUT                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   GLM-4-Voice                           │   │
│  │            Text-to-Speech (Natural voice)               │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 Z.AI API Endpoints

| Capability | Endpoint | Method |
|------------|----------|--------|
| Speech-to-Text | `POST /api/paas/v4/audio/transcriptions` | Multipart |
| Chat/Reasoning | `POST /api/paas/v4/chat/completions` | JSON |
| Text-to-Speech | `POST /api/paas/v4/audio/speech` | JSON |
| Image Generation | `POST /api/paas/v4/images/generations` | JSON |
| Video Generation | `POST /api/paas/v4/videos/generations` | JSON |

### 6.3 Data Flow Example

**Guest says:** "Where can I get good sushi nearby that's open now?"

```
1. [Audio Capture] → WebM audio blob
2. [GLM-ASR-2512] → "Where can I get good sushi nearby that's open now?"
3. [Intent Router] → category: "sightseeing", skill: "SEE-001"
4. [Sightseeing Agent]
   a. Extract entities: cuisine=sushi, distance=nearby, time=now
   b. Query RAG: local restaurant knowledge base
   c. Query OpenStreetMap: filter by distance, opening hours
   d. GLM-4.7: Rank and compose response
5. [Response] → "There are 3 great sushi places within 10 minutes walk..."
6. [GLM-4-Voice] → Audio response
7. [Playback] → Guest hears recommendation
```

---

## 7. Non-Functional Requirements

### 7.1 Performance
| Metric | Requirement |
|--------|-------------|
| End-to-end latency | < 3 seconds |
| ASR latency | < 500ms |
| LLM response | < 2 seconds |
| TTS generation | < 500ms |
| Concurrent users | 100 per hotel |

### 7.2 Reliability
| Metric | Requirement |
|--------|-------------|
| Uptime | 99.9% |
| Fallback | Human handoff within 30s |
| Offline mode | Basic FAQ cache |

### 7.3 Security & Privacy
| Requirement | Implementation |
|-------------|----------------|
| Data encryption | AES-256 at rest, TLS 1.3 in transit |
| GDPR/CCPA compliance | Consent management, data deletion |
| Audio retention | 24 hours max, then delete |
| PII handling | Anonymize in logs |

### 7.4 Localization
| Requirement | Implementation |
|-------------|----------------|
| Input languages | 20+ (GLM-ASR native support) |
| Output languages | 20+ (GLM-4-Voice) |
| Dialect support | Cantonese, regional variants |
| Cultural adaptation | Location-specific responses |

---

## 8. MVP Roadmap (4 Weeks)

### Week 1: Voice Foundation
| Task | Deliverable |
|------|-------------|
| GLM-ASR integration | Speech-to-text working |
| GLM-4.7 basic chat | Conversation working |
| Web UI | Hold-to-speak interface |
| Vercel deployment | Live demo URL |

### Week 2: Concierge Skills
| Task | Deliverable |
|------|-------------|
| Intent router | Skill classification |
| Hotel knowledge base | FAQ responses |
| Room service skill | Order flow |
| Housekeeping skill | Request flow |

### Week 3: Sightseeing Skills
| Task | Deliverable |
|------|-------------|
| RAG pipeline | Local recommendations |
| OpenStreetMap integration | Directions |
| Itinerary generation | Day planning |
| Partner API | Booking integration |

### Week 4: Media & Polish
| Task | Deliverable |
|------|-------------|
| CogView-4 integration | Destination images |
| CogVideoX integration | Tour video generation |
| Multi-language testing | 5 languages validated |
| Production hardening | Error handling, logging |

---

## 9. Success Criteria for MVP

| Criteria | Target | Validation |
|----------|--------|------------|
| Voice recognition accuracy | > 95% | Test with 100 utterances |
| Skill routing accuracy | > 90% | Test 50 intents |
| Response relevance | > 85% | Human evaluation |
| End-to-end latency | < 3s | Performance testing |
| Languages supported | 5+ | Functional testing |
| User satisfaction | > 4/5 stars | User feedback |

---

## 10. Future Roadmap

### Phase 2: PMS Integration (Month 2)
- Mews/Cloudbeds two-way sync
- Mobile check-in/check-out
- Digital room keys
- Automated billing

### Phase 3: Omnichannel (Month 3)
- WhatsApp Business API
- SMS gateway (Twilio)
- In-room tablet/speaker devices

### Phase 4: Revenue Optimization (Month 4)
- Upsell recommendations
- Partner commission tracking
- A/B testing framework
- Analytics dashboard

---

## 11. Appendix

### A. Competitive Analysis
| Competitor | Strengths | Weaknesses |
|------------|-----------|------------|
| Canary Technologies | PMS integration | No voice |
| Akia | SMS focus | Limited AI |
| Duve | Guest journey | No multilingual voice |
| **NomadAI** | Voice-first, 20+ languages, Z.AI stack | New entrant |

### B. Glossary
| Term | Definition |
|------|------------|
| ASR | Automatic Speech Recognition |
| RAG | Retrieval-Augmented Generation |
| PMS | Property Management System |
| TTS | Text-to-Speech |
| WER | Word Error Rate |

### C. References
- [GLM-ASR Documentation](https://docs.z.ai/guides/audio/glm-asr-2512)
- [GLM-4.7 API Reference](https://docs.z.ai/api/glm-4)
- [CogView-4 Image Generation](https://docs.z.ai/api/cogview)
- [CogVideoX Video Generation](https://docs.z.ai/api/cogvideo)

---

**Document Owner:** NomadAI Product Team
**Last Updated:** 2026-02-08
**Next Review:** 2026-02-15
