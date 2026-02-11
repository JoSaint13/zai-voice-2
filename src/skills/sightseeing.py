"""
Sightseeing Expert Skills
Handles local recommendations, itinerary planning, and directions.
Uses Chutes.ai via shared chat_provider.
"""

import os
from typing import Dict, Any, List
from src.skills.chat_provider import skill_chat


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
        pass

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        transcription = context.get("transcription", "")
        session_id = context.get("session_id", "default")
        location = context.get("location", "the area")

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
            {"role": "user", "content": transcription}
        ]

        assistant_message = skill_chat(messages)

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
        pass

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        transcription = context.get("transcription", "")
        session_id = context.get("session_id", "default")

        itinerary_kb = """
        Popular Routes:
        4-hour cultural tour: Temple (1h) -> Museum (1.5h) -> Local lunch (1h) -> Market (30min)
        Half-day food tour: Breakfast spot -> Coffee -> Market tour -> Lunch
        Walking tour: Park -> Historic district -> Shopping street -> Cafe
        Family-friendly: Aquarium (2h) -> Park (1h) -> Kids restaurant
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
            {"role": "user", "content": transcription}
        ]

        assistant_message = skill_chat(messages)

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
        pass

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        transcription = context.get("transcription", "")
        session_id = context.get("session_id", "default")
        hotel_location = context.get("hotel_location", "the hotel")

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
            {"role": "user", "content": transcription}
        ]

        assistant_message = skill_chat(messages)

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
