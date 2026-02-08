# NomadAI Voice Agent - Architecture Design

**Version:** 1.0
**Date:** 2026-02-08
**Status:** Approved

---

## 1. System Overview

NomadAI Voice Agent is a voice-first digital concierge system built on Z.AI's GLM model stack. This document describes the architecture for intent routing, skill management, agent communication, state management, and error handling.

### Core Design Principles

1. **Extensibility**: New skills can be added without modifying core routing logic
2. **Separation of Concerns**: Each agent handles a specific domain
3. **Graceful Degradation**: System remains functional when individual components fail
4. **Stateless Processing**: Request handlers are stateless; state is externalized
5. **Observable**: All operations are logged and traceable

---

## 2. Intent Router Design

The Intent Router is the central dispatcher that classifies user intents and routes requests to the appropriate skill handler.

### 2.1 Intent Categories

| Category | Description | Agent | Examples |
|----------|-------------|-------|----------|
| `concierge` | Hotel service requests | ConciergeAgent | Room service, housekeeping, WiFi |
| `sightseeing` | Local exploration | SightseeingAgent | Recommendations, directions, booking |
| `media` | Content generation | MediaAgent | Images, videos of destinations |
| `system` | Agent control | SystemAgent | Language switch, repeat, handoff |

### 2.2 Classification Architecture

```
                    +------------------+
                    |   User Input     |
                    | (transcribed)    |
                    +--------+---------+
                             |
                             v
                    +------------------+
                    |  Intent Router   |
                    |   (GLM-4.7)      |
                    +--------+---------+
                             |
              +--------------+--------------+
              |              |              |
              v              v              v
    +------------------+  +------------------+  +------------------+
    | Primary Intent   |  | Confidence Score |  | Extracted        |
    | (category)       |  | (0.0 - 1.0)      |  | Entities         |
    +------------------+  +------------------+  +------------------+
```

### 2.3 Classification Prompt Template

The router uses a structured prompt to classify intents:

```
You are an intent classifier for a hotel voice assistant.

Given the user utterance, classify into exactly one category:
- concierge: Hotel services (room service, housekeeping, amenities, WiFi, checkout, complaints)
- sightseeing: Local exploration (recommendations, directions, booking tours, events)
- media: Visual content requests (show me, create image/video of destinations)
- system: Agent control (language change, repeat, speak slower, human handoff)

Also extract relevant entities and assign a confidence score.

User: "{utterance}"
Context: {context}

Respond in JSON format:
{
  "category": "<category>",
  "skill_hint": "<skill_id or null>",
  "confidence": <0.0-1.0>,
  "entities": {...},
  "reasoning": "<brief explanation>"
}
```

### 2.4 Routing Decision Flow

```
1. Receive transcribed text + conversation context
2. Call GLM-4.7 with classification prompt
3. Parse JSON response
4. If confidence < 0.6:
   - Ask clarifying question
5. If confidence >= 0.6:
   - Route to category agent
6. Agent executes skill and returns response
7. Response sent to TTS for voice output
```

### 2.5 Skill ID Hints

The router can provide a hint for the specific skill within a category:

| Category | Skill Hints |
|----------|-------------|
| concierge | `CON-001` to `CON-008` |
| sightseeing | `SEE-001` to `SEE-008` |
| system | `SYS-001` to `SYS-005` |
| media | `MED-001` (image), `MED-002` (video) |

---

## 3. Skill Registry Pattern

The Skill Registry provides a plugin-based architecture for skill management.

### 3.1 Registry Architecture

```
+------------------------------------------------------------------+
|                         SkillRegistry                             |
|  +------------------------------------------------------------+  |
|  |                    Registered Skills                        |  |
|  |  +------------+  +------------+  +------------+             |  |
|  |  | CON-001    |  | SEE-001    |  | SYS-001    |   ...       |  |
|  |  | RoomSvc    |  | LocalRec   |  | LangSwitch |             |  |
|  |  +------------+  +------------+  +------------+             |  |
|  +------------------------------------------------------------+  |
|                                                                   |
|  Methods:                                                         |
|  - register(skill: BaseSkill) -> None                            |
|  - get(skill_id: str) -> BaseSkill                               |
|  - list_by_category(category: str) -> List[BaseSkill]            |
|  - match(utterance: str, category: str) -> Optional[BaseSkill]   |
+------------------------------------------------------------------+
```

