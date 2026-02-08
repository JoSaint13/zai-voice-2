"""
Media Generation Skills
Handles image and video generation for destination previews.
"""

import os
from typing import Dict, Any, List
from zhipuai import ZhipuAI


class ImagePreviewSkill:
    """Generate destination preview images with CogView-4."""

    name = "image_preview"
    description = "Generate preview images of destinations and attractions"
    example_utterances = [
        "Show me what Kyoto looks like",
        "Generate an image of the temple",
        "What does the beach look like?",
        "Show me a picture of that restaurant",
        "Create an image of the local market",
    ]

    def __init__(self):
        api_key = os.getenv("ZHIPUAI_API_KEY")
        if not api_key:
            raise ValueError("ZHIPUAI_API_KEY environment variable is required")
        self.client = ZhipuAI(api_key=api_key)

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate destination preview image.

        Args:
            context: Contains 'transcription', 'session_id', 'destination', etc.

        Returns:
            Dict with 'response', 'image_url', and 'metadata'
        """
        transcription = context.get("transcription", "")
        session_id = context.get("session_id", "default")

        # First, use GLM-4.7 to create an optimized image prompt
        prompt_messages = [
            {
                "role": "system",
                "content": """You are an expert at creating image generation prompts.
                Convert the user's request into a detailed, vivid image prompt.
                Focus on: visual details, lighting, atmosphere, composition.
                Keep it under 100 words. Output ONLY the prompt, no explanation."""
            },
            {
                "role": "user",
                "content": transcription
            }
        ]

        prompt_response = self.client.chat.completions.create(
            model="glm-4.7",
            messages=prompt_messages
        )

        image_prompt = prompt_response.choices[0].message.content

        # Generate image with CogView-4
        try:
            image_response = self.client.images.generations(
                model="cogview-4",
                prompt=image_prompt,
                size="1024x1024",
            )

            image_url = image_response.data[0].url

            return {
                "response": f"I've generated a preview image for you. {image_prompt[:100]}...",
                "image_url": image_url,
                "action": "image_generated",
                "metadata": {
                    "skill": self.name,
                    "session_id": session_id,
                    "prompt": image_prompt,
                    "model": "cogview-4"
                }
            }

        except Exception as e:
            return {
                "response": f"I encountered an issue generating the image: {str(e)}. Let me describe it instead: {image_prompt}",
                "error": str(e),
                "action": "image_generation_failed",
                "metadata": {
                    "skill": self.name,
                    "session_id": session_id,
                    "prompt": image_prompt
                }
            }


class VideoTourSkill:
    """Generate tour videos with CogVideoX."""

    name = "video_tour"
    description = "Generate personalized tour videos of destinations and routes"
    example_utterances = [
        "Create a video of my walking route",
        "Show me a video tour of the city",
        "Generate a video of the scenic route",
        "Make a video preview of my itinerary",
        "Can you create a virtual tour?",
    ]

    def __init__(self):
        api_key = os.getenv("ZHIPUAI_API_KEY")
        if not api_key:
            raise ValueError("ZHIPUAI_API_KEY environment variable is required")
        self.client = ZhipuAI(api_key=api_key)

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate tour video.

        Args:
            context: Contains 'transcription', 'session_id', 'route', etc.

        Returns:
            Dict with 'response', 'video_url', and 'metadata'
        """
        transcription = context.get("transcription", "")
        session_id = context.get("session_id", "default")

        # First, use GLM-4.7 to create an optimized video prompt
        prompt_messages = [
            {
                "role": "system",
                "content": """You are an expert at creating video generation prompts.
                Convert the user's request into a detailed video scene description.
                Focus on: camera movement, scenery progression, atmosphere, key landmarks.
                Describe a smooth, cinematic journey. Keep it under 150 words.
                Output ONLY the prompt, no explanation."""
            },
            {
                "role": "user",
                "content": transcription
            }
        ]

        prompt_response = self.client.chat.completions.create(
            model="glm-4.7",
            messages=prompt_messages
        )

        video_prompt = prompt_response.choices[0].message.content

        # Generate video with CogVideoX
        try:
            video_response = self.client.videos.generations(
                model="cogvideox",
                prompt=video_prompt,
            )

            # The video generation is async, so we get a task ID
            task_id = video_response.id
            video_status = video_response.task_status

            return {
                "response": f"I'm generating your tour video. {video_prompt[:100]}... This will take a few moments.",
                "task_id": task_id,
                "status": video_status,
                "action": "video_generation_started",
                "metadata": {
                    "skill": self.name,
                    "session_id": session_id,
                    "prompt": video_prompt,
                    "model": "cogvideox"
                }
            }

        except Exception as e:
            return {
                "response": f"I encountered an issue generating the video: {str(e)}. Let me describe the tour instead: {video_prompt}",
                "error": str(e),
                "action": "video_generation_failed",
                "metadata": {
                    "skill": self.name,
                    "session_id": session_id,
                    "prompt": video_prompt
                }
            }


async def check_video_status(task_id: str) -> Dict[str, Any]:
    """
    Check the status of a video generation task.

    Args:
        task_id: The video generation task ID

    Returns:
        Dict with status, video_url if complete, or progress info
    """
    api_key = os.getenv("ZHIPUAI_API_KEY")
    if not api_key:
        raise ValueError("ZHIPUAI_API_KEY environment variable is required")

    client = ZhipuAI(api_key=api_key)

    try:
        result = client.videos.retrieve_videos_result(id=task_id)

        if result.task_status == "SUCCESS":
            return {
                "status": "completed",
                "video_url": result.video_result[0].url,
                "cover_image_url": result.video_result[0].cover_image_url
            }
        elif result.task_status == "PROCESSING":
            return {
                "status": "processing",
                "message": "Video is still being generated..."
            }
        else:
            return {
                "status": "failed",
                "error": "Video generation failed"
            }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
