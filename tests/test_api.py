"""
Tests for NomadAI Flask API endpoints (Chutes.ai provider).

Tests cover:
- Chat endpoint functionality (via Chutes.ai)
- Translate endpoint (prompt-based via Chutes.ai)
- Transcribe/voice-chat stubs (501)
- Provider listing
- Session management
"""

import json
import os
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def app():
    """Create Flask app for testing."""
    if 'api.index' in sys.modules:
        del sys.modules['api.index']

    with patch.dict(os.environ, {'CHUTES_API_KEY': 'cpk_test_key'}):
        from api.index import app as flask_app
        flask_app.config['TESTING'] = True
        return flask_app


@pytest.fixture
def client(app):
    """Create Flask test client."""
    return app.test_client()


class TestChatEndpoint:
    """Test suite for /api/chat endpoint (Chutes.ai)."""

    def test_chat_endpoint_success(self, client):
        """Test successful chat request via Chutes."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "Hello! How can I help?"}}]
        }

        with patch('requests.post', return_value=mock_resp):
            response = client.post(
                '/api/chat',
                data=json.dumps({'message': 'Hello!'}),
                content_type='application/json'
            )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'response' in data

    def test_chat_missing_message(self, client):
        """Test chat request without required message parameter."""
        response = client.post(
            '/api/chat',
            data=json.dumps({}),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_chat_with_model_selection(self, client):
        """Test chat with explicit model selection."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "Response from Qwen"}}]
        }

        with patch('requests.post', return_value=mock_resp):
            response = client.post(
                '/api/chat',
                data=json.dumps({
                    'message': 'Test',
                    'model': 'Qwen/Qwen3-32B'
                }),
                content_type='application/json'
            )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True


class TestTranscribeEndpoint:
    """Test suite for /api/transcribe endpoint (Chutes STT)."""

    def test_transcribe_returns_501(self, client):
        """Transcribe returns text when STT succeeds (mocked)."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"text": "hello world"}

        with patch('requests.post', return_value=mock_resp):
            response = client.post(
                '/api/transcribe',
                data=json.dumps({'audio_base64': 'dGVzdA=='}),
                content_type='application/json'
            )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['text'] == 'hello world'


class TestVoiceChatEndpoint:
    """Test suite for /api/voice-chat endpoint (STT -> LLM -> TTS)."""

    def test_voice_chat_returns_501(self, client):
        """Voice chat returns combined result when all stages succeed (mocked)."""
        # Mock STT, LLM, TTS sequential calls
        stt_resp = MagicMock(status_code=200)
        stt_resp.json.return_value = {"text": "hello"}
        llm_resp = MagicMock(status_code=200)
        llm_resp.json.return_value = {"choices": [{"message": {"content": "Hi there!"}}]}
        tts_resp = MagicMock(status_code=200)
        tts_resp.json.return_value = {"audio": "bWFkZWF1ZGlv"}

        def side_effect(*args, **kwargs):
            url = args[0]
            if 'audio/transcriptions' in url:
                return stt_resp
            if 'chat/completions' in url:
                return llm_resp
            if 'audio/speech' in url:
                return tts_resp
            return llm_resp

        with patch('requests.post', side_effect=side_effect):
            response = client.post(
                '/api/voice-chat',
                data=json.dumps({'audio_base64': 'dGVzdA==', 'session_id': 'voice_test'}),
                content_type='application/json'
            )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['transcription'] == 'hello'
        assert data['response'] == 'Hi there!'
        assert 'audio_base64' in data


class TestTranslateEndpoint:
    """Test suite for /api/translate endpoint (prompt-based via Chutes)."""

    def test_translate_success(self, client):
        """Test translation via chat model."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "チェックアウトは何時ですか？"}}]
        }

        with patch('requests.post', return_value=mock_resp):
            response = client.post(
                '/api/translate',
                data=json.dumps({
                    'text': 'What time is checkout?',
                    'target_lang': 'ja'
                }),
                content_type='application/json'
            )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'translated_text' in data

    def test_translate_missing_text(self, client):
        """Test translate without text parameter."""
        response = client.post(
            '/api/translate',
            data=json.dumps({'target_lang': 'ja'}),
            content_type='application/json'
        )

        assert response.status_code == 400


class TestSlidesEndpoint:
    """Test suite for /api/generate-slides (501 stub)."""

    def test_slides_returns_501(self, client):
        """Slides generation is not available — returns 501."""
        response = client.post(
            '/api/generate-slides',
            data=json.dumps({'topic': 'Tokyo'}),
            content_type='application/json'
        )

        assert response.status_code == 501


class TestVideoEndpoint:
    """Test suite for /api/generate-video (501 stub)."""

    def test_video_returns_501(self, client):
        """Video generation is not available — returns 501."""
        response = client.post(
            '/api/generate-video',
            data=json.dumps({'prompt': 'Tokyo sunset'}),
            content_type='application/json'
        )

        assert response.status_code == 501


class TestProvidersEndpoint:
    """Test suite for /api/providers endpoint."""

    def test_providers_returns_chutes_only(self, client):
        """Provider list should only contain Chutes."""
        response = client.get('/api/providers')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'chutes' in data['providers']
        assert 'zai' not in data['providers']
        assert data['active_provider'] == 'chutes'


class TestSessionManagement:
    """Test suite for conversation session management."""

    def test_reset_conversation(self, client):
        """Test resetting conversation history for a session."""
        response = client.post(
            '/api/reset',
            data=json.dumps({'session_id': 'reset-test'}),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

    def test_reset_nonexistent_session(self, client):
        """Test resetting a session that doesn't exist."""
        response = client.post(
            '/api/reset',
            data=json.dumps({'session_id': 'nonexistent'}),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
