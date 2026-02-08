"""
NomadAI Voice Agent - Skills System
"""

from typing import Dict, Any, List, Protocol


class Skill(Protocol):
    """Base protocol for all skills."""

    name: str
    description: str
    example_utterances: List[str]

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the skill with given context."""
        ...


def get_all_skills() -> List[Any]:
    """Get all registered skills."""
    from .concierge import (
        RoomServiceSkill,
        HousekeepingSkill,
        AmenitiesSkill,
        WifiSkill,
    )
    from .sightseeing import (
        RecommendationSkill,
        ItinerarySkill,
        DirectionsSkill,
    )
    from .media import (
        ImagePreviewSkill,
        VideoTourSkill,
    )

    return [
        RoomServiceSkill(),
        HousekeepingSkill(),
        AmenitiesSkill(),
        WifiSkill(),
        RecommendationSkill(),
        ItinerarySkill(),
        DirectionsSkill(),
        ImagePreviewSkill(),
        VideoTourSkill(),
    ]
