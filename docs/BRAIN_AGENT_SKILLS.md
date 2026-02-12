# Brain Agent Skills

**LLM:** XiaomiMiMo/MiMo-V2-Flash (via Chutes.ai)  
**Total Skills:** 12 tools/functions  
**Location:** `api/index.py` lines 1282-1453  
**Last Updated:** 2026-02-12

---

## Overview

The brain agent uses **tool calling** (function calling) to handle guest requests. When a user message arrives, the LLM analyzes intent and decides which tool(s) to call. Tools are executed via `_execute_tool()`, and results are synthesized into the final response.

### Agent Loop Flow

```
User Message
    ↓
agent_loop() — orchestration
    ↓
Brain LLM (MiMo-V2-Flash) — intent analysis
    ↓
Tool Call Decision (auto)
    ↓
_execute_tool() — skill execution
    ↓
Result → LLM
    ↓
Final Response → User
```

**Max Iterations:** 5 (prevents infinite loops)  
**Tool Choice:** `auto` (LLM decides when to use tools)

---

## 🏨 Hotel & Concierge Services (6 skills)

### 1. room_service

**Description:** Order food and beverages to the guest's room  
**Parameters:**
- `request` (string, required) — What the guest wants to order

**Example Queries:**
- "I'd like breakfast to my room"
- "Can I order a club sandwich?"
- "Order two coffees to room 305"

**Implementation:** Mock acknowledgment (logs request)

---

### 2. housekeeping

**Description:** Request housekeeping services (towels, cleaning, supplies)  
**Parameters:**
- `request` (string, required) — What the guest needs

**Example Queries:**
- "Can I get fresh towels?"
- "I need extra pillows"
- "Please clean my room now"

**Implementation:** Mock acknowledgment (logs request)

---

### 3. amenities_info

**Description:** Get info about hotel amenities, hours, facilities (pool, gym, spa, restaurant)  
**Parameters:**
- `query` (string, required) — What amenity or facility the guest is asking about

**Example Queries:**
- "What time does the pool open?"
- "Do you have a gym?"
- "What are the restaurant hours?"
- "Is there a spa?"

**Implementation:** Functional — retrieves data from `data/hotels/*.json`

**Knowledge Base:** NomadAI Hotel data includes:
- Restaurant: Sakura Dining (6:30 AM - 10:30 AM breakfast, 11:30 AM - 11:00 PM dinner)
- Pool: 6 AM - 10 PM
- Gym: 24/7 access
- Spa: 9 AM - 9 PM
- WiFi: GuestNet (password in wifi_help)

---

### 4. wifi_help

**Description:** Provide WiFi password or help with connectivity issues  
**Parameters:**
- `issue` (string, required) — WiFi issue description

**Example Queries:**
- "What's the WiFi password?"
- "I can't connect to WiFi"
- "How do I access the internet?"

**Implementation:** Functional — retrieves credentials from hotel data  
**NomadAI Hotel WiFi:**
- Network: GuestNet
- Password: Welcome2024!

---

### 5. check_out

**Description:** Assist with hotel checkout process and final billing  
**Parameters:**
- `request` (string, required) — Checkout request details

**Example Queries:**
- "I need a late checkout"
- "Can I check out at noon?"
- "Help me with checkout"

**Implementation:** Mock acknowledgment (simulates checkout process)

---

### 6. wake_up_call

**Description:** Schedule a wake-up call for the guest  
**Parameters:**
- `request` (string, required) — Wake-up call time and date

**Example Queries:**
- "Wake me up at 7am tomorrow"
- "Set a wake-up call for 6:30"
- "I need a morning call"

**Implementation:** Mock acknowledgment (simulates scheduling)

---

## 🗺️ Sightseeing & Local Exploration (3 skills)

### 7. local_recommendations

**Description:** Suggest local restaurants, attractions, points of interest  
**Parameters:**
- `query` (string, required) — What kind of place or activity the guest wants

