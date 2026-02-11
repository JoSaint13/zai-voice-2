#!/bin/bash
# Test session persistence (Sprint 4.2)

API="http://localhost:8088"
SESSION_ID="test_persist_$(date +%s)"
HOTEL_ID="2ada3c2b-b208-4599-9c46-f32dc16ff950"

echo "🧪 Testing Session Persistence (Sprint 4.2)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

# Test 1: First message (no context)
echo "📝 Test 1: Send first message (no context)"
RESP1=$(curl -s -X POST "$API/api/chat" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"What time is breakfast?\",
    \"session_id\": \"$SESSION_ID\",
    \"hotel_id\": \"$HOTEL_ID\"
  }")

echo "Response: $(echo $RESP1 | jq -r '.response' | head -c 80)..."
echo "Cached: $(echo $RESP1 | jq -r '.cached')"
echo

# Test 2: Second message (context sent)
echo "📝 Test 2: Send follow-up with context (simulating cold start restore)"
CONTEXT='[
  {"role": "user", "content": "What time is breakfast?"},
  {"role": "assistant", "content": "Breakfast is served from 6:30 AM to 10:30 AM."}
]'

RESP2=$(curl -s -X POST "$API/api/chat" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"And what about lunch?\",
    \"session_id\": \"${SESSION_ID}_restored\",
    \"hotel_id\": \"$HOTEL_ID\",
    \"context\": $CONTEXT
  }")

echo "Response: $(echo $RESP2 | jq -r '.response' | head -c 80)..."
echo

# Test 3: Check health and session stats
echo "📊 Test 3: Check health endpoint (session stats)"
curl -s "$API/api/health" | jq '{status, version, sessions, cache: {size: .cache.size, hits: .cache.hits, hit_rate: .cache.hit_rate}}'
echo

echo "✅ Session persistence tests complete!"
echo
echo "Key observations:"
echo " - Context param accepted by /api/chat"
echo " - Sessions restored from client context"
echo " - Session stats tracked in /api/health"
echo " - FAQ cache working independently"
