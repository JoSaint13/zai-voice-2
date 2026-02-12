# Knowledge Access Strategy - Handling Meta-Queries

## Problem
When guests ask "show me your knowledge" or "what can you help with", the system dumps the entire knowledge base, creating poor UX.

## Solution: Multi-Level Knowledge Access

### 1. Meta-Query Detection Patterns

```python
META_QUERY_PATTERNS = {
    "capabilities": [
        r"what can you (do|help)",
        r"show me your (knowledge|capabilities)",
        r"what (are you|do you know)",
        r"list (your|all) (services|features|capabilities)",
        r"tell me (about|what) you (can do|know)"
    ],
    "hotel_overview": [
        r"tell me about (the|this) hotel",
        r"hotel information",
        r"what (is|are) the hotel (facilities|amenities)",
    ],
    "specific_service": [
        r"(breakfast|lunch|dinner|restaurant)",
        r"(pool|gym|spa|fitness)",
        r"(wifi|internet|password)",
        r"(check.*in|check.*out|checkout)",
        r"(parking|park)",
    ]
}
```

### 2. Three-Tier Response Strategy

#### Tier 1: Capabilities Summary (for "what can you do")
**Short, voice-friendly overview:**
```
I'm your AI concierge! I can help you with:

🏨 Hotel Services
   • Room service & housekeeping
   • Check-in/out assistance
   
🍴 Dining & Amenities
   • Restaurant hours & reservations
   • Pool, gym, spa information
   
🗺️ Local Exploration
   • Restaurant recommendations
   • Attractions & directions
   
📞 Personal Assistance
   • Make phone calls for you
   • Create custom itineraries

What would you like help with?
```

#### Tier 2: Category Details (when user asks about specific category)
**Example: "tell me about hotel services"**
```
Hotel Services Available:

Room Service: 24/7
  • Breakfast, lunch, dinner, desserts

Housekeeping:
  • Towels, cleaning, supplies on request

Check-in: 15:00 | Check-out: 11:00

WiFi: NomadAI-Guest (Password: Welcome2026!)

Need help with something specific?
```

#### Tier 3: Specific Information (targeted questions)
**Example: "what time is breakfast"**
```
Breakfast at Sakura Dining is served from 6:30 AM to 10:30 AM.
```

### 3. Implementation Options

#### Option A: New Skill - `show_capabilities`
Add a dedicated tool that the LLM can call when detecting meta-queries.

```python
{
    "type": "function",
    "function": {
        "name": "show_capabilities",
        "description": "Show overview of NomadAI's capabilities when guest asks 'what can you do', 'show me your knowledge', etc.",
        "parameters": {
            "type": "object",
            "properties": {
                "detail_level": {
                    "type": "string",
                    "enum": ["summary", "categories", "full"],
                    "description": "Level of detail to show"
                }
            },
            "required": ["detail_level"]
        }
    }
}
```

#### Option B: Enhanced System Prompt (Simpler)
Update system prompt to handle these queries naturally:

```python
system_prompt = """You are NomadAI, a voice-first AI hotel concierge.

IMPORTANT: When guests ask about your knowledge/capabilities:
- DON'T dump the entire knowledge base
- DO give a friendly, categorized summary (3-4 categories max)
- DO ask follow-up: "What would you like to know more about?"

Knowledge available:
{hotel_context}

Keep responses concise (2-3 sentences) unless asked for details."""
```

#### Option C: Pre-Cached Responses (Fastest)
Add meta-queries to FAQ cache with pre-formatted answers.

```python
# In FAQ_PATTERNS
r"show (me )?your (knowledge|capabilities|skills)",
r"what can you (do|help)",
r"list (all |your )?services",

# Pre-cache the response
faq_cache.set(hotel_id, "what can you do", CAPABILITIES_SUMMARY)
```

### 4. Recommended Implementation (Hybrid)

**Step 1:** Detect meta-queries in FAQ patterns
```python
def is_meta_query(text: str) -> bool:
    """Detect questions about the bot's capabilities."""
    patterns = [
        r"show (me )?your (knowledge|capabilities|skills)",
        r"what can you (do|help)",
        r"what do you know",
        r"list (all |your )?(services|features)",
        r"tell me what you can do"
    ]
    return any(re.search(p, text.lower()) for p in patterns)
```