### 3.2 Skill Metadata Structure

Each skill defines metadata for discovery and routing:

```python
@dataclass
class SkillMetadata:
    skill_id: str          # Unique identifier (e.g., "CON-001")
    name: str              # Human-readable name
    category: str          # concierge | sightseeing | media | system
    description: str       # What the skill does
    example_utterances: List[str]  # Training examples
    required_entities: List[str]   # Entities needed to execute
    optional_entities: List[str]   # Entities that enhance execution
    version: str           # Semantic version
```

### 3.3 Registration Pattern

Skills are registered at application startup:

```python
# Auto-discovery pattern
from skills import concierge, sightseeing, media, system

registry = SkillRegistry()

# Register all skills from modules
for module in [concierge, sightseeing, media, system]:
    for skill_class in module.SKILLS:
        registry.register(skill_class())
```

### 3.4 Skill Invocation Flow

```
1. Router identifies category + skill_hint
2. Registry.get(skill_id) returns skill instance
3. Skill.validate(context) checks prerequisites
4. Skill.execute(context) performs action
5. Skill returns SkillResponse
6. Response formatted for TTS output
```

---

## 4. Agent Communication Flow

### 4.1 Request-Response Pipeline

```
+--------+    +-------+    +--------+    +-------+    +--------+
| Client | -> | ASR   | -> | Router | -> | Agent | -> | TTS    |
| (Web/  |    | GLM-  |    | Intent |    | Skill |    | GLM-4  |
| App)   |    | ASR   |    | Class. |    | Exec  |    | Voice  |
+--------+    +-------+    +--------+    +-------+    +--------+
    ^                                                      |
    |                                                      |
    +------------------------------------------------------+
                        Audio Response
```

### 4.2 Context Object

All components share a unified context object:

```python
@dataclass
class ConversationContext:
    session_id: str
    guest_id: Optional[str]
    room_number: Optional[str]
    language: str
    conversation_history: List[Message]
    current_intent: Optional[ClassifiedIntent]
    active_skill: Optional[str]
    entities: Dict[str, Any]
    preferences: Dict[str, Any]
    timestamp: datetime
```

### 4.3 Message Types

```python
class MessageType(Enum):
    USER_AUDIO = "user_audio"
    USER_TEXT = "user_text"
    TRANSCRIPTION = "transcription"
    INTENT = "intent"
    SKILL_REQUEST = "skill_request"
    SKILL_RESPONSE = "skill_response"
    AGENT_RESPONSE = "agent_response"
    TTS_AUDIO = "tts_audio"
    ERROR = "error"
```

### 4.4 Inter-Agent Communication

Agents can delegate to other agents:

```
Guest: "I want to book that ramen place you mentioned"

1. SightseeingAgent receives request
2. Identifies need for booking (SEE-005)
3. SEE-005 requires confirmation
4. Delegates to SystemAgent for confirmation flow
5. On confirm, SEE-005 calls booking API
6. Returns result to guest
```

---

## 5. State Management Approach

### 5.1 State Layers

```
+-------------------------------------------------------------------+
|                      State Architecture                            |
+-------------------------------------------------------------------+
|                                                                    |
|  +------------------+  +------------------+  +------------------+  |
|  | Session State    |  | Conversation     |  | Persistent       |  |
|  | (Redis/Memory)   |  | State (Context)  |  | State (DB)       |  |
|  +------------------+  +------------------+  +------------------+  |
|  | - Active skill   |  | - Message history|  | - Guest profile  |  |
|  | - Pending action |  | - Entities       |  | - Preferences    |  |
|  | - Temp data      |  | - Current intent |  | - Past requests  |  |
|  | TTL: 30 minutes  |  | TTL: 1 hour      |  | TTL: Permanent   |  |
|  +------------------+  +------------------+  +------------------+  |
|                                                                    |
+-------------------------------------------------------------------+
```

### 5.2 State Store Interface

```python
class StateStore(Protocol):
    async def get(self, key: str) -> Optional[Any]: ...
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None: ...
    async def delete(self, key: str) -> None: ...
    async def exists(self, key: str) -> bool: ...
```

