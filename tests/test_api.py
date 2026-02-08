"""
Tests for Clawdbot Flask API endpoints.

Tests cover:
- Chat endpoint functionality
- Transcription endpoint with audio handling
- Voice-chat endpoint combining both operations
- Session management
"""

import json
import base64
import os
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Mock the ZhipuAI import before importing app
sys.modules['zhipuai'] = MagicMock()


@pytest.fixture
def mock_zhipu_client():
    """Mock ZhipuAI client."""
    with patch('api.index.client') as mock_client:
        yield mock_client


@pytest.fixture
def mock_env_var(monkeypatch):
    """Set mock API key environment variable."""
    monkeypatch.setenv('ZHIPUAI_API_KEY', 'test-api-key-12345')


@pytest.fixture
def app():
    """Create Flask app for testing."""
    # Clear any existing app
    if 'api.index' in sys.modules:
        del sys.modules['api.index']

    with patch.dict(os.environ, {'ZHIPUAI_API_KEY': 'test-api-key'}):
        from api.index import app as flask_app
        flask_app.config['TESTING'] = True
        return flask_app


@pytest.fixture
def client(app):
    """Create Flask test client."""
    return app.test_client()


class TestChatEndpoint:
    """Test suite for /api/chat endpoint."""

    def test_chat_endpoint_success(self, client, monkeypatch):
        """Test successful chat request."""
        # Mock the ZhipuAI chat response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Hello! How can I help you today?"))]

        with patch('api.index.client') as mock_client:
            mock_client.chat.completions.create.return_value = mock_response

            response = client.post(
                '/api/chat',
                data=json.dumps({'message': 'Hello, Clawdbot!'}),
                content_type='application/json'
            )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'response' in data
        assert data['response'] == "Hello! How can I help you today?"

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
        assert 'message required' in data['error']

    def test_chat_with_session_id(self, client):
        """Test chat with custom session ID."""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Session test response"))]

        with patch('api.index.client') as mock_client:
            mock_client.chat.completions.create.return_value = mock_response

            response = client.post(
                '/api/chat',
                data=json.dumps({
                    'message': 'Test message',
                    'session_id': 'user-session-1'
                }),
                content_type='application/json'
            )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

    def test_chat_api_error_handling(self, client):
        """Test chat endpoint handles API errors gracefully."""
        with patch('api.index.client') as mock_client:
            mock_client.chat.completions.create.side_effect = Exception("API Error")

            response = client.post(
                '/api/chat',
                data=json.dumps({'message': 'Test'}),
                content_type='application/json'
            )

        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data


class TestTranscriptionEndpoint:
    """Test suite for /api/transcribe endpoint."""

    def test_transcribe_success(self, client):
        """Test successful audio transcription."""
        # Create dummy audio data (base64 encoded)
        audio_data = b'dummy_audio_data_wav_format'
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')

        mock_response = Mock()
        mock_response.text = "Hello, this is a test transcription"

        with patch('api.index.client') as mock_client:
            mock_client.audio.transcriptions.create.return_value = mock_response

            response = client.post(
                '/api/transcribe',
                data=json.dumps({'audio_base64': audio_base64}),
                content_type='application/json'
            )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['text'] == "Hello, this is a test transcription"

    def test_transcribe_missing_audio(self, client):
        """Test transcription request without audio_base64."""
        response = client.post(
            '/api/transcribe',
            data=json.dumps({}),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'audio_base64 required' in data['error']

    def test_transcribe_invalid_base64(self, client):
        """Test transcription with invalid base64 data."""
        with patch('api.index.client'):
            response = client.post(
                '/api/transcribe',
                data=json.dumps({'audio_base64': 'not-valid-base64!!!'}),
                content_type='application/json'
            )

        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] is False

    def test_transcribe_api_error(self, client):
        """Test transcription API error handling."""
        audio_base64 = base64.b64encode(b'test_audio').decode('utf-8')

        with patch('api.index.client') as mock_client:
            mock_client.audio.transcriptions.create.side_effect = Exception("Transcription API Error")

            response = client.post(
                '/api/transcribe',
                data=json.dumps({'audio_base64': audio_base64}),
                content_type='application/json'
            )

        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] is False


