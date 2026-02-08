# NomadAI Team Composition

> Team structure, roles, and responsibilities

---

## Team Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      NomadAI Team                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│    ┌─────────────────────────────────────────────────────┐      │
│    │                  PRODUCT OWNER                       │      │
│    │              Strategic Direction                     │      │
│    └─────────────────────────┬───────────────────────────┘      │
│                              │                                   │
│         ┌────────────────────┼────────────────────┐             │
│         │                    │                    │             │
│         ▼                    ▼                    ▼             │
│    ┌─────────┐         ┌─────────┐         ┌─────────┐         │
│    │  BRAIN  │         │   DEV   │         │ RUNNER  │         │
│    │  Agent  │         │  Agent  │         │  Agent  │         │
│    │ (Opus)  │         │(Sonnet) │         │(Haiku)  │         │
│    └─────────┘         └─────────┘         └─────────┘         │
│         │                    │                    │             │
│    Architecture         Implementation        Testing           │
│    Design               Coding              Validation          │
│    Strategy             Features            Quality             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## AI Agent Team

### Brain Agent (Opus 4.5)

**Role:** Architect & Strategic Thinker

| Responsibility | Output |
|----------------|--------|
| System architecture design | `docs/ARCHITECTURE.md` |
| Skill system design | `src/skills/base.py` patterns |
| Intent routing strategy | Classification logic |
| Complex problem solving | Technical decisions |
| Documentation | PRD, guides, specs |

**Characteristics:**
- Deep reasoning capabilities
- Long-context understanding
- Strategic planning
- Complex code architecture

**Best Used For:**
- Designing new systems
- Solving hard problems
- Writing specifications
- Code review
- Architectural decisions

**Invocation:**
```
Brain Agent: Design the intent routing system that classifies
user utterances into skill categories (concierge, sightseeing,
media, system) with confidence scores.
```

---

### Dev Agent (Sonnet 4.5)

**Role:** Implementation Specialist

| Responsibility | Output |
|----------------|--------|
| Feature implementation | `src/skills/*.py` |
| API development | `api/index.py` |
| Integration work | External API connectors |
| Bug fixes | Code patches |
| Refactoring | Improved code |

**Characteristics:**
- Fast, efficient coding
- Good balance of speed/quality
- Strong at implementation
- Practical solutions

**Best Used For:**
- Writing new features
- Implementing designs
- Bug fixing
- API integrations
- Routine development

**Invocation:**
```
Dev Agent: Implement the RoomServiceSkill class that handles
menu lookup, order placement, and dietary restrictions based
on the BaseSkill interface.
```

---

### Runner Agent (Haiku 4.5)

**Role:** Quality & Validation

| Responsibility | Output |
|----------------|--------|
| Test creation | `tests/*.py` |
| Pipeline validation | `scripts/demo.py` |
| Quick checks | Status reports |
| Documentation updates | README updates |
| Routine tasks | File operations |

**Characteristics:**
- Very fast responses
- Efficient for simple tasks
- Good for validation
- Cost-effective

**Best Used For:**
- Writing tests
- Running validations
- Simple file operations
- Status checks
- Documentation updates

**Invocation:**
```
Runner Agent: Create pytest tests for the RoomServiceSkill
covering happy path, error cases, and edge cases.
```

---

## Team Collaboration Model

### Parallel Execution

```
┌─────────────────────────────────────────────────────────────────┐
│                    Task: Implement New Feature                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Brain ──────────────────────────────────────────► Design Doc  │
│      │                                                           │
│      │ (in parallel)                                            │
│      │                                                           │
│   Dev ────────────────────────────────────────────► Code        │
│      │                                                           │
│      │ (in parallel)                                            │
│      │                                                           │
│   Runner ─────────────────────────────────────────► Tests       │
│                                                                  │
│   ═══════════════════════════════════════════════════════════   │
│                          All complete                            │
│                              │                                   │
│                              ▼                                   │
│                        Commit & Push                             │
└─────────────────────────────────────────────────────────────────┘
```

### Sequential Handoff

