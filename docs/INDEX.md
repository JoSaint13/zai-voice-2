# NomadAI Documentation Index

> **NomadAI** - Voice-first hotel smart assistant powered by Z.AI

## Quick Links

| Document | Audience | Description |
|----------|----------|-------------|
| [README.md](../README.md) | Everyone | Project overview, quick start |
| [PRD.md](PRD.md) | Product/Business | Product requirements, goals, metrics |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Engineers | System design, components |
| [ROADMAP.md](ROADMAP.md) | All teams | Implementation phases, timeline |
| [TEAM.md](TEAM.md) | Management | Team structure, responsibilities |

---

## Audience-Specific Guides

### For Business Stakeholders
- [PRD.md](PRD.md) - Full product requirements
- [ROADMAP.md](ROADMAP.md) - Timeline and milestones
- [docs/readers/BUSINESS.md](readers/BUSINESS.md) - Business summary

### For Developers
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical design
- [docs/readers/DEVELOPER.md](readers/DEVELOPER.md) - Developer guide
- [TESTING.md](../TESTING.md) - Testing guide

### For Operations
- [docs/readers/OPERATIONS.md](readers/OPERATIONS.md) - Deployment & monitoring

---

## Project Structure

```
zai-voice-2/
├── api/                    # Flask API server
│   └── index.py            # Main API endpoints
├── public/                 # Web frontend
│   └── index.html          # Voice UI
├── src/                    # Core source code
│   └── skills/             # Skill implementations
│       ├── base.py         # BaseSkill, Registry
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
└── README.md               # Project entry point
```

---

## Key Technologies

| Component | Technology | Documentation |
|-----------|------------|---------------|
| Speech Recognition | GLM-ASR-2512 | [Z.AI Docs](https://docs.z.ai/guides/audio/glm-asr-2512) |
| Conversation | GLM-4.7 | [Z.AI API](https://docs.z.ai/api/glm-4) |
| Image Generation | CogView-4 | [Z.AI CogView](https://docs.z.ai/api/cogview) |
| Video Generation | CogVideoX | [Z.AI CogVideo](https://docs.z.ai/api/cogvideo) |
| Backend | Flask/Python | [Flask Docs](https://flask.palletsprojects.com/) |
| Deployment | Vercel | [Vercel Docs](https://vercel.com/docs) |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2026-02-08 | Initial voice pipeline, skill system |

---

**Maintained by:** NomadAI Team