### 5.3 Context Persistence

```python
class ContextManager:
    def __init__(self, store: StateStore):
        self.store = store

    async def get_context(self, session_id: str) -> ConversationContext:
        """Retrieve or create conversation context."""
        ...

    async def save_context(self, context: ConversationContext) -> None:
        """Persist context to store."""
        ...

    async def clear_context(self, session_id: str) -> None:
        """Clear context (for reset skill)."""
        ...
```

### 5.4 Slot Filling State Machine

For multi-turn skills that require gathering information:

```
States: IDLE -> GATHERING -> CONFIRMING -> EXECUTING -> COMPLETE

Example (Room Service):
1. IDLE: Guest says "I want breakfast"
2. GATHERING: "What would you like? We have eggs, pancakes..."
3. GATHERING: "Eggs please" -> entities["item"] = "eggs"
4. GATHERING: "How would you like them?" (missing: preparation)
5. GATHERING: "Scrambled" -> entities["preparation"] = "scrambled"
6. CONFIRMING: "Scrambled eggs for room 302. Confirm?"
7. EXECUTING: "Yes" -> Create order in PMS
8. COMPLETE: "Your breakfast will arrive in 20 minutes"
```

---

## 6. Error Handling Strategy

### 6.1 Error Categories

| Category | Examples | Response Strategy |
|----------|----------|-------------------|
| `recognition_error` | ASR failure, unclear audio | "I didn't catch that, could you repeat?" |
| `intent_unclear` | Low confidence classification | "Did you mean X or Y?" |
| `skill_error` | Skill execution failure | "Sorry, I couldn't complete that. Let me try again." |
| `backend_error` | API/service unavailable | "I'm having trouble connecting. Please try again." |
| `validation_error` | Missing required entities | "I need to know X to help you with that." |
| `permission_error` | Unauthorized action | "I'll need to connect you with staff for that." |

### 6.2 Error Response Structure

```python
@dataclass
class ErrorResponse:
    error_code: str
    category: str
    message: str  # User-friendly message
    technical_details: Optional[str]  # For logging
    recovery_action: Optional[str]  # Suggested next step
    escalate: bool  # Should we involve human?
```

### 6.3 Retry Strategy

```python
class RetryConfig:
    max_attempts: int = 3
    backoff_base: float = 1.0  # seconds
    backoff_multiplier: float = 2.0
    retriable_errors: List[str] = ["backend_error", "timeout"]

async def with_retry(func, config: RetryConfig):
    for attempt in range(config.max_attempts):
        try:
            return await func()
        except RetriableError as e:
            if attempt == config.max_attempts - 1:
                raise
            wait = config.backoff_base * (config.backoff_multiplier ** attempt)
            await asyncio.sleep(wait)
```

### 6.4 Graceful Degradation

```
Level 1: Primary Service Unavailable
  -> Use cached responses for common queries

Level 2: GLM-4.7 Unavailable
  -> Fallback to pattern matching for basic intents
  -> Escalate complex queries to human

Level 3: Complete Outage
  -> Return static "experiencing difficulties" message
  -> Provide direct phone number to front desk
```

### 6.5 Human Handoff Protocol

```python
class HandoffTrigger(Enum):
    EXPLICIT_REQUEST = "guest requested human"
    REPEATED_FAILURES = "3+ failed attempts"
    SENSITIVE_TOPIC = "complaint or safety issue"
    LOW_CONFIDENCE = "persistent low confidence"
    TIMEOUT = "no response in 30 seconds"

async def initiate_handoff(context: ConversationContext, trigger: HandoffTrigger):
    1. Log handoff reason and context
    2. Notify front desk via PMS integration
    3. Provide guest with wait time estimate
    4. Transfer conversation transcript to staff
    5. Keep session alive for seamless transition
```

---

## 7. Component Diagram

