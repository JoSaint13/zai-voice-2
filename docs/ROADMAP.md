# NomadAI Implementation Roadmap

> Phased implementation plan from MVP to full product

**Version:** 0.1.0 | **Current Phase:** Phase 1 Complete | **Last Updated:** 2026-02-08

---

## Current Status

```
Phase 1: Foundation     ████████████████████ 100% ✅ COMPLETE
Phase 2: Skills         ░░░░░░░░░░░░░░░░░░░░   0% ⏳ STARTING
Phase 3: PMS            ░░░░░░░░░░░░░░░░░░░░   0% 📋 PLANNED
Phase 4: Omnichannel    ░░░░░░░░░░░░░░░░░░░░   0% 📋 PLANNED
Phase 5: Revenue        ░░░░░░░░░░░░░░░░░░░░   0% 📋 PLANNED
```

---

## Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           NomadAI Roadmap                                    │
├─────────────┬─────────────┬─────────────┬─────────────┬─────────────────────┤
│   Week 1-2  │   Week 3-4  │   Month 2   │   Month 3   │      Month 4+       │
│  Foundation │   Skills    │     PMS     │ Omnichannel │      Revenue        │
├─────────────┼─────────────┼─────────────┼─────────────┼─────────────────────┤
│ ✅ Voice    │ ⏳ Intent   │ 📋 Mews    │ 📋 WhatsApp │ 📋 Upsell Engine   │
│ ✅ Web UI   │ ⏳ Concierge│ 📋 Cloudbeds│ 📋 SMS     │ 📋 Analytics       │
│ ✅ Deploy   │ ⏳ Sightsee │ 📋 Billing │ 📋 In-room │ 📋 A/B Testing     │
│ ✅ Skills   │ ⏳ Media    │ 📋 Keys    │ 📋 Tablet  │ 📋 Partnerships    │
└─────────────┴─────────────┴─────────────┴─────────────┴─────────────────────┘