```
┌─────────────────────────────────────────────────────────────────┐
│                    Task: Complex Feature                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Step 1: Brain designs architecture                            │
│           ↓                                                      │
│   Step 2: Dev implements based on design                        │
│           ↓                                                      │
│   Step 3: Runner validates implementation                       │
│           ↓                                                      │
│   Step 4: Brain reviews if needed                               │
│           ↓                                                      │
│   Done: Commit & Push                                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Task Assignment Matrix

| Task Type | Primary | Secondary | Reviewer |
|-----------|---------|-----------|----------|
| Architecture design | Brain | - | Brain |
| New feature | Dev | Brain | Runner |
| Bug fix | Dev | - | Runner |
| Test writing | Runner | Dev | Brain |
| Documentation | Brain | Runner | - |
| Integration | Dev | Brain | Runner |
| Performance tuning | Brain | Dev | Runner |
| Code review | Brain | - | - |
| Deployment | Runner | Dev | - |

---

## Communication Protocol

### Task Handoff Format

```markdown
## Task: [Name]

**Assigned to:** [Agent]
**Priority:** P0/P1/P2/P3
**Deadline:** [Date/Time]

### Context
[Background information, related files, dependencies]

### Requirements
1. [Specific requirement 1]
2. [Specific requirement 2]

### Deliverables
- [ ] [Expected output 1]
- [ ] [Expected output 2]

### Success Criteria
- [Measurable criteria]
```

### Status Update Format

```markdown
## Status: [Task Name]

**Agent:** [Name]
**Status:** In Progress / Complete / Blocked

### Completed
- [What was done]

### Next Steps
- [What's remaining]

### Blockers
- [Any issues]
```

---

## Scaling the Team

### Current: MVP Phase (3 Agents)

```
Brain (Opus)   → Architecture, Complex problems
Dev (Sonnet)   → Features, Integration
Runner (Haiku) → Tests, Validation
```

### Growth: Production Phase (5 Agents)

```
Brain (Opus)     → Architecture, Strategy
Dev-1 (Sonnet)   → Backend features
Dev-2 (Sonnet)   → Frontend features
Runner (Haiku)   → Tests, CI/CD
Ops (Haiku)      → Monitoring, Deployment
```

### Enterprise: Scale Phase (7+ Agents)

```
Brain (Opus)       → Architecture, Strategy
Dev-Backend        → API, Skills
Dev-Frontend       → UI, Mobile
Dev-Integration    → PMS, Partners
Runner             → Tests
Ops                → Infrastructure
Support            → Documentation, Triage
```

---

## Cost Optimization

### Model Selection by Task

| Task Complexity | Model | Cost | Speed |
|-----------------|-------|------|-------|
| Architecture | Opus | $$$ | Slow |
| Features | Sonnet | $$ | Medium |
| Tests/Docs | Haiku | $ | Fast |

### Guidelines

1. **Use Haiku** for:
   - Simple file operations
   - Test writing
   - Status checks
   - Documentation updates

2. **Use Sonnet** for:
   - Feature implementation
   - Bug fixes
   - Standard integrations

3. **Use Opus** for:
   - System design
   - Complex problems
   - Critical reviews
   - Strategic decisions

---

## Performance Metrics

### Agent Efficiency

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Task completion rate | >95% | Tasks done / assigned |
| First-time quality | >80% | No rework needed |
| Parallel efficiency | 3x speedup | Time vs sequential |
| Cost per feature | <$10 | API costs tracked |

### Team Velocity

| Sprint | Features | Tests | Docs |
|--------|----------|-------|------|
| Week 1-2 | 18 skills | 2 test files | 5 docs |
| Week 3-4 | TBD | TBD | TBD |

---

## Onboarding New Agents

### Context Needed

1. **Project Overview**
   - README.md
   - docs/PRD.md

2. **Technical Context**
   - docs/ARCHITECTURE.md
   - src/skills/base.py

3. **Current Status**
   - docs/ROADMAP.md
   - Recent commits

### Prompt Template

```
You are the [ROLE] agent for NomadAI Voice Agent.

Project: Hotel voice assistant using Z.AI (GLM-ASR, GLM-4.7)
Your role: [SPECIFIC RESPONSIBILITIES]

Key files:
- [FILE 1]: [PURPOSE]
- [FILE 2]: [PURPOSE]

Current sprint focus: [CURRENT GOALS]

Your task: [SPECIFIC TASK]
```

---

**Last Updated:** 2026-02-08
