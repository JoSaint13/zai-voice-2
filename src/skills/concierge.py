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


class CheckOutSkill:
    """Handle guest checkout process."""

    name = "check_out"
    description = "Assist with hotel checkout process and final billing"
    example_utterances = [
        "I'd like to check out",
        "Can I check out now?",
        "I'm ready to leave",
        "Process my checkout",
        "I want to settle my bill",
    ]

    def __init__(self):
        pass

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        transcription = context.get("transcription", "")
        session_id = context.get("session_id", "default")

        messages = [
            {
                "role": "system",
                "content": """You are a hotel front desk checkout assistant.
                Help guests with checkout process. Be concise (2-3 sentences).
                
                Checkout Process:
                1. Confirm room number
                2. Review final bill (room rate + any charges)
                3. Payment method (card on file or new payment)
                4. Return key card
                5. Late checkout available until 2 PM ($50 fee)
                
                Standard checkout time: 11:00 AM
                Express checkout: Available via app or phone"""
            },
            {"role": "user", "content": transcription}
        ]

        assistant_message = skill_chat(messages)

        return {
            "response": assistant_message,
            "action": "checkout_initiated",
            "metadata": {
                "skill": self.name,
                "session_id": session_id,
                "checkout_type": "standard"
            }
        }


class ComplaintsSkill:
    """Handle guest complaints and service recovery."""

    name = "complaints"
    description = "Log and acknowledge guest complaints or issues"
    example_utterances = [
        "I have a complaint",
        "The room is too noisy",
        "My AC isn't working",
        "I'm not happy with the service",
        "There's a problem with my room",
    ]

    def __init__(self):
        pass

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        transcription = context.get("transcription", "")
        session_id = context.get("session_id", "default")

        messages = [
            {
                "role": "system",
                "content": """You are a hotel guest relations manager.
                Handle complaints with empathy and urgency. Be concise (2-3 sentences).
                
                Response Protocol:
                1. Acknowledge and apologize
                2. Clarify the issue
                3. Offer immediate solution or escalation
                4. Provide timeline for resolution
                
                Common Solutions:
                - Room issues → Offer room change or immediate maintenance
                - Noise → Move to quieter floor
                - Service issues → Manager follow-up within 30 min
                - Billing disputes → Front desk review
                
                Always thank them for bringing it to our attention."""
            },
            {"role": "user", "content": transcription}
        ]

        assistant_message = skill_chat(messages)

        return {
            "response": assistant_message,
            "action": "complaint_logged",
            "metadata": {
                "skill": self.name,
                "session_id": session_id,
                "priority": "high",
                "requires_followup": True
            }
        }


class WakeUpCallSkill:
    """Schedule wake-up calls for guests."""

    name = "wake_up_call"
    description = "Schedule morning wake-up calls"
    example_utterances = [
        "Set a wake-up call for 7 AM",
        "I need a morning call",
        "Wake me up at 6:30",
        "Schedule an alarm for tomorrow",
        "Can you call my room at 8 AM?",
    ]

    def __init__(self):
        pass

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        transcription = context.get("transcription", "")
        session_id = context.get("session_id", "default")

        messages = [
            {
                "role": "system",
                "content": """You are a hotel wake-up call coordinator.
                Schedule wake-up calls for guests. Be concise (2-3 sentences).
                
                Process:
                1. Confirm time (use 12-hour or 24-hour format)
                2. Confirm room number
                3. Confirm date (today/tomorrow)
                4. Set reminder
                
                Wake-up Call Features:
                - Available 5:00 AM to 11:00 AM
                - Can schedule up to 7 days in advance
                - Automated call with option to snooze (10 min)
                - Confirm time in guest's timezone
                
                Always repeat back the confirmed time."""
            },
            {"role": "user", "content": transcription}
        ]

        assistant_message = skill_chat(messages)

        return {
            "response": assistant_message,
            "action": "wake_up_call_scheduled",
            "metadata": {
                "skill": self.name,
                "session_id": session_id,
                "scheduled_time": "extracted_from_transcription"
            }
        }


class BillingInquirySkill:
    """Provide billing and folio information."""

    name = "billing_inquiry"
    description = "Answer questions about guest bill and charges"
    example_utterances = [
        "What's my current bill?",
        "How much do I owe?",
        "Show me my charges",
        "What are these charges for?",
        "Can I see my folio?",
    ]

    def __init__(self):
        pass

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        transcription = context.get("transcription", "")
        session_id = context.get("session_id", "default")

        mock_folio = """
        Sample Charges:
        - Room Rate: $150/night × 2 nights = $300
        - Room Service: $45
        - Minibar: $18
        - Parking: $25/day × 2 = $50
        - Tax (12%): $49.56
        Total: $462.56
        """

        messages = [
            {
                "role": "system",
                "content": f"""You are a hotel billing assistant.
                Answer billing questions clearly. Be concise (2-3 sentences).
                
                Mock Folio Data:
                {mock_folio}
                
                Billing Information:
                - All charges posted within 24 hours
                - Minibar charges at checkout
                - Disputes: Contact front desk
                - Payment: Card on file or at checkout
                - Detailed invoice available via email
                
                Always offer to send detailed breakdown to guest's email."""
            },
            {"role": "user", "content": transcription}
        ]

        assistant_message = skill_chat(messages)

        return {
            "response": assistant_message,
            "action": "billing_info_provided",
            "metadata": {
                "skill": self.name,
                "session_id": session_id,
                "total_charges": 462.56
            }
        }
