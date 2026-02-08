# NomadAI Voice Agent - Scripts

Utility scripts for testing and demonstrating the voice agent pipeline.

## demo.py

Complete pipeline demo script that validates the NomadAI Voice Agent implementation without requiring actual audio input.

### Features

- **Health Check**: Verifies API is running and responding
- **Chat Endpoint Testing**: Validates single-message chat
- **Multi-Turn Conversation**: Tests session-based conversation
- **Session Management**: Verifies session reset functionality
- **Transcription Endpoint**: Tests audio transcription interface
- **Comprehensive Reporting**: Detailed results at each stage

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt

# Start the Flask API server in another terminal
python api/index.py
```

### Usage

#### Full Pipeline Demo
```bash
python scripts/demo.py
```

Output shows results at each stage:
- Health check status
- Chat response validation
- Multi-turn conversation flow
- Session management
- Summary of all tests

#### Quick Health Check
```bash
python scripts/demo.py --quick
```

Just verifies the API is running without full tests.

#### Custom API URL
```bash
python scripts/demo.py --api-url http://example.com:3000
```

For testing against remote API servers.

### Execution Flow

1. **Health Check** (Step 0)
   - Verifies API is reachable
   - Checks response format
   - Exits if API unavailable

2. **Single Message Chat** (Step 1)
   - Sends test message to API
   - Validates response format
   - Checks success flag

3. **Multi-Turn Conversation** (Step 2)
   - Conducts 3-turn conversation
   - Validates session persistence
   - Tests conversation context

4. **Session Reset** (Step 3)
   - Resets conversation history
   - Verifies reset success
   - Confirms session cleanup

5. **Transcription Endpoint** (Step 4)
   - Tests with dummy WAV file
   - Validates endpoint structure
   - Notes: Requires valid ZHIPUAI_API_KEY for actual transcription

### Example Output

```
============================================================
  NomadAI Voice Agent - Pipeline Demo
============================================================

API URL: http://localhost:3000
Session ID: demo-session-1707383400

========================================
  [Step 0] Health Check
========================================

  Status: ok
  Message: Clawdbot API is running

========================================
  [Step 1] Chat Endpoint - Single Message
========================================

Sending: 'Hello! What's your name?'
  Response: Hello! I'm Clawdbot, your friendly AI assistant. How can I help you today?

========================================
  [Step 2] Multi-Turn Conversation (3 exchanges)
========================================

Turn 1 - User: How are you today?
Turn 1 - Bot: I'm doing great! Thanks for asking. How can I assist you?

...

============================================================
  Test Summary
============================================================

Results:
  ✓ Passed:  6
  ~ Partial: 0
  ✗ Failed:  0
  Total:   6
```

### Error Handling

The demo gracefully handles various error scenarios:

- **API Not Running**: Clear message with startup instructions
- **Invalid API URL**: Connection error with helpful feedback
- **Invalid Base64**: Handled as expected endpoint behavior
- **Missing API Key**: Partial credit for endpoint verification
- **Network Issues**: Timeout messages with retry guidance

### Return Codes

- `0`: All tests passed or API verified working
- `1`: API unavailable or critical tests failed

### Troubleshooting

#### "Could not connect to API"
```bash
# Make sure Flask app is running
cd /home/user/zai-voice-2
python api/index.py
```

#### "API Error" messages during transcription
This is expected if `ZHIPUAI_API_KEY` is not set:
```bash
export ZHIPUAI_API_KEY='your-api-key-here'
```

#### Custom API endpoint issues
Verify the URL is accessible:
```bash
curl http://your-api-url:3000/
```

### Demo Use Cases

1. **Local Development**
   - Validate setup works before running tests
   - Quick verification during development
   - Testing configuration changes

2. **CI/CD Pipeline**
   - Integration tests in automated workflows
   - Quick smoke tests before main test suite
   - Health check before deployment

3. **Deployment Verification**
   - Verify API is running in production
   - Validate configuration on new servers
   - Smoke test after deployments

4. **Documentation**
   - Show expected behavior to users
   - Document API response formats
   - Demonstrate multi-turn conversation flow

### Extending the Demo

To add additional tests:

1. Add new method to `VoicePipelineDemo` class
2. Call method from `run_full_demo()`
3. Follow existing print/result patterns
4. Update summary if needed

Example:
```python
def test_custom_feature(self) -> bool:
    """Test custom feature."""
    self.print_step(5, "Custom Feature")
    # Test code here
    self.results.append(('custom_feature', True, result))
    return True
```

### Performance Notes

- Full demo typically completes in 5-10 seconds
- Includes realistic API response times
- Network latency will affect total time
- No actual model inference happens

### Related Files

- `api/index.py` - Flask API server
- `clawdbot.py` - Voice agent implementation
- `tests/test_api.py` - Comprehensive API tests
- `tests/test_skills.py` - Skill system tests