```
+------------------------------------------------------------------+
|                        NomadAI Voice Agent                        |
+------------------------------------------------------------------+
|                                                                    |
|  +------------------+       +------------------+                   |
|  |    Interfaces    |       |    Core Engine   |                   |
|  +------------------+       +------------------+                   |
|  | - Web App        |       | - IntentRouter   |                   |
|  | - WhatsApp       |  -->  | - SkillRegistry  |                   |
|  | - SMS Gateway    |       | - ContextManager |                   |
|  | - In-Room Device |       | - AgentOrch.     |                   |
|  +------------------+       +------------------+                   |
|                                    |                               |
|                                    v                               |
|  +------------------+       +------------------+                   |
|  |    AI Services   |       |     Agents       |                   |
|  +------------------+       +------------------+                   |
|  | - GLM-ASR-2512   |  <->  | - ConciergeAgent |                   |
|  | - GLM-4.7        |       | - SightseeingAgt |                   |
|  | - GLM-4-Voice    |       | - MediaAgent     |                   |
|  | - CogView-4      |       | - SystemAgent    |                   |
|  | - CogVideoX      |       +------------------+                   |
|  +------------------+              |                               |
|                                    v                               |
|  +------------------+       +------------------+                   |
|  |   Integrations   |       |     Skills       |                   |
|  +------------------+       +------------------+                   |
|  | - PMS (Mews)     |  <->  | - RoomService    |                   |
|  | - Maps API       |       | - Housekeeping   |                   |
|  | - Viator API     |       | - LocalRecs      |                   |
|  | - Events API     |       | - Directions     |                   |
|  +------------------+       | - Booking        |                   |
|                             | - MediaGen       |                   |
|                             +------------------+                   |
|                                                                    |
+------------------------------------------------------------------+
```

---

## 8. Data Flow Sequence

### 8.1 Standard Request Flow

```
Guest                 Web App              Router               Agent              Backend
  |                      |                    |                    |                   |
  |---(1) Audio-------->|                    |                    |                   |
  |                      |---(2) ASR-------->|                    |                   |
  |                      |<---(3) Text-------|                    |                   |
  |                      |---(4) Classify--->|                    |                   |
  |                      |<---(5) Intent-----|                    |                   |
  |                      |---(6) Execute-----|---(7) Route------->|                   |
  |                      |                    |                    |---(8) API Call-->|
  |                      |                    |                    |<---(9) Result----|
  |                      |                    |<---(10) Response---|                   |
  |                      |<---(11) TTS-------|                    |                   |
  |<---(12) Audio--------|                    |                    |                   |
```

---

## 9. Security Considerations

### 9.1 Authentication

- Session tokens for guest identification
- API keys for service-to-service communication
- JWT tokens with short expiry for sensitive operations

### 9.2 Data Protection

- Audio data retained for 24 hours maximum
- PII anonymized in logs
- Encryption at rest (AES-256) and in transit (TLS 1.3)

### 9.3 Rate Limiting

```python
RATE_LIMITS = {
    "requests_per_minute": 30,
    "audio_uploads_per_minute": 10,
    "media_generations_per_hour": 5,
}
```

---

## 10. Appendix

### A. Skill ID Reference

| ID | Name | Category |
|----|------|----------|
| CON-001 | Room Service | concierge |
| CON-002 | Housekeeping | concierge |
| CON-003 | Amenities Info | concierge |
| CON-004 | WiFi Help | concierge |
| CON-005 | Check-out | concierge |
| CON-006 | Complaints | concierge |
| CON-007 | Wake-up Call | concierge |
| CON-008 | Billing | concierge |
| SEE-001 | Local Recommendations | sightseeing |
| SEE-002 | Itinerary Planning | sightseeing |
| SEE-003 | Directions | sightseeing |
| SEE-004 | Events | sightseeing |
| SEE-005 | Booking | sightseeing |
| SEE-006 | Translation | sightseeing |
| SEE-007 | Destination Preview | sightseeing |
| SEE-008 | Video Tour | sightseeing |
| SYS-001 | Language Switch | system |
| SYS-002 | Human Handoff | system |
| SYS-003 | Repeat | system |
| SYS-004 | Slow Down | system |
| SYS-005 | Conversation Reset | system |
| MED-001 | Image Generation | media |
| MED-002 | Video Generation | media |

### B. Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.11+ |
| Web Framework | FastAPI |
| Async Runtime | asyncio / uvloop |
| State Store | Redis |
| Database | PostgreSQL |
| AI Platform | Z.AI (zhipuai SDK) |
| Deployment | Vercel (serverless) |

---

**Document Owner:** NomadAI Engineering Team
**Last Updated:** 2026-02-08
