"""
Hotel Concierge Skills
Handles room service, housekeeping, amenities info, and WiFi help.
Uses Chutes.ai via shared chat_provider.
"""

import os
from typing import Dict, Any, List
from src.skills.chat_provider import skill_chat


class RoomServiceSkill:
    """Handle food and beverage orders."""

    name = "room_service"
    description = "Process room service orders for food and beverages"
    example_utterances = [
        "I'd like to order breakfast",
        "Can I get room service?",
        "I want to order dinner to my room",
        "What's on the menu?",
        "I need food delivered to my room",
    ]

    def __init__(self):
        pass

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        transcription = context.get("transcription", "")
        session_id = context.get("session_id", "default")

        messages = [
            {
                "role": "system",
                "content": """You are a hotel room service assistant.
                Help guests order food and beverages. Be concise (2-3 sentences).
                Available items: Breakfast (Continental, American, Japanese),
                Lunch/Dinner (Burgers, Pasta, Local cuisine),
                Beverages (Coffee, Tea, Soft drinks, Wine).
                Always confirm the order and room number before processing."""
            },
            {"role": "user", "content": transcription}
        ]

        assistant_message = skill_chat(messages)

        return {
            "response": assistant_message,
            "action": "room_service_order",
            "metadata": {
                "skill": self.name,
                "session_id": session_id,
                "requires_confirmation": True
            }
        }


class HousekeepingSkill:
    """Handle housekeeping and cleaning requests."""

    name = "housekeeping"
    description = "Process housekeeping requests like extra towels, cleaning, etc."
    example_utterances = [
        "Can I get extra towels?",
        "I need my room cleaned",
        "Please send housekeeping",
        "I need more pillows",
        "Can you clean my room now?",
    ]

    def __init__(self):
        pass

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        transcription = context.get("transcription", "")
        session_id = context.get("session_id", "default")

        messages = [
            {
                "role": "system",
                "content": """You are a hotel housekeeping coordinator.
                Help guests with housekeeping requests. Be concise (2-3 sentences).
                Available services: Extra towels/linens, room cleaning,
                toiletries, pillows/blankets, laundry service.
                Confirm the request and provide estimated time (usually 15-30 minutes)."""
            },
            {"role": "user", "content": transcription}
        ]

        assistant_message = skill_chat(messages)

        return {
            "response": assistant_message,
            "action": "create_housekeeping_ticket",
            "metadata": {
                "skill": self.name,
                "session_id": session_id,
                "priority": "normal"
            }
        }


class AmenitiesSkill:
    """Answer questions about hotel amenities and facilities."""

    name = "amenities_info"
    description = "Provide information about hotel amenities, hours, and facilities"
    example_utterances = [
        "What time does the pool close?",
        "Do you have a gym?",
        "When is breakfast served?",
        "Is there a spa?",
        "What amenities do you have?",
    ]

    def __init__(self):
        pass

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        transcription = context.get("transcription", "")
        session_id = context.get("session_id", "default")

        amenities_kb = """
        Hotel Amenities:
        - Pool: Open 6 AM - 10 PM daily
        - Gym: 24/7 access with room key
        - Spa: 9 AM - 9 PM, booking required
        - Restaurant: Breakfast 6-10 AM, Lunch 12-3 PM, Dinner 6-10 PM
        - Bar: 5 PM - 1 AM
        - Business Center: 24/7 access
        - Concierge Desk: 7 AM - 11 PM
        - Parking: Valet and self-parking available
        """

        messages = [
            {
                "role": "system",
                "content": f"""You are a hotel information assistant.
                Provide accurate information about hotel amenities. Be concise (2-3 sentences).
                Use this knowledge base:
                {amenities_kb}
                """
            },
            {"role": "user", "content": transcription}
        ]

        assistant_message = skill_chat(messages)

        return {
            "response": assistant_message,
            "action": "info_provided",
            "metadata": {
                "skill": self.name,
                "session_id": session_id,
                "category": "amenities"
            }
        }


class WifiSkill:
    """Provide WiFi credentials and connectivity help."""

    name = "wifi_help"
    description = "Provide WiFi password and help with connectivity issues"
    example_utterances = [
        "What's the WiFi password?",
        "How do I connect to WiFi?",
        "I can't connect to the internet",
        "WiFi not working",
        "What's the network name?",
    ]

    def __init__(self):
        pass

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        transcription = context.get("transcription", "")
        session_id = context.get("session_id", "default")

        wifi_info = """
        Network Name: NomadAI-Guest
        Password: Welcome2026!

        For faster speeds, use:
        Network Name: NomadAI-Premium
        Password: (Available in your welcome packet)
        """

        messages = [
            {
                "role": "system",
                "content": f"""You are a hotel IT support assistant.
                Help guests connect to WiFi. Be concise (2-3 sentences).
                WiFi Information:
                {wifi_info}

                If they have connectivity issues, suggest: restart device,
                forget network and reconnect, or contact front desk."""
            },
            {"role": "user", "content": transcription}
        ]

        assistant_message = skill_chat(messages)

        return {
            "response": assistant_message,
            "action": "wifi_credentials_provided",
            "metadata": {
                "skill": self.name,
                "session_id": session_id,
                "network": "NomadAI-Guest"
            }
        }
