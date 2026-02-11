"""
Media Generation Skills
Handles image and video generation for destination previews.
Uses Chutes.ai via shared chat_provider.
Note: Image/video generation is not available via Chutes; we return rich text descriptions instead.
"""

import os
from typing import Dict, Any, List
from src.skills.chat_provider import skill_chat


class ImagePreviewSkill:
    """Generate destination preview descriptions (image generation not available)."""

    name = "image_preview"
    description = "Describe destinations and attractions visually"
    example_utterances = [
        "Show me what Kyoto looks like",
        "Generate an image of the temple",
        "What does the beach look like?",
        "Show me a picture of that restaurant",
        "Create an image of the local market",
    ]

    def __init__(self):
        pass

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        transcription = context.get("transcription", "")
        session_id = context.get("session_id", "default")

        messages = [
            {
                "role": "system",
                "content": """You are a vivid travel describer.
                The user wants to see what a place looks like. Since image generation is not available,
                provide a rich, detailed visual description of the place (3-5 sentences).
                Include colors, atmosphere, architecture, and what makes it special.
                End with a helpful tip about visiting."""
            },
            {"role": "user", "content": transcription}
        ]

        assistant_message = skill_chat(messages)

        return {
            "response": assistant_message,
            "action": "description_provided",
            "metadata": {
                "skill": self.name,
                "session_id": session_id,
                "note": "Image generation not available - text description provided"
            }
        }


class VideoTourSkill:
    """Generate tour descriptions (video generation not available)."""

    name = "video_tour"
    description = "Describe personalized tour routes and virtual tours"
    example_utterances = [
        "Create a video of my walking route",
        "Show me a video tour of the city",
        "Generate a video of the scenic route",
        "Make a video preview of my itinerary",
        "Can you create a virtual tour?",
    ]

    def __init__(self):
        pass

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        transcription = context.get("transcription", "")
        session_id = context.get("session_id", "default")

        messages = [
            {
                "role": "system",
                "content": """You are a virtual tour narrator.
                The user wants a video tour. Since video generation is not available,
                narrate a vivid walking tour (4-6 sentences) as if guiding them through the scene.
                Describe what they would see, hear, and feel along the route.
                Include landmarks, atmosphere, and local details."""
            },
            {"role": "user", "content": transcription}
        ]

        assistant_message = skill_chat(messages)

        return {
            "response": assistant_message,
            "action": "tour_narration_provided",
            "metadata": {
                "skill": self.name,
                "session_id": session_id,
                "note": "Video generation not available - narrated tour provided"
            }
        }


async def check_video_status(task_id: str) -> Dict[str, Any]:
    """Check the status of a video generation task (legacy - returns unavailable)."""
    return {
        "status": "unavailable",
        "message": "Video generation is not currently available."
    }