class TestVoiceChatEndpoint:
    """Test suite for /api/voice-chat endpoint combining transcription and chat."""

    def test_voice_chat_success(self, client):
        """Test successful voice chat (transcription + response)."""
        audio_base64 = base64.b64encode(b'dummy_audio').decode('utf-8')

        # Mock both transcription and chat responses
        mock_asr_response = Mock()
        mock_asr_response.text = "What time is it?"

        mock_chat_response = Mock()
        mock_chat_response.choices = [Mock(message=Mock(content="It is currently 3 PM"))]

        with patch('api.index.client') as mock_client:
            mock_client.audio.transcriptions.create.return_value = mock_asr_response
            mock_client.chat.completions.create.return_value = mock_chat_response

            response = client.post(
                '/api/voice-chat',
                data=json.dumps({'audio_base64': audio_base64}),
                content_type='application/json'
            )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['transcription'] == "What time is it?"
        assert data['response'] == "It is currently 3 PM"

    def test_voice_chat_missing_audio(self, client):
        """Test voice chat without audio_base64."""
        response = client.post(
            '/api/voice-chat',
            data=json.dumps({}),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'audio_base64 required' in data['error']

    def test_voice_chat_with_session(self, client):
        """Test voice chat maintains session context."""
        audio_base64 = base64.b64encode(b'audio_data').decode('utf-8')

        mock_asr_response = Mock()
        mock_asr_response.text = "Hello"

        mock_chat_response = Mock()
        mock_chat_response.choices = [Mock(message=Mock(content="Hi there!"))]

        with patch('api.index.client') as mock_client:
            mock_client.audio.transcriptions.create.return_value = mock_asr_response
            mock_client.chat.completions.create.return_value = mock_chat_response

            response = client.post(
                '/api/voice-chat',
                data=json.dumps({
                    'audio_base64': audio_base64,
                    'session_id': 'test-session-1'
                }),
                content_type='application/json'
            )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

    def test_voice_chat_transcription_error(self, client):
        """Test voice chat handles transcription errors."""
        audio_base64 = base64.b64encode(b'bad_audio').decode('utf-8')

        with patch('api.index.client') as mock_client:
            mock_client.audio.transcriptions.create.side_effect = Exception("ASR Error")

            response = client.post(
                '/api/voice-chat',
                data=json.dumps({'audio_base64': audio_base64}),
                content_type='application/json'
            )

        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] is False


class TestSessionManagement:
    """Test suite for conversation session management."""

    def test_session_isolation(self, client):
        """Test that different sessions maintain separate conversations."""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Response 1"))]

        with patch('api.index.client') as mock_client:
            mock_client.chat.completions.create.return_value = mock_response

            # Message in session 1
            client.post(
                '/api/chat',
                data=json.dumps({
                    'message': 'Message 1',
                    'session_id': 'session-1'
                }),
                content_type='application/json'
            )

            # Message in session 2
            client.post(
                '/api/chat',
                data=json.dumps({
                    'message': 'Message 2',
                    'session_id': 'session-2'
                }),
                content_type='application/json'
            )

        # Both should succeed without interference
        assert response.status_code == 200

    def test_reset_conversation(self, client):
        """Test resetting conversation history for a session."""
        with patch('api.index.client') as mock_client:
            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content="Test"))]
            mock_client.chat.completions.create.return_value = mock_response

            # Create a conversation
            client.post(
                '/api/chat',
                data=json.dumps({
                    'message': 'Hello',
                    'session_id': 'reset-test'
                }),
                content_type='application/json'
            )

            # Reset it
            response = client.post(
                '/api/reset',
                data=json.dumps({'session_id': 'reset-test'}),
                content_type='application/json'
            )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'message' in data

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


class TestHomeEndpoint:
    """Test suite for health check endpoint."""

    def test_home_endpoint(self, client):
        """Test home endpoint returns status."""
        response = client.get('/')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'ok'
        assert 'message' in data


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
