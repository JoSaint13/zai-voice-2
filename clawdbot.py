#!/usr/bin/env python3
"""
Clawdbot - Voice assistant using GLM-ASR + GLM-4.7
"""

import os
import sys
import wave
import tempfile
from pathlib import Path

import torch
import numpy as np
import soundfile as sf
from transformers import AutoModel, AutoProcessor
from zhipuai import ZhipuAI


class Clawdbot:
    def __init__(self, zhipu_api_key: str = None):
        """Initialize Clawdbot with GLM-ASR and GLM-4.7."""
        self.api_key = zhipu_api_key or os.getenv("ZHIPUAI_API_KEY")
        if not self.api_key:
            raise ValueError("ZHIPUAI_API_KEY environment variable required")

        self.glm_client = ZhipuAI(api_key=self.api_key)
        self.asr_processor = None
        self.asr_model = None
        self.conversation_history = []

    def load_asr_model(self):
        """Load GLM-ASR-Nano model (call once, lazy loading)."""
        if self.asr_model is None:
            print("Loading GLM-ASR-Nano-2512 model...")
            self.asr_processor = AutoProcessor.from_pretrained("zai-org/GLM-ASR-Nano-2512")
            self.asr_model = AutoModel.from_pretrained(
                "zai-org/GLM-ASR-Nano-2512",
                torch_dtype=torch.bfloat16,
                device_map="auto"
            )
            print("ASR model loaded!")

    def transcribe(self, audio_path: str) -> str:
        """Transcribe audio file to text using GLM-ASR."""
        self.load_asr_model()

        messages = [{
            "role": "user",
            "content": [
                {"type": "audio", "url": audio_path},
                {"type": "text", "text": "Transcribe this audio into text"}
            ]
        }]

        inputs = self.asr_processor.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(self.asr_model.device)

        outputs = self.asr_model.generate(**inputs, max_new_tokens=512, do_sample=False)
        transcription = self.asr_processor.batch_decode(
            outputs[:, inputs.input_ids.shape[1]:],
            skip_special_tokens=True
        )[0]

        return transcription.strip()

    def transcribe_cloud(self, audio_path: str) -> str:
        """Transcribe using GLM-ASR-2512 cloud API (no local GPU needed)."""
        with open(audio_path, "rb") as f:
            response = self.glm_client.audio.transcriptions.create(
                model="glm-asr-2512",
                file=f
            )
        return response.text

    def chat(self, user_message: str, system_prompt: str = None) -> str:
        """Send message to GLM-4.7 and get response."""
        if system_prompt and not self.conversation_history:
            self.conversation_history.append({
                "role": "system",
                "content": system_prompt
            })

        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        response = self.glm_client.chat.completions.create(
            model="glm-4.7",
            messages=self.conversation_history
        )

        assistant_message = response.choices[0].message.content
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        return assistant_message

    def voice_chat(self, audio_path: str, use_cloud_asr: bool = False) -> str:
        """Complete voice chat: transcribe audio then respond with GLM-4.7."""
        # Transcribe
        if use_cloud_asr:
            transcription = self.transcribe_cloud(audio_path)
        else:
            transcription = self.transcribe(audio_path)

        print(f"You said: {transcription}")

        # Get response from GLM-4.7
        response = self.chat(transcription)

        return response

    def reset_conversation(self):
        """Clear conversation history."""
        self.conversation_history = []


def record_audio(duration: float = 5.0, sample_rate: int = 16000) -> str:
    """Record audio from microphone and save to temp file."""
    import pyaudio

    p = pyaudio.PyAudio()

    print(f"Recording for {duration} seconds... Speak now!")

    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=sample_rate,
        input=True,
        frames_per_buffer=1024
    )

    frames = []
    for _ in range(int(sample_rate / 1024 * duration)):
        data = stream.read(1024)
        frames.append(data)

    print("Recording finished!")

    stream.stop_stream()
    stream.close()
    p.terminate()

    # Save to temp file
    temp_file = tempfile.mktemp(suffix=".wav")
    with wave.open(temp_file, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))

    return temp_file


def main():
    """Interactive voice chat demo."""
    print("=" * 50)
    print("Clawdbot - GLM-ASR + GLM-4.7 Voice Assistant")
    print("=" * 50)

    # Check for API key
    if not os.getenv("ZHIPUAI_API_KEY"):
        print("\nError: Set ZHIPUAI_API_KEY environment variable first:")
        print("  export ZHIPUAI_API_KEY='your_api_key_here'")
        sys.exit(1)

    bot = Clawdbot()

    system_prompt = """You are Clawdbot, a helpful voice assistant.
    Keep responses concise and conversational since they will be spoken aloud.
    Be friendly and helpful."""

    print("\nCommands:")
    print("  'r' or 'record' - Record audio from microphone")
    print("  'f <path>'      - Transcribe audio file")
    print("  't <text>'      - Text chat (skip voice)")
    print("  'c' or 'cloud'  - Toggle cloud ASR (default: local)")
    print("  'q' or 'quit'   - Exit")
    print()

    use_cloud = False

    while True:
        try:
            cmd = input("\n> ").strip()

            if not cmd:
                continue

            if cmd.lower() in ('q', 'quit', 'exit'):
                print("Goodbye!")
                break

            if cmd.lower() in ('c', 'cloud'):
                use_cloud = not use_cloud
                mode = "Cloud (GLM-ASR-2512)" if use_cloud else "Local (GLM-ASR-Nano)"
                print(f"ASR mode: {mode}")
                continue

            if cmd.lower() in ('r', 'record'):
                audio_path = record_audio(duration=5.0)
                response = bot.voice_chat(audio_path, use_cloud_asr=use_cloud)
                print(f"\nClawdbot: {response}")
                os.unlink(audio_path)  # Clean up temp file
                continue

            if cmd.lower().startswith('f '):
                audio_path = cmd[2:].strip()
                if not Path(audio_path).exists():
                    print(f"File not found: {audio_path}")
                    continue
                response = bot.voice_chat(audio_path, use_cloud_asr=use_cloud)
                print(f"\nClawdbot: {response}")
                continue

            if cmd.lower().startswith('t '):
                text = cmd[2:].strip()
                response = bot.chat(text, system_prompt=system_prompt)
                print(f"\nClawdbot: {response}")
                continue

            # Default: treat as text input
            response = bot.chat(cmd, system_prompt=system_prompt)
            print(f"\nClawdbot: {response}")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