**Example Queries:**
- "Best ramen near the hotel"
- "Recommend a good sushi place"
- "What should I see in Tokyo?"
- "Where can I buy souvenirs?"

**Implementation:** Mock suggestions (returns generic Tokyo recommendations)

---

### 8. itinerary_planning

**Description:** Create personalized day plans and sightseeing itineraries  
**Parameters:**
- `request` (string, required) — What kind of day plan the guest wants

**Example Queries:**
- "Plan a full day in Shibuya"
- "Create an itinerary for tomorrow"
- "What should I do this afternoon?"

**Implementation:** Mock itineraries (returns sample Tokyo day plans)

---

### 9. directions

**Description:** Help navigate to a destination with directions  
**Parameters:**
- `destination` (string, required) — Where the guest wants to go

**Example Queries:**
- "How do I get to Tokyo Tower?"
- "Directions to Shibuya station"
- "Where is the nearest convenience store?"

**Implementation:** Mock directions (returns generic navigation help)

---

## 📞 Advanced Services (3 skills)

### 10. voice_call

**Description:** Make a phone call on behalf of the guest (e.g., call a restaurant to make a reservation)  
**Parameters:**
- `action` (string, required, enum) — `initiate_call`, `speak`, `end_call`, `get_status`
- `to` (string) — Phone number or place name to call
- `message` (string) — What to say on the call

**Example Queries:**
- "Call Sakura restaurant to book a table for 2"
- "Make a reservation at the sushi place"
- "Phone the front desk"

**Implementation:** Mock call simulation  
**Call Flow:**
1. `initiate_call` → "Dialing {to}..."
2. `speak` → "Speaking: {message}"
3. `end_call` → "Call ended"
4. `get_status` → Current call status

**Mock Restaurant Data:**
- Sakura (Sushi): +81-3-1234-5678
- Ramen House: +81-3-2345-6789
- Tempura Place: +81-3-3456-7890

**Note:** This is a Phase 3 feature with mock responses. Real Twilio integration planned.

---

### 11. complaints

**Description:** Log and acknowledge guest complaints or service issues  
**Parameters:**
- `issue` (string, required) — Description of the complaint or issue

**Example Queries:**
- "Room is too cold"
- "The TV doesn't work"
- "There's noise from the hallway"

**Implementation:** Logs complaint (simulates ticket creation)

---

### 12. billing_inquiry

**Description:** Provide information about guest bill and charges  
**Parameters:**
- `query` (string, required) — What billing information the guest wants

**Example Queries:**
- "What are the charges on my bill?"
- "How much do I owe?"
- "Show me my invoice"

**Implementation:** Mock billing info (returns sample charges)

---

## Testing Skills

### Manual Testing

1. Open: http://localhost:8088
2. Navigate to **Chat** tab
3. Type queries from examples above
4. Observe:
   - LLM response includes tool result
   - Logs show `tool_call` events

### Example Conversations

**Test amenities_info:**
```
User: What time is breakfast served?
Bot: Breakfast at Sakura Dining is served from 6:30 AM to 10:30 AM.
```

**Test wifi_help:**
```
User: What's the WiFi password?
Bot: Connect to GuestNet with password: Welcome2024!
```

**Test voice_call:**
```
User: Call Sakura restaurant to book a table for 2 at 7pm
Bot: [Initiates mock call]
     I've called Sakura restaurant (+81-3-1234-5678) and requested...
```

### Log Inspection

Check tool call logs:
```bash
tail -f /tmp/nomadai-mute.log | grep "tool_call"
```

Look for:
- `[agent_loop] iteration=1/5 msgs=3`
- `[agent_loop] tool_call: amenities_info({'query': 'breakfast'})`
- `[agent_loop] tool_result (123 chars)`

---

## Implementation Details

### Code Locations

