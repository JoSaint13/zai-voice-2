"""
Sightseeing Expert Skills
Handles local recommendations, itinerary planning, and directions.
"""

import os
from typing import Dict, Any, List
from zhipuai import ZhipuAI


class RecommendationSkill:
    """Provide local place recommendations."""

    name = "local_recommendations"
    description = "Suggest local restaurants, attractions, and points of interest"
    example_utterances = [
        "Where's good ramen nearby?",
        "Recommend a local restaurant",
        "What should I see in the area?",
        "Where can I get authentic food?",
        "Best coffee shop nearby?",
    ]

    def __init__(self):
        api_key = os.getenv("ZHIPUAI_API_KEY")
        if not api_key:
            raise ValueError("ZHIPUAI_API_KEY environment variable is required")
        self.client = ZhipuAI(api_key=api_key)

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provide local recommendations.

        Args:
            context: Contains 'transcription', 'session_id', 'location', etc.

        Returns:
            Dict with 'response', 'action', and 'metadata'
        """
        transcription = context.get("transcription", "")
        session_id = context.get("session_id", "default")
        location = context.get("location", "the area")

        # In production, this would use RAG with local knowledge base
        local_kb = """
        Popular Local Spots:
        - Ramen: Ichiran (5 min walk), Ippudo (10 min walk)
        - Sushi: Sushi Dai (15 min), Tsukiji Market
        - Coffee: Blue Bottle (3 min), Starbucks Reserve (8 min)
        - Attractions: Temple nearby (10 min), Museum (15 min)
        - Shopping: Local market (5 min), Mall (20 min)
        - Parks: Central Park (7 min walk)
        """

        messages = [
            {
                "role": "system",
                "content": f"""You are a local expert and tour guide.
                Recommend authentic local places based on guest preferences.
                Be concise (2-3 sentences) and include distance/time.

                Local Knowledge Base:
                {local_kb}

                Consider: cuisine type, distance, price range, current time,
                and whether places are currently open."""
            },
            {
                "role": "user",
                "content": transcription
            }
        ]

        response = self.client.chat.completions.create(
            model="glm-4.7",
            messages=messages
        )

        assistant_message = response.choices[0].message.content

        return {
            "response": assistant_message,
            "action": "recommendations_provided",
            "metadata": {
                "skill": self.name,
                "session_id": session_id,
                "location": location,
                "recommendation_type": "local_places"
            }
        }


class ItinerarySkill:
    """Plan day trips and itineraries."""

    name = "itinerary_planning"
    description = "Create personalized day plans and itineraries"
    example_utterances = [
        "Plan my day, I have 4 hours",
        "What should I do today?",
        "Create an itinerary for tomorrow",
        "I have half a day free, what to do?",
        "Plan a walking tour for me",
    ]

    def __init__(self):
        api_key = os.getenv("ZHIPUAI_API_KEY")
        if not api_key:
            raise ValueError("ZHIPUAI_API_KEY environment variable is required")
        self.client = ZhipuAI(api_key=api_key)

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create personalized itinerary.

        Args:
            context: Contains 'transcription', 'session_id', 'preferences', etc.

        Returns:
            Dict with 'response', 'action', and 'metadata'
        """
        transcription = context.get("transcription", "")
        session_id = context.get("session_id", "default")

        # In production, use RAG + route optimization
        itinerary_kb = """
        Popular Routes:
        4-hour cultural tour: Temple (1h) → Museum (1.5h) → Local lunch (1h) → Market (30min)
        Half-day food tour: Breakfast spot → Coffee → Market tour → Lunch
        Walking tour: Park → Historic district → Shopping street → Cafe
        Family-friendly: Aquarium (2h) → Park (1h) → Kids restaurant
        """

        messages = [
            {
                "role": "system",
                "content": f"""You are a professional tour planner.
                Create optimized itineraries based on time available and preferences.
                Be concise but specific with timing and locations.

                Route Templates:
                {itinerary_kb}

                Consider: available time, interests, walking distance,
                meal times, and opening hours. Present as a bulleted list."""
            },
            {
                "role": "user",
                "content": transcription
            }
        ]

        response = self.client.chat.completions.create(
            model="glm-4.7",
            messages=messages
        )

        assistant_message = response.choices[0].message.content

        return {
            "response": assistant_message,
            "action": "itinerary_created",
            "metadata": {
                "skill": self.name,
                "session_id": session_id,
                "type": "day_plan"
            }
        }


class DirectionsSkill:
    """Provide navigation and directions."""

    name = "directions"
    description = "Help guests navigate to destinations with turn-by-turn directions"
    example_utterances = [
        "How do I get to Shibuya?",
        "Directions to the nearest subway",
        "How far is the temple?",
        "Best way to get to the airport?",
        "Walking directions to the museum",
    ]

    def __init__(self):
        api_key = os.getenv("ZHIPUAI_API_KEY")
        if not api_key:
            raise ValueError("ZHIPUAI_API_KEY environment variable is required")
        self.client = ZhipuAI(api_key=api_key)

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provide directions to destination.

        Args:
            context: Contains 'transcription', 'session_id', 'current_location', etc.

        Returns:
            Dict with 'response', 'action', and 'metadata'
        """
        transcription = context.get("transcription", "")
        session_id = context.get("session_id", "default")
        hotel_location = context.get("hotel_location", "the hotel")

        # In production, integrate with OpenStreetMap API
        directions_kb = """
        Common Destinations from Hotel:
        - Shibuya Station: 10 min walk east, or 5 min subway
        - Nearest Subway: Exit hotel, turn right, 3 min walk
        - Airport: 45 min by Narita Express train, or 60 min bus
        - Temple: 10 min walk north through park
        - Museum: 15 min walk, or 2 stops on subway line
        """

        messages = [
            {
                "role": "system",
                "content": f"""You are a navigation assistant.
                Provide clear, step-by-step directions. Be concise (2-4 sentences).

                Common Routes:
                {directions_kb}

                Include: walking time, transportation options, landmarks,
                and distance. Prefer walking for <15 min distances."""
            },
            {
                "role": "user",
                "content": transcription
            }
        ]

        response = self.client.chat.completions.create(
            model="glm-4.7",
            messages=messages
        )

        assistant_message = response.choices[0].message.content

        return {
            "response": assistant_message,
            "action": "directions_provided",
            "metadata": {
                "skill": self.name,
                "session_id": session_id,
                "from": hotel_location,
                "transport_mode": "walking"
            }
        }
