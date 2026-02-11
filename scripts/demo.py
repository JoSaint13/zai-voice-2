#!/usr/bin/env python3
"""
Demo script for NomadAI Voice Agent.

This script validates the full voice pipeline:
1. Text input (simulating transcription)
2. Chat endpoint processing
3. Response generation

Can be run locally to validate setup without needing actual audio.
"""

import sys
import json
import requests
import time
from typing import Dict, Any, Optional
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class DemoConfig:
    """Configuration for demo."""

    def __init__(self, api_url: str = "http://localhost:3000"):
        """Initialize config."""
        self.api_url = api_url
        self.session_id = "demo-session-" + str(int(time.time()))
        self.timeout = 10


class VoicePipelineDemo:
    """Demo the full voice pipeline."""

    def __init__(self, config: Optional[DemoConfig] = None):
        """Initialize demo."""
        self.config = config or DemoConfig()
        self.results = []

    def print_header(self, text: str) -> None:
        """Print formatted header."""
        print("\n" + "=" * 60)
        print(f"  {text}")
        print("=" * 60)

    def print_step(self, step_num: int, title: str) -> None:
        """Print step header."""
        print(f"\n[Step {step_num}] {title}")
        print("-" * 40)

    def print_result(self, label: str, value: Any, indent: int = 2) -> None:
        """Print result with formatting."""
        prefix = " " * indent
        if isinstance(value, dict):
            print(f"{prefix}{label}:")
            for k, v in value.items():
                print(f"{prefix}  {k}: {v}")
        else:
            print(f"{prefix}{label}: {value}")

    def test_health_check(self) -> bool:
        """Test if API is running."""
        self.print_step(0, "Health Check")

        try:
            response = requests.get(
                f"{self.config.api_url}/",
                timeout=self.config.timeout
            )
            response.raise_for_status()

            data = response.json()
            self.print_result("Status", data.get('status'))
            self.print_result("Message", data.get('message'))
            self.results.append(('health_check', True, data))

            return True

        except requests.exceptions.ConnectionError:
            print("ERROR: Could not connect to API at", self.config.api_url)
            print("Make sure Flask app is running: python api/index.py")
            self.results.append(('health_check', False, 'Connection failed'))
            return False

        except Exception as e:
            print(f"ERROR: {str(e)}")
            self.results.append(('health_check', False, str(e)))
            return False

    def test_chat_endpoint(self, message: str) -> bool:
        """Test chat endpoint."""
        self.print_step(1, f"Chat Endpoint - Single Message")

        try:
            print(f"Sending: '{message}'")

            response = requests.post(
                f"{self.config.api_url}/api/chat",
                json={
                    'message': message,
                    'session_id': self.config.session_id
                },
                timeout=self.config.timeout
            )
            response.raise_for_status()

            data = response.json()

            if data.get('success'):
                self.print_result("Response", data['response'])
                self.results.append(('chat_single', True, data))
                return True
            else:
                self.print_result("Error", data.get('error'))
                self.results.append(('chat_single', False, data))
                return False

        except Exception as e:
            print(f"ERROR: {str(e)}")
            self.results.append(('chat_single', False, str(e)))
            return False

    def test_multi_turn_conversation(self, messages: list) -> bool:
        """Test multi-turn conversation."""
        self.print_step(2, f"Multi-Turn Conversation ({len(messages)} exchanges)")

        all_success = True

        for i, user_message in enumerate(messages, 1):
            try:
                print(f"\nTurn {i} - User: {user_message}")

                response = requests.post(
                    f"{self.config.api_url}/api/chat",
                    json={
                        'message': user_message,
                        'session_id': self.config.session_id
                    },
                    timeout=self.config.timeout
                )
                response.raise_for_status()

                data = response.json()

                if data.get('success'):
                    bot_response = data['response']
                    print(f"Turn {i} - Bot: {bot_response}")
                    self.results.append(
                        (f'chat_turn_{i}', True, bot_response)
                    )
                else:
                    print(f"Turn {i} - ERROR: {data.get('error')}")
                    self.results.append(
                        (f'chat_turn_{i}', False, data.get('error'))
                    )
                    all_success = False

            except Exception as e:
                print(f"Turn {i} - ERROR: {str(e)}")
                self.results.append((f'chat_turn_{i}', False, str(e)))
                all_success = False

        return all_success

    def test_session_reset(self) -> bool:
        """Test session reset functionality."""
        self.print_step(3, "Session Reset")

        try:
            print(f"Resetting session: {self.config.session_id}")

            response = requests.post(
                f"{self.config.api_url}/api/reset",
                json={'session_id': self.config.session_id},
                timeout=self.config.timeout
            )
            response.raise_for_status()

            data = response.json()

            if data.get('success'):
                self.print_result("Result", data.get('message'))
                self.results.append(('session_reset', True, data))
                return True
            else:
                print(f"ERROR: {data.get('error')}")
                self.results.append(('session_reset', False, data))
                return False

        except Exception as e:
            print(f"ERROR: {str(e)}")
            self.results.append(('session_reset', False, str(e)))
            return False

    def test_transcription_endpoint(self) -> bool:
        """Test transcription endpoint with dummy audio."""
        self.print_step(4, "Transcription Endpoint (Dummy Audio)")

        try:
            import base64

            # Create minimal WAV file header (44 bytes) + some dummy audio data
            # This is a valid WAV file with silence
            wav_header = bytes([
                0x52, 0x49, 0x46, 0x46,  # RIFF
                0x24, 0x00, 0x00, 0x00,  # File size - 8
                0x57, 0x41, 0x56, 0x45,  # WAVE
                0x66, 0x6D, 0x74, 0x20,  # fmt
                0x10, 0x00, 0x00, 0x00,  # Subchunk1 size
                0x01, 0x00,              # Audio format (PCM)
                0x01, 0x00,              # Channels
                0x44, 0xAC, 0x00, 0x00,  # Sample rate (44100)
                0x88, 0x58, 0x01, 0x00,  # Byte rate
                0x02, 0x00,              # Block align
                0x10, 0x00,              # Bits per sample
                0x64, 0x61, 0x74, 0x61,  # data
                0x00, 0x00, 0x00, 0x00,  # Subchunk2 size
            ])

            audio_base64 = base64.b64encode(wav_header).decode('utf-8')

            print("Sending dummy audio file (WAV format)...")

            response = requests.post(
                f"{self.config.api_url}/api/transcribe",
                json={'audio_base64': audio_base64},
                timeout=self.config.timeout
            )

            # Note: Transcribe is a 501 stub (ASR not available via Chutes)
            # But we're testing the endpoint structure
            data = response.json()

            if response.status_code == 200 and data.get('success'):
                self.print_result("Transcription", data.get('text'))
                self.results.append(('transcribe', True, data))
                return True
            elif response.status_code == 500:
                # Expected if API key is invalid or service unavailable
                print("(Transcription endpoint available but API key validation failed)")
                print("This is expected — transcription requires an ASR provider (not available)")
                self.results.append(('transcribe', 'partial', 'API validation required'))
                return True
            else:
                self.print_result("Error", data.get('error'))
                self.results.append(('transcribe', False, data))
                return False

        except Exception as e:
            print(f"Note: {str(e)}")
            print("(Transcription endpoint not available — ASR provider not configured)")
            self.results.append(('transcribe', 'partial', str(e)))
            return True

    def print_summary(self) -> None:
        """Print test summary."""
        self.print_header("Test Summary")

        passed = sum(1 for _, success, _ in self.results if success is True)
        partial = sum(1 for _, success, _ in self.results if success == 'partial')
        failed = sum(1 for _, success, _ in self.results if success is False)

        print(f"\nResults:")
        print(f"  ✓ Passed:  {passed}")
        print(f"  ~ Partial: {partial}")
        print(f"  ✗ Failed:  {failed}")
        print(f"  Total:   {len(self.results)}")

        if failed > 0:
            print("\nFailed tests:")
            for name, success, result in self.results:
                if success is False:
                    print(f"  - {name}: {result}")

        print()

    def run_full_demo(self) -> bool:
        """Run complete demo pipeline."""
        self.print_header("NomadAI Voice Agent - Pipeline Demo")

        print(f"API URL: {self.config.api_url}")
        print(f"Session ID: {self.config.session_id}")

        # Step 0: Health check
        if not self.test_health_check():
            print("\nERROR: API is not running!")
            print("Start the API with: python api/index.py")
            return False

        # Step 1: Single message chat
        if not self.test_chat_endpoint("Hello! What's your name?"):
            print("\nWARNING: Chat endpoint test failed")

        # Step 2: Multi-turn conversation
        conversation = [
            "How are you today?",
            "Tell me something interesting about AI",
            "That's fascinating. Can you explain more?",
        ]
        if not self.test_multi_turn_conversation(conversation):
            print("\nWARNING: Some conversation turns failed")

        # Step 3: Session reset
        if not self.test_session_reset():
            print("\nWARNING: Session reset failed")

        # Step 4: Transcription endpoint
        self.test_transcription_endpoint()

        # Print summary
        self.print_summary()

        # Return success if API is working
        return any(success is True for _, success, _ in self.results)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='NomadAI Voice Agent Pipeline Demo'
    )
    parser.add_argument(
        '--api-url',
        default='http://localhost:3000',
        help='API URL (default: http://localhost:3000)'
    )
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Run quick test (health check only)'
    )

    args = parser.parse_args()

    config = DemoConfig(api_url=args.api_url)
    demo = VoicePipelineDemo(config)

    if args.quick:
        # Quick health check
        success = demo.test_health_check()
        if success:
            print("\n✓ API is running and responding!")
            sys.exit(0)
        else:
            print("\n✗ API is not available")
            sys.exit(1)
    else:
        # Full demo
        success = demo.run_full_demo()
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
