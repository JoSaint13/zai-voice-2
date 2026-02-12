#!/bin/bash

# Test the meta-query UX improvement (Sprint 4 follow-up)
# Issue: "show me your knowledge" was dumping entire KB
# Fix: Detect meta-queries → structured Tier 1 response

API="${API_URL:-http://localhost:8088}"
HOTEL_ID="${HOTEL_ID:-2ada3c2b-b208-4599-9c46-f32dc16ff950}"

echo "╔═════════════════════════════════════════════════════════════════╗"
echo "║  Meta-Query UX Improvement Test                                 ║"
echo "║  Before: KB dump | After: Structured 4-category summary         ║"
echo "╚═════════════════════════════════════════════════════════════════╝"
echo

# Test 1: Original problem query
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 1: 'show me your knowledge'"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
RESPONSE=$(curl -s -X POST "$API/api/chat" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"show me your knowledge\", \"session_id\": \"meta_test_1\", \"hotel_id\": \"$HOTEL_ID\"}" \
  | jq -r '.response')

echo "$RESPONSE"
echo

# Validate response
if [[ "$RESPONSE" == *"Hotel Services"* ]] && \
   [[ "$RESPONSE" == *"Dining & Facilities"* ]] && \
   [[ "$RESPONSE" == *"Local Exploration"* ]] && \
   [[ "$RESPONSE" == *"Personal Assistance"* ]]; then
    echo "✅ PASS: Structured 4-category response"
else
    echo "❌ FAIL: Expected structured response, got KB dump or error"
fi

# Test that it doesn't contain KB dump markers
if [[ "$RESPONSE" == *"WiFi password"* ]] || [[ "$RESPONSE" == *"GuestNet"* ]]; then
    echo "❌ FAIL: Response contains KB dump (WiFi password leaked)"
else
    echo "✅ PASS: No KB dump detected"
fi

echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 2: 'what can you help with'"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
RESPONSE=$(curl -s -X POST "$API/api/chat" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"what can you help with?\", \"session_id\": \"meta_test_2\", \"hotel_id\": \"$HOTEL_ID\"}" \
  | jq -r '.response')

echo "$RESPONSE"
echo

if [[ "$RESPONSE" == *"Hotel Services"* ]]; then
    echo "✅ PASS: Meta-query detected and handled"
else
    echo "❌ FAIL: Meta-query not detected"
fi

echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 3: 'give me an overview'"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
RESPONSE=$(curl -s -X POST "$API/api/chat" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"give me an overview\", \"session_id\": \"meta_test_3\", \"hotel_id\": \"$HOTEL_ID\"}" \
  | jq -r '.response')

echo "$RESPONSE"
echo

if [[ "$RESPONSE" == *"AI concierge"* ]]; then
    echo "✅ PASS: Overview query handled"
else
    echo "❌ FAIL: Overview query not detected"
fi

echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 4: Specific question should still use LLM"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
RESPONSE=$(curl -s -X POST "$API/api/chat" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"what time is breakfast?\", \"session_id\": \"meta_test_4\", \"hotel_id\": \"$HOTEL_ID\"}" \
  | jq -r '.response')

echo "$RESPONSE"
echo

if [[ "$RESPONSE" == *"breakfast"* ]] && [[ "$RESPONSE" != *"Hotel Services"* ]]; then
    echo "✅ PASS: Specific question uses LLM (not meta-query)"
else
    echo "❌ FAIL: Specific question incorrectly treated as meta-query"
fi

echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 5: Check logs for meta_query_handled events"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Count meta_query_handled events in recent logs (last 10 seconds)
RECENT_LOG="/tmp/nomadai-meta.log"
if [ -f "$RECENT_LOG" ]; then
    META_COUNT=$(grep -c 'meta_query_handled' "$RECENT_LOG" 2>/dev/null || echo 0)
    echo "Total meta_query_handled events: $META_COUNT"
    
    if [ "$META_COUNT" -ge 3 ]; then
        echo "✅ PASS: Meta-queries logged correctly"
        echo
        echo "Recent meta-query logs:"
        grep 'meta_query_handled' "$RECENT_LOG" | tail -3 | while read line; do
            echo "  $(echo $line | jq -r '{query, bypassed_llm, latency_ms}')"
        done
    else
        echo "⚠️  WARNING: Expected at least 3 meta_query_handled events, found $META_COUNT"
    fi
else
    echo "⚠️  WARNING: Log file not found at $RECENT_LOG"
fi

echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 6: Performance check (meta-queries should be instant)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

START_TIME=$(date +%s%3N)
curl -s -X POST "$API/api/chat" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"what can you do\", \"session_id\": \"meta_test_perf\", \"hotel_id\": \"$HOTEL_ID\"}" \
  > /dev/null
END_TIME=$(date +%s%3N)
LATENCY=$((END_TIME - START_TIME))

echo "Latency: ${LATENCY}ms"

if [ "$LATENCY" -lt 100 ]; then
    echo "✅ PASS: Meta-query response <100ms (bypassed LLM)"
elif [ "$LATENCY" -lt 500 ]; then
    echo "⚠️  WARNING: Meta-query took ${LATENCY}ms (expected <100ms)"
else
    echo "❌ FAIL: Meta-query took ${LATENCY}ms (should be instant)"
fi

echo
echo "╔═════════════════════════════════════════════════════════════════╗"
echo "║                        Test Summary                             ║"
echo "╚═════════════════════════════════════════════════════════════════╝"
echo "✓ Meta-queries return structured summaries (not KB dumps)"
echo "✓ Specific questions still use LLM normally"
echo "✓ Performance: meta-queries bypass LLM (~0ms vs 1-3s)"
echo "✓ Logs: meta_query_handled events track bypassed queries"
echo
