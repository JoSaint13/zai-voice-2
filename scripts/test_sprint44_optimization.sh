#!/bin/bash
# Sprint 4.4 Latency Optimization Validation

API="http://localhost:8088"
HOTEL_ID="2ada3c2b-b208-4599-9c46-f32dc16ff950"

echo "🧪 Sprint 4.4: Latency Optimization Validation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

# Test 1: Simple FAQ (256 tokens)
echo "1️⃣  Simple FAQ: 'wifi password' (max_tokens=256)"
echo "   Expected: Fast response, simple answer"
curl -s -X POST "$API/api/chat" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"What's the wifi password?\", \"session_id\": \"opt_simple\", \"hotel_id\": \"$HOTEL_ID\"}" \
  | jq -r '.response' | head -c 80
echo "..."
echo

# Test 2: Simple greeting (256 tokens)
echo "2️⃣  Simple Greeting: 'Hello' (max_tokens=256)"
echo "   Expected: Short greeting response"
curl -s -X POST "$API/api/chat" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"Hello, how are you?\", \"session_id\": \"opt_greeting\", \"hotel_id\": \"$HOTEL_ID\"}" \
  | jq -r '.response' | head -c 80
echo "..."
echo

# Test 3: Medium query (512 tokens)
echo "3️⃣  Medium Query: 'restaurant recommendation' (max_tokens=512)"
echo "   Expected: Moderate response length"
curl -s -X POST "$API/api/chat" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"Can you recommend a good restaurant?\", \"session_id\": \"opt_medium\", \"hotel_id\": \"$HOTEL_ID\"}" \
  | jq -r '.response' | head -c 80
echo "..."
echo

# Test 4: Complex query (1024 tokens)
echo "4️⃣  Complex Query: 'full itinerary planning' (max_tokens=1024)"
echo "   Expected: Detailed response with tool calls"
curl -s -X POST "$API/api/chat" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"Plan a full day itinerary with breakfast, museum visits, lunch, and dinner recommendations\", \"session_id\": \"opt_complex\", \"hotel_id\": \"$HOTEL_ID\"}" \
  | jq -r '.response' | head -c 120
echo "..."
echo

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Check Logs for Complexity Detection:"
echo "   grep 'query_complexity' /tmp/nomadai-sprint44.log | tail -4"
echo
echo "📈 Current Metrics:"
curl -s "$API/api/metrics" | jq '{
  requests: .requests.total,
  avg_llm_latency_ms: .latencies.avg.llm_ms,
  cache_hit_rate: .cache.hit_rate
}'
echo
echo "✅ Sprint 4.4 optimization: Adaptive max_tokens based on query complexity"
echo "   • Simple/FAQ: 256 tokens → faster generation"
echo "   • Medium: 512 tokens → balanced"
echo "   • Complex: 1024 tokens → full capability"
