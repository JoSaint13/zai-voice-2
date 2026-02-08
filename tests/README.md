# NomadAI Voice Agent - Test Suite

Comprehensive test suite for validating the NomadAI Voice Agent implementation.

## Test Files

### test_api.py
Tests for Flask API endpoints and HTTP interface.

**Coverage:**
- `TestChatEndpoint` - Chat endpoint functionality
  - Successful chat requests
  - Missing message parameter validation
  - Session management with session IDs
  - API error handling

- `TestTranscriptionEndpoint` - Audio transcription endpoint
  - Successful transcription with base64-encoded audio
  - Missing audio_base64 parameter validation
  - Invalid base64 data handling
  - API error handling

- `TestVoiceChatEndpoint` - Combined transcription + chat pipeline
  - End-to-end voice chat (transcription then response)
  - Missing audio parameter validation
  - Session context preservation
  - Transcription error handling

- `TestSessionManagement` - Conversation session handling
  - Session isolation between different users
  - Conversation history reset functionality
  - Non-existent session handling

- `TestHomeEndpoint` - Health check endpoint
  - API health status verification

### test_skills.py
Tests for the skill system and intent routing engine.

**Coverage:**
- `TestSkillBaseInterface` - Skill class contract
  - Skill initialization with intents
  - Intent matching (case-insensitive)
  - Skill enable/disable functionality

- `TestIntentRouting` - Intent router logic
  - Skill registration
  - Routing to matched skills
  - Handling unmatched intents
  - Multiple skill coordination
  - Context passing
  - Error handling in skills
  - Disabled skill skipping

- `TestSkillExecution` - Individual skill performance
  - Weather skill execution
  - Time skill execution
  - Calculator skill execution
  - Multi-intent skill matching

- `TestIntentRouterIntegration` - Full router integration
  - Skill priority/ordering
  - Listing registered skills
  - Sequential request routing

## Running Tests

### Prerequisites
Install test dependencies:
```bash
pip install -r requirements.txt
```

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
# Test API endpoints only
pytest tests/test_api.py -v

# Test skills system only
pytest tests/test_skills.py -v
```

### Run Specific Test Class
```bash
pytest tests/test_api.py::TestChatEndpoint -v
```

### Run Specific Test
```bash
pytest tests/test_api.py::TestChatEndpoint::test_chat_endpoint_success -v
```

### Run with Verbose Output
```bash
pytest -v
```

### Run with Short Traceback
```bash
pytest --tb=short
```

### Run with Coverage Report
```bash
pip install pytest-cov
pytest --cov=api --cov=tests --cov-report=html
```

## Test Fixtures

### test_api.py Fixtures
- `app` - Flask test app instance
- `client` - Flask test client
- `mock_zhipu_client` - Mocked ZhipuAI client

### test_skills.py Fixtures
- `skill_router` - IntentRouter instance
- `mock_weather_skill` - Sample weather skill
- `mock_time_skill` - Sample time skill
- `mock_calculator_skill` - Sample calculator skill

## Mocking Strategy

### API Tests
All external API calls are mocked using `unittest.mock`:
- ZhipuAI client methods are patched
- Flask requests are handled by test client
- No actual API calls are made (safe for offline testing)

### Skills Tests
Skills are implemented as test fixtures:
- Complete skill implementations included in test file
- Demonstrates expected skill interface
- All skills follow SkillBase abstract class contract

## Expected Test Results

All tests should pass when:
1. Flask app is properly configured
2. ZhipuAI imports are available (mocked in tests)
3. All dependencies are installed

### Typical Output
```
tests/test_api.py::TestChatEndpoint::test_chat_endpoint_success PASSED
tests/test_api.py::TestChatEndpoint::test_chat_missing_message PASSED
tests/test_api.py::TestTranscriptionEndpoint::test_transcribe_success PASSED
...
tests/test_skills.py::TestSkillBaseInterface::test_skill_initialization PASSED
...

======================== X passed in Y.XX seconds =========================
```

## Troubleshooting

### Import Errors
If you get `ModuleNotFoundError: No module named 'zhipuai'`:
- This is expected - the tests mock the ZhipuAI client
- The mocking happens before import, so tests still work

### Flask App Issues
If Flask tests fail to initialize:
- Ensure `ZHIPUAI_API_KEY` environment variable is set
- The test fixtures mock this automatically

### Assertion Failures
If tests fail on assertions:
- Review the error message for which assertion failed
- Check mock data matches expected format
- Verify API response structure matches test expectations

## Test Markers

Use pytest markers to run subsets of tests:

```bash
# Run only API tests
pytest -m api

# Run only skill tests
pytest -m skills

# Skip slow tests
pytest -m "not slow"
```

## Adding New Tests

When adding new features:

1. **For API endpoints:** Add to `test_api.py` with corresponding test class
2. **For skills:** Add to `test_skills.py` with skill implementation + tests
3. **Follow naming:** All test functions must start with `test_`
4. **Use fixtures:** Leverage existing fixtures rather than creating duplicates
5. **Mock externals:** Always mock external API calls
6. **Document:** Add docstrings explaining what is being tested

## Integration with CI/CD

This test suite is designed for:
- Local development (`pytest`)
- CI/CD pipelines (GitHub Actions, GitLab CI, etc.)
- Pre-commit hooks (`pytest tests/`)
- Code coverage tracking

Example GitHub Actions workflow:
```yaml
- name: Run Tests
  run: |
    pip install -r requirements.txt
    pytest --cov=api tests/
```

## Coverage Goals

- API endpoints: 100% coverage
- Error paths: 100% coverage
- Skill system: 95%+ coverage
- Overall: 90%+ coverage

Check coverage with:
```bash
pytest --cov=. --cov-report=term-missing
```
