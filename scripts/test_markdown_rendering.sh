#!/bin/bash

# Test markdown rendering in UI (visual test - requires browser)

API="${API_URL:-http://localhost:8088}"
HOTEL_ID="${HOTEL_ID:-2ada3c2b-b208-4599-9c46-f32dc16ff950}"

cat << 'EOF'
╔══════════════════════════════════════════════════════════════════════╗
║              Markdown Rendering Test (Visual)                        ║
║              Requires browser inspection                             ║
╚══════════════════════════════════════════════════════════════════════╝

This test verifies that bot responses render markdown correctly.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Manual Testing Steps:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EOF

echo "1️⃣  Open: $API"
echo "2️⃣  Switch to 'Voice' tab"
echo "3️⃣  Type or say: 'show me your knowledge'"
echo
echo "Expected UI rendering:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   I'm your AI concierge at NomadAI Hotel! I can help you with:"
echo
echo "   🏨 Hotel Services - Room service, housekeeping, check-in/out assistance"
echo "      ^^^ Should be BOLD (not **bold**)"
echo
echo "   🍴 Dining & Facilities - Restaurant hours, pool, gym, spa information"
echo "      ^^^ Should be BOLD"
echo
echo "   🗺️ Local Exploration - Nearby restaurants, attractions, directions"
echo "      ^^^ Should be BOLD"
echo
echo "   📞 Personal Assistance - Make phone calls, create itineraries"
echo "      ^^^ Should be BOLD"
echo
echo "   What would you like to know more about?"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "Visual checks:"
echo "  ✓ Category titles are bold (not **text**)"
echo "  ✓ Line breaks between categories"
echo "  ✓ Emojis display correctly"
echo "  ✓ No raw markdown syntax visible"
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  Inspect with DevTools (F12):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "Find the bot message element and verify HTML structure:"
echo
echo "Expected DOM structure:"
cat << 'HTML'
<div class="msg assistant">
  <div class="lbl">Concierge</div>
  <div>
    <p>I'm your AI concierge at NomadAI Hotel! I can help you with:</p>
    <p>🏨 <strong>Hotel Services</strong> - Room service, housekeeping...</p>
    <p>🍴 <strong>Dining &amp; Facilities</strong> - Restaurant hours...</p>
    <p>🗺️ <strong>Local Exploration</strong> - Nearby restaurants...</p>
    <p>📞 <strong>Personal Assistance</strong> - Make phone calls...</p>
    <p>What would you like to know more about?</p>
  </div>
</div>
HTML

echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Additional Tests:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "5️⃣  Test other queries to verify markdown parsing:"
echo
echo "   • 'what can you help with' → should have bold categories"
echo "   • 'what time is breakfast' → plain answer (no special formatting)"
echo "   • 'tell me about the pool' → might have bold headings if LLM uses them"
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Automated Check (response text):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

# Get raw response text from API
RESPONSE=$(curl -s -X POST "$API/api/chat" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"show me your knowledge\", \"session_id\": \"markdown_test\", \"hotel_id\": \"$HOTEL_ID\"}" \
  | jq -r '.response')

echo "Raw API response (should contain markdown):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "$RESPONSE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

# Verify markdown is present
if [[ "$RESPONSE" == *"**Hotel Services**"* ]]; then
    echo "✅ PASS: Response contains markdown (**bold**)"
else
    echo "❌ FAIL: Response missing markdown formatting"
fi

if [[ "$RESPONSE" == *"🏨"* ]] && [[ "$RESPONSE" == *"🍴"* ]]; then
    echo "✅ PASS: Response contains emojis"
else
    echo "❌ FAIL: Response missing emojis"
fi

echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Frontend Verification (requires browser):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "1. Backend sends markdown: **Hotel Services**"
echo "2. marked.js parses: <strong>Hotel Services</strong>"
echo "3. CSS renders: bold text with white color"
echo
echo "✅ If you see BOLD text in browser → markdown rendering works!"
echo "❌ If you see **Hotel Services** → markdown parsing failed"
echo