Legend: ✅ Done  ⏳ In Progress  📋 Planned
```

---

## Phase 1: Foundation (Week 1-2) ✅ COMPLETE

### Objectives
- Establish voice pipeline with Chutes.ai models
- Deploy working prototype to Vercel
- Create skill system architecture

### Deliverables

| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| ASR integration | ⚠️ Pending | Dev | Speech-to-text not yet configured |
| Chutes.ai chat integration | ✅ Done | Dev | Conversation working |
| Web UI with voice recording | ✅ Done | Dev | Hold-to-speak interface |
| Vercel deployment | ✅ Done | Dev | Auto-deploy on push |
| Skill system architecture | ✅ Done | Brain | BaseSkill, Registry, Context |
| Concierge skill stubs | ✅ Done | Dev | 8 skills defined |
| Sightseeing skill stubs | ✅ Done | Dev | 8 skills defined |
| Media skill stubs | ⚠️ Pending | Dev | Image/video gen not available |
| Test framework | ✅ Done | Runner | pytest + demo script |
| Documentation | ✅ Done | Brain | PRD, Architecture, Guides |

### Metrics Achieved
- [x] Voice pipeline working end-to-end
- [x] <3s response latency
- [x] Deployed to production URL
- [x] 18 skills defined

---

## Phase 2: Skill Implementation (Week 3-4) ⏳ IN PROGRESS

### Objectives
- Implement intent routing with Chutes.ai (DeepSeek/Qwen)
- Build functional concierge and sightseeing skills
- Integrate media generation

### Sprint 1 (Week 3): Core Skills

| Task | Priority | Owner | Estimate |
|------|----------|-------|----------|
| Intent router with Chutes.ai model | P0 | Brain | 2 days |
| Wire skills to API endpoints | P0 | Dev | 1 day |
| Room service skill | P1 | Dev | 1 day |
| Housekeeping skill | P1 | Dev | 1 day |
| Amenities info skill | P1 | Dev | 0.5 day |
| WiFi/FAQ skill | P1 | Dev | 0.5 day |
| Integration tests | P1 | Runner | 1 day |

### Sprint 2 (Week 4): Advanced Skills

| Task | Priority | Owner | Estimate |
|------|----------|-------|----------|
| Local recommendations (RAG) | P1 | Dev | 2 days |
| Itinerary planning | P2 | Dev | 1 day |
| Directions (OpenStreetMap) | P2 | Dev | 1 day |
| Image generation (provider TBD) | P2 | Dev | 1 day |
| Video generation (provider TBD) | P3 | Dev | 1 day |
| Multi-language testing | P1 | Runner | 1 day |
| Production hardening | P1 | Dev | 1 day |

### Success Criteria
- [ ] Intent routing >90% accuracy
- [ ] 8 concierge skills functional
- [ ] 5 sightseeing skills functional
- [ ] Image generation working
- [ ] 5 languages validated

---

## Phase 3: PMS Integration (Month 2) 📋 PLANNED

### Objectives
- Two-way sync with hotel property management systems
- Enable real-time room status and guest profiles
- Automate billing and checkout

### Tasks

| Task | Priority | Owner | Estimate |
|------|----------|-------|----------|
| Mews API integration | P0 | Dev | 1 week |
| Cloudbeds API integration | P1 | Dev | 1 week |
| Guest profile retrieval | P0 | Dev | 2 days |
| Room status sync | P1 | Dev | 2 days |
| Mobile check-in/check-out | P1 | Dev | 3 days |
| Digital room keys | P2 | Dev | 3 days |
| Billing integration | P1 | Dev | 3 days |
| PMS webhook handlers | P1 | Dev | 2 days |

### Dependencies
- PMS sandbox accounts (Mews, Cloudbeds)
- OAuth credentials
- Webhook endpoints

### Success Criteria
- [ ] Guest lookup by room/name working
- [ ] Room status reflected in responses
- [ ] Charges posted to guest folio
- [ ] Check-in/out flow complete

---

## Phase 4: Omnichannel (Month 3) 📋 PLANNED

### Objectives
- Expand beyond web to messaging platforms
- Enable in-room device integration
- Unified inbox for hotel staff

### Tasks

| Task | Priority | Owner | Estimate |
|------|----------|-------|----------|
| WhatsApp Business API | P0 | Dev | 1 week |
| Twilio SMS gateway | P1 | Dev | 3 days |
| Message router | P0 | Brain | 3 days |
| In-room tablet app | P2 | Dev | 1 week |
| Voice speaker integration | P3 | Dev | 1 week |
| Staff dashboard | P1 | Dev | 1 week |
| Human handoff flow | P0 | Dev | 3 days |
| Channel analytics | P2 | Dev | 2 days |

### Dependencies
- WhatsApp Business API approval
- Twilio account
- Hardware partners (tablets, speakers)

### Success Criteria
- [ ] WhatsApp bot responding
- [ ] SMS fallback working
- [ ] Staff can see all conversations
- [ ] Human handoff <30s

---

## Phase 5: Revenue Optimization (Month 4+) 📋 PLANNED

### Objectives
- Drive ancillary revenue through AI recommendations
- Enable partner bookings with commission tracking
- Provide analytics for hotel management

### Tasks

| Task | Priority | Owner | Estimate |
|------|----------|-------|----------|
| Upsell recommendation engine | P0 | Brain | 1 week |
| Viator/GetYourGuide integration | P1 | Dev | 1 week |
| Restaurant reservation API | P2 | Dev | 3 days |
| Commission tracking | P1 | Dev | 3 days |
| A/B testing framework | P2 | Dev | 1 week |
| Analytics dashboard | P1 | Dev | 1 week |
| Revenue reports | P1 | Dev | 3 days |
| Conversion optimization | P2 | Brain | Ongoing |

### Dependencies
- Partner API agreements
- Payment processing (Stripe)
- BI tool selection

### Success Criteria
- [ ] Upsell conversion >15%
- [ ] Partner bookings tracked
- [ ] Revenue dashboard live
- [ ] A/B tests running

---

## Technical Debt & Improvements

### Short-term (Ongoing)

| Item | Priority | Effort |
|------|----------|--------|
| Add response caching | Medium | 2 days |
| Improve error handling | High | 1 day |
| Add request logging | High | 1 day |
| Rate limiting | Medium | 1 day |

### Medium-term (Month 2-3)

| Item | Priority | Effort |
|------|----------|--------|
| WebSocket for real-time | Medium | 1 week |
| Redis for session state | Medium | 3 days |
| CDN for audio/media | Low | 2 days |
| Database for knowledge base | High | 1 week |

### Long-term (Month 4+)

| Item | Priority | Effort |
|------|----------|--------|
| Kubernetes migration | Low | 2 weeks |
| Multi-region deployment | Low | 1 week |
| Custom voice training | Low | 1 month |
| On-premise option | Low | 1 month |

---

## Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Chutes.ai API outage | Low | High | Fallback responses, retry logic |
| PMS integration delays | Medium | Medium | Start early, have backup PMS |
| WhatsApp approval denied | Medium | Medium | Focus on SMS first |
| Low pilot hotel adoption | Medium | High | Offer free trial, hands-on support |
| Competitor launches | Medium | Medium | Focus on dialect/voice differentiation |

---

## Milestones

| Milestone | Target Date | Criteria |
|-----------|-------------|----------|
| MVP Launch | Week 4 | Voice assistant live with 10 skills |
| First Pilot Hotel | Month 2 | One hotel actively using system |
| PMS Live | Month 2 | Mews or Cloudbeds integrated |
| Omnichannel | Month 3 | WhatsApp + SMS working |
| Revenue Launch | Month 4 | Partner bookings generating commission |
| 10 Hotels | Month 6 | 10 paying hotel customers |

---

## Next Actions

### This Week
1. [ ] Implement intent router
2. [ ] Wire concierge skills to API
3. [ ] Test room service flow end-to-end
4. [ ] Validate 3 languages (EN, ZH, ES)

### Next Week
1. [ ] Complete sightseeing skills
2. [ ] Integrate CogView-4 for images
3. [ ] Load test with 50 concurrent users
4. [ ] Prepare pilot hotel demo

---

**Last Updated:** 2026-02-08
**Next Review:** 2026-02-15
