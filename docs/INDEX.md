# NomadAI Documentation Index

> **NomadAI** - Voice-first hotel smart assistant powered by Chutes.ai

**Version:** 0.2.0 | **Status:** Alpha | **Last Updated:** 2026-02-11

---

## Start Here

| New to NomadAI? | Document |
|-----------------|----------|
| **Using Claude Code?** | [CLAUDE.md](../CLAUDE.md) - AI assistant context |
| **Business stakeholder?** | [BUSINESS.md](readers/BUSINESS.md) - Executive summary |
| **Developer?** | [DEVELOPER.md](readers/DEVELOPER.md) - Technical guide |
| **DevOps/SRE?** | [OPERATIONS.md](readers/OPERATIONS.md) - Deployment guide |

---

## Quick Links

| Document | Audience | Description |
|----------|----------|-------------|
| [README.md](../README.md) | Everyone | Project overview, quick start |
| [PRD.md](PRD.md) | Product/Business | Product requirements, goals, metrics |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Engineers | System design, components |
| [ROADMAP.md](ROADMAP.md) | All teams | Implementation phases, timeline |
| [TEAM.md](TEAM.md) | Management | Team structure, responsibilities |
| [BRAIN_AGENT_SKILLS.md](BRAIN_AGENT_SKILLS.md) | Developers | 12 LLM tools/functions reference |
| [KNOWLEDGE_ACCESS_STRATEGY.md](KNOWLEDGE_ACCESS_STRATEGY.md) | Developers | Meta-query handling strategy |

---

## Audience-Specific Guides

### For Business Stakeholders
- [PRD.md](PRD.md) - Full product requirements
- [ROADMAP.md](ROADMAP.md) - Timeline and milestones
- [docs/readers/BUSINESS.md](readers/BUSINESS.md) - Business summary

### For Developers
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical design
- [docs/readers/DEVELOPER.md](readers/DEVELOPER.md) - Developer guide
- [BRAIN_AGENT_SKILLS.md](BRAIN_AGENT_SKILLS.md) - Agent skills reference
- [KNOWLEDGE_ACCESS_STRATEGY.md](KNOWLEDGE_ACCESS_STRATEGY.md) - KB access patterns

### For Operations
- [docs/readers/OPERATIONS.md](readers/OPERATIONS.md) - Deployment & monitoring

---

## Project Structure

```
zai-voice-2/
├── api/                    # Flask API server
│   ├── index.py            # Main API (~1370 lines, agent loop)
│   └── requirements.txt    # Vercel Python dependencies
├── public/                 # Web frontend
│   └── index.html          # Voice UI (~1200 lines, mobile-first)
├── src/                    # Core source code
│   └── skills/             # Skill implementations
│       ├── base.py         # BaseSkill, Registry
│       ├── chat_provider.py# Shared chat function
│       ├── concierge.py    # Hotel services
│       ├── sightseeing.py  # Local recommendations
│       └── media.py        # Image/video generation
├── tests/                  # Test suite
│   ├── test_api.py
│   └── test_skills.py
├── scripts/                # Utility scripts
│   └── demo.py             # Pipeline demo
├── docs/                   # Documentation
│   ├── INDEX.md            # This file
│   ├── PRD.md              # Product requirements
│   ├── ARCHITECTURE.md     # System design
│   ├── ROADMAP.md          # Implementation plan
│   ├── TEAM.md             # Team structure
│   └── readers/            # Audience guides
│       ├── BUSINESS.md
│       ├── DEVELOPER.md
│       └── OPERATIONS.md
├── CHANGELOG.md            # Version history
├── Makefile                # Build/dev commands
└── README.md               # Project entry point
```

---

## Key Technologies

| Component | Technology | Documentation |
|-----------|------------|---------------|
| 🧠 Brain LLM | Chutes.ai (MiMo-V2-Flash) | Reasoning, tool-calling agent loop |
| 🎧 Speech-to-Text | Chutes.ai (Whisper Large V3) | Voice transcription |
| 🔊 Text-to-Speech | Chutes.ai (Kokoro) | Voice synthesis (raw WAV) |
| Translation | Brain LLM | Built-in translation via chat models |
| Backend | Flask/Python | [Flask Docs](https://flask.palletsprojects.com/) |
| Deployment | Vercel | [Vercel Docs](https://vercel.com/docs) |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.2.0 | 2026-02-11 | Agentic architecture, STT/TTS, tool-calling, wake word, TTS streaming |
| 0.1.0 | 2026-02-08 | Initial voice pipeline, skill system |

---

**Maintained by:** NomadAI Team