| Component | File | Lines | Description |
|-----------|------|-------|-------------|
| SKILL_TOOLS | `api/index.py` | 1282-1453 | OpenAI function schema definitions |
| SKILL_MAP | `api/index.py` | 1456-1458 | Tool name → skill instance mapping |
| _execute_tool() | `api/index.py` | 1461-1489 | Tool dispatcher |
| _execute_voice_call() | `api/index.py` | 1491-1562 | Mock voice call handler |
| agent_loop() | `api/index.py` | 1594-1746 | Orchestration loop |

### Skill Classes (src/skills/)

```
src/skills/
├── __init__.py           # Export all skills
├── base.py              # BaseSkill, SkillRegistry, Context
├── concierge.py         # RoomServiceSkill, HousekeepingSkill, etc.
└── sightseeing.py       # LocalRecommendationSkill, ItinerarySkill
```

**Note:** Current implementation uses simplified in-memory skills with mock data. Skill classes are defined but not fully wired.

### Knowledge Base

**File:** `data/hotels/2ada3c2b-b208-4599-9c46-f32dc16ff950.json`

```json
{
  "id": "2ada3c2b-b208-4599-9c46-f32dc16ff950",
  "name": "NomadAI Hotel",
  "location": "Tokyo, Japan",
  "amenities": {
    "pool": { "hours": "6 AM - 10 PM" },
    "gym": { "hours": "24/7" },
    "spa": { "hours": "9 AM - 9 PM" },
    "restaurant": {
      "name": "Sakura Dining",
      "breakfast": "6:30 AM - 10:30 AM",
      "dinner": "11:30 AM - 11:00 PM"
    }
  },
  "wifi": {
    "ssid": "GuestNet",
    "password": "Welcome2024!"
  },
  "check_in_time": "3:00 PM",
  "check_out_time": "11:00 AM"
}
```

---

## Future Enhancements

### Planned

1. **Real PMS Integration**
   - Connect to Mews/Cloudbeds APIs
   - Real-time room status
   - Actual order submission

2. **Voice Call via Twilio**
   - Replace mock with real phone calls
   - Speech recognition on calls
   - Call recording & transcription

3. **Dynamic Knowledge Base**
   - Multi-hotel support
   - Real-time amenity updates
   - Seasonal hours

4. **Advanced Skills**
   - `transportation_booking` — book taxis, trains
   - `event_tickets` — purchase show/museum tickets
   - `emergency_services` — urgent assistance routing

### Possible

- **Skill Analytics** — track most-used tools
- **Custom Skills per Hotel** — hotel-specific tools
- **Multi-Language Skills** — localized responses
- **Skill Chaining** — compose multiple skills in one query

---

## Troubleshooting

### Skill Not Triggering

**Symptom:** LLM doesn't call expected tool

**Causes:**
1. Query too vague (LLM can't determine intent)
2. Tool description unclear
3. Max iterations reached (5)

**Solutions:**
- Rephrase query more explicitly
- Check tool schema in SKILL_TOOLS
- Check logs for `[agent_loop] final_answer`

### Tool Call Error

**Symptom:** Error in tool execution

**Causes:**
1. Missing required parameter
2. Invalid hotel data
3. Skill implementation bug

**Solutions:**
- Check logs: `grep "tool_call" /tmp/nomadai-mute.log`
- Verify hotel data exists: `ls -la data/hotels/`
- Check `_execute_tool()` error handling

### Response Too Generic

**Symptom:** LLM ignores tool result

**Causes:**
1. Tool returned empty/error
2. LLM hallucinating instead of using tool data

**Solutions:**
- Verify tool returns useful data
- Check system prompt (emphasizes using tool results)
- Increase max_tokens if response cut off

---

## Summary

**Total Skills:** 12 functional tools  
**Categories:** Hotel Services (6), Sightseeing (3), Advanced (3)  
**Status:** All skills operational (most with mock data)  
**Next Steps:** PMS integration, real voice calls, enhanced knowledge base

**Test Now:** http://localhost:8088 → Chat tab → "What time is breakfast?"