**Step 2:** Generate structured response
```python
def generate_capabilities_response(hotel_info: dict) -> str:
    """Generate a friendly capabilities summary."""
    return f"""I'm your AI concierge at {hotel_info.get('name', 'this hotel')}! 

I can help you with:

🏨 Hotel Services
   Room service, housekeeping, check-in/out

🍴 Dining & Facilities  
   Restaurant hours, pool, gym, spa info

🗺️ Local Recommendations
   Nearby restaurants, attractions, directions

📞 Personal Help
   Make calls, create itineraries, answer questions

What would you like to know more about?"""
```

**Step 3:** Integrate into agent_loop
```python
# Before calling LLM, check for meta-queries
if is_meta_query(user_message):
    response = generate_capabilities_response(hotel_info)
    messages.append({"role": "assistant", "content": response})
    return response
```

### 5. Progressive Disclosure Pattern

```
User: "show me your knowledge"
Bot: [Tier 1 - Summary with 4 categories]

User: "tell me about dining"
Bot: [Tier 2 - Detailed dining info]

User: "what time is breakfast"
Bot: [Tier 3 - Specific answer]
```

### 6. Voice-Optimized Responses

For voice interface, keep it extra concise:

```
"I can help with hotel services, dining, local recommendations, 
and making calls. What interests you?"
```

vs. text interface can show bullet points.

### 7. Testing Scenarios

| User Query | Expected Response |
|------------|-------------------|
| "show me your knowledge" | Tier 1: Capabilities summary (4 categories) |
| "what can you do" | Tier 1: Same |
| "tell me about hotel services" | Tier 2: Hotel services category details |
| "what time is breakfast" | Tier 3: Specific answer from KB |
| "list all restaurants" | Tier 2: Local recommendations category |
| "help me" | Tier 1: Capabilities summary |

### 8. Implementation Priority

1. ✅ **Quick Win**: Add meta-query detection + structured response (30 min)
2. ⬜ **Medium**: Add FAQ caching for common meta-queries (15 min)
3. ⬜ **Advanced**: Create `show_capabilities` skill with detail levels (1 hour)

### 9. Code Changes Needed

**File:** `api/index.py`

```python
# Add after is_faq_question()
def is_meta_query(text: str) -> bool:
    """Detect meta-queries about bot capabilities."""
    patterns = [
        r"show (me )?your (knowledge|capabilities|skills)",
        r"what can you (do|help with)",
        r"what do you know",
        r"list (all |your )?(services|features|capabilities)",
        r"tell me what you (can do|know about)"
    ]
    return any(re.search(p, text.lower()) for p in patterns)

def generate_capabilities_summary(hotel_info: dict) -> str:
    """Generate friendly capabilities overview."""
    hotel_name = hotel_info.get('name', 'this hotel') if hotel_info else 'this hotel'
    
    return f"""I'm your AI concierge at {hotel_name}! I can help you with:

🏨 Hotel Services - Room service, housekeeping, check-in/out assistance

🍴 Dining & Facilities - Restaurant hours, pool, gym, spa information  

🗺️ Local Exploration - Nearby restaurants, attractions, directions

📞 Personal Assistance - Make phone calls, create itineraries

What would you like to know more about?"""

# In agent_loop(), before LLM call:
# Check for meta-query first
if is_meta_query(user_message):
    response = generate_capabilities_summary(hotel_info)
    messages.append({"role": "assistant", "content": response})
    set_session_messages(session_id, messages)
    
    # Log as simple query
    log_structured("meta_query_handled", 
        session_id=session_id,
        query_type="capabilities",
        bypassed_llm=True)
    
    return response
```

### 10. Benefits

✅ **Better UX**: Structured, readable responses  
✅ **Faster**: Bypass LLM for meta-queries (~0ms vs 1-2s)  
✅ **Voice-Friendly**: Concise, clear categories  
✅ **Progressive**: Guest can drill down as needed  
✅ **Scalable**: Easy to add new categories  

---

## Next Steps

1. Implement meta-query detection (simple pattern matching)
2. Create structured capabilities response template
3. Test with common queries
4. Monitor metrics: % of meta-queries handled instantly
5. Iterate based on user feedback

**Estimated Time:** 30-45 minutes for basic implementation
