# Hotel Smart Assistant - Technical Architecture Plan

## Business Goal
Transform generic "z.ai" voice assistant into a B2B SaaS "White-label AI Concierge" for hotels.

## Current State (MVP v0.1)
- **Frontend:** Single HTML file, hardcoded to "Grand Budapest Hotel".
- **Backend:** Flask app calling Z.AI (GLM-4.7) with RAG from SQLite.
- **Data:** SQLite database w/ `hotels` and `recommendations`.
- **Gaps:** No true multi-tenancy, no structured upsell actions, no admin API.

## Architecture Roadmap (CTO Perspective)

### Phase 1: Robust Multi-Tenancy (Immediate)
- **Problem:** `public/index.html` has a hardcoded `HOTEL_ID`.
- **Solution:** 
    - Frontend: Accept `hotel_id` via URL parameter (e.g., `?hotel_id=...`) so the same widget works for any hotel.
    - Backend: Validates the ID and loads the specific branding (Name, Primary Color) dynamically from DB.

### Phase 2: Action Engine (Upsells)
- **Problem:** Chatbot conversations are passive. It can answer "Check out is at 12", but can't *book* late checkout.
- **Solution:** Implement **Tool Calling** (Function Calling) in the LLM pipeline.
    - Detect intents: `request_late_checkout`, `book_spa`, `report_issue`.
    - Execute: Log request to DB -> Send webhook/email to Hotel Staff.

### Phase 3: Admin & Analytics (Foundational)
- **Problem:** No way for hotels to update their data without SQL access.
- **Solution:** Simple REST API endpoints for key management (Update Knowledge Base, Add Recommendation).

## Execution Plan (Completed)
1. [x] **Refactor Frontend**: `public/hotel.html` now reads `?id=` and fetches branding.
2. [x] **Refactor Backend**: Added `/api/hotel/<hotel_id>` endpoint and updated `/api/chat` to use context.
3. [x] **Implement Action Tools**: Added `request_late_checkout` tool definition and handling in `api/index.py`.

## Critical Next Steps (Production)
- **Database Migration**: SQLite will reset on every deployment in serverless environments (like Vercel). **Must migrate to PostgreSQL (Neon/Supabase)** for production.
- **Security**: Add authentication for the `/api/hotel` endpoints to prevent scraping.
- **Admin UI**: Build a restricted page to edit the Knowledge Base.
