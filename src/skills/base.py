"""
Base skill module for NomadAI Voice Agent.

This module provides the abstract base class and common interfaces
for all skills in the system.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, Type, TypeVar

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Enums
# -----------------------------------------------------------------------------

class SkillCategory(str, Enum):
    """Categories of skills for intent routing."""
    CONCIERGE = "concierge"
    SIGHTSEEING = "sightseeing"
    MEDIA = "media"
    SYSTEM = "system"


class SkillState(str, Enum):
    """State machine states for multi-turn skills."""
    IDLE = "idle"
    GATHERING = "gathering"
    CONFIRMING = "confirming"
    EXECUTING = "executing"
    COMPLETE = "complete"
    ERROR = "error"


class ResponseType(str, Enum):
    """Type of response returned by a skill."""
    TEXT = "text"
    AUDIO = "audio"
    IMAGE = "image"
    VIDEO = "video"
    CARD = "card"  # Rich card with text + image
    ACTION = "action"  # Backend action confirmation


# -----------------------------------------------------------------------------
# Data Classes
# -----------------------------------------------------------------------------

@dataclass
class SkillMetadata:
    """
    Metadata that describes a skill for discovery and routing.

    Attributes:
        skill_id: Unique identifier (e.g., "CON-001")
        name: Human-readable name
        category: The skill category for routing
        description: What the skill does
        example_utterances: Training examples for intent matching
        required_entities: Entities needed to execute the skill
        optional_entities: Entities that enhance execution
        version: Semantic version of the skill
        enabled: Whether the skill is currently active
    """
    skill_id: str
    name: str
    category: SkillCategory
    description: str
    example_utterances: List[str] = field(default_factory=list)
    required_entities: List[str] = field(default_factory=list)
    optional_entities: List[str] = field(default_factory=list)
    version: str = "1.0.0"
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary for serialization."""
        return {
            "skill_id": self.skill_id,
            "name": self.name,
            "category": self.category.value,
            "description": self.description,
            "example_utterances": self.example_utterances,
            "required_entities": self.required_entities,
            "optional_entities": self.optional_entities,
            "version": self.version,
            "enabled": self.enabled,
        }


@dataclass
class Message:
    """A single message in the conversation history."""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationContext:
    """
    Shared context object passed between all components.

    Contains session information, conversation history, extracted entities,
    and the current state of skill execution.
    """
    session_id: str
    guest_id: Optional[str] = None
    room_number: Optional[str] = None
    language: str = "en"
    conversation_history: List[Message] = field(default_factory=list)
    entities: Dict[str, Any] = field(default_factory=dict)
    preferences: Dict[str, Any] = field(default_factory=dict)
    current_skill_id: Optional[str] = None
    skill_state: SkillState = SkillState.IDLE
    slot_values: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def add_message(self, role: str, content: str, **metadata: Any) -> None:
        """Add a message to the conversation history."""
        self.conversation_history.append(
            Message(role=role, content=content, metadata=metadata)
        )

    def get_last_user_message(self) -> Optional[str]:
        """Get the most recent user message."""
        for msg in reversed(self.conversation_history):
            if msg.role == "user":
                return msg.content
        return None

    def get_entity(self, name: str, default: Any = None) -> Any:
        """Get an entity value by name."""
        return self.entities.get(name, default)

    def set_entity(self, name: str, value: Any) -> None:
        """Set an entity value."""
        self.entities[name] = value

    def clear_skill_state(self) -> None:
        """Reset skill-related state (for new interactions)."""
        self.current_skill_id = None
        self.skill_state = SkillState.IDLE
        self.slot_values.clear()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize context to dictionary."""
        return {
            "session_id": self.session_id,
            "guest_id": self.guest_id,
            "room_number": self.room_number,
            "language": self.language,
            "entities": self.entities,
            "preferences": self.preferences,
            "current_skill_id": self.current_skill_id,
            "skill_state": self.skill_state.value,
            "slot_values": self.slot_values,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class SkillResponse:
    """
    Response returned by a skill after execution.

    Attributes:
        success: Whether the skill executed successfully
        response_type: Type of response content
        message: The text response to speak/display
        data: Additional structured data
        next_state: The state to transition to
        follow_up_prompt: Optional prompt for gathering more info
        media_url: URL to generated media (image/video)
        actions: Backend actions that were performed
        should_end_conversation: Whether to end the conversation
    """
    success: bool
    response_type: ResponseType = ResponseType.TEXT
    message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    next_state: SkillState = SkillState.COMPLETE
    follow_up_prompt: Optional[str] = None
    media_url: Optional[str] = None
    actions: List[Dict[str, Any]] = field(default_factory=list)
    should_end_conversation: bool = False

    @classmethod
    def text(cls, message: str, **kwargs: Any) -> SkillResponse:
        """Create a simple text response."""
        return cls(success=True, message=message, **kwargs)

    @classmethod
    def error(cls, message: str, **kwargs: Any) -> SkillResponse:
        """Create an error response."""
        return cls(
            success=False,
            message=message,
            next_state=SkillState.ERROR,
            **kwargs
        )

    @classmethod
    def needs_info(cls, prompt: str, **kwargs: Any) -> SkillResponse:
        """Create a response requesting more information."""
        return cls(
            success=True,
            message=prompt,
            next_state=SkillState.GATHERING,
            follow_up_prompt=prompt,
            **kwargs
        )

    @classmethod
    def confirm(cls, message: str, **kwargs: Any) -> SkillResponse:
        """Create a confirmation request response."""
        return cls(
            success=True,
            message=message,
            next_state=SkillState.CONFIRMING,
            **kwargs
        )


@dataclass
class ValidationResult:
    """Result of validating skill prerequisites."""
    is_valid: bool
    missing_entities: List[str] = field(default_factory=list)
    error_message: Optional[str] = None


# -----------------------------------------------------------------------------
# Abstract Base Class
# -----------------------------------------------------------------------------

class BaseSkill(ABC):
    """
    Abstract base class for all skills in NomadAI Voice Agent.

    All skills must inherit from this class and implement the required
    abstract methods. Skills are stateless - all state is stored in
    the ConversationContext.

    Example:
        class RoomServiceSkill(BaseSkill):
            @property
            def metadata(self) -> SkillMetadata:
                return SkillMetadata(
                    skill_id="CON-001",
                    name="Room Service",
                    category=SkillCategory.CONCIERGE,
                    description="Order food and beverages to your room",
                    example_utterances=[
                        "I'd like to order breakfast",
                        "Can I get room service?",
                        "I want to order food"
                    ],
                    required_entities=["order_items"],
                    optional_entities=["special_instructions", "delivery_time"]
                )

            async def execute(self, context: ConversationContext) -> SkillResponse:
                # Implementation here
                ...
    """

    @property
    @abstractmethod
    def metadata(self) -> SkillMetadata:
        """
        Return the skill's metadata.

        This is used for skill discovery, routing, and documentation.
        """
        ...

    @abstractmethod
    async def execute(
        self,
        context: ConversationContext
    ) -> SkillResponse:
        """
        Execute the skill with the given context.

        This is the main entry point for skill execution. The skill
        should use the context to access conversation history, entities,
        and any other required state.

        Args:
            context: The conversation context containing all relevant state

        Returns:
            SkillResponse with the result of execution
        """
        ...

    def validate(self, context: ConversationContext) -> ValidationResult:
        """
        Validate that all prerequisites are met for execution.

        Override this method to add custom validation logic.
        The default implementation checks for required entities.

        Args:
            context: The conversation context

        Returns:
            ValidationResult indicating if execution can proceed
        """
        missing = []
        for entity in self.metadata.required_entities:
            if entity not in context.entities:
                missing.append(entity)

        if missing:
            return ValidationResult(
                is_valid=False,
                missing_entities=missing,
                error_message=f"Missing required information: {', '.join(missing)}"
            )

        return ValidationResult(is_valid=True)

    async def gather_slot(
        self,
        slot_name: str,
        context: ConversationContext
    ) -> SkillResponse:
        """
        Generate a prompt to gather a missing slot value.

        Override this method to customize slot gathering prompts.

        Args:
            slot_name: The name of the slot to gather
            context: The conversation context

        Returns:
            SkillResponse with the prompt for the user
        """
        prompts = {
            # Default prompts for common slots
            "order_items": "What would you like to order?",
            "room_number": "What is your room number?",
            "time": "What time would you like that?",
            "date": "What date would you like that?",
            "location": "Where would you like to go?",
            "cuisine": "What type of food are you in the mood for?",
            "budget": "What is your budget?",
        }

        prompt = prompts.get(
            slot_name,
            f"Could you please provide the {slot_name.replace('_', ' ')}?"
        )

        return SkillResponse.needs_info(prompt)

    async def confirm_action(
        self,
        context: ConversationContext,
        action_description: str
    ) -> SkillResponse:
        """
        Request confirmation from the user before executing an action.

        Args:
            context: The conversation context
            action_description: Human-readable description of the action

        Returns:
            SkillResponse requesting confirmation
        """
        return SkillResponse.confirm(
            f"{action_description}. Should I proceed?"
        )

    def is_confirmation(self, text: str) -> Optional[bool]:
        """
        Check if the user's response is a confirmation or rejection.

        Args:
            text: The user's response text

        Returns:
            True if confirmed, False if rejected, None if unclear
        """
        text_lower = text.lower().strip()

        confirmations = {
            "yes", "yeah", "yep", "sure", "ok", "okay",
            "confirm", "correct", "right", "please", "go ahead",
            "do it", "proceed", "that's right", "absolutely"
        }

        rejections = {
            "no", "nope", "cancel", "stop", "wait",
            "don't", "never mind", "forget it", "wrong"
        }

        if any(word in text_lower for word in confirmations):
            return True
        if any(word in text_lower for word in rejections):
            return False

        return None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.metadata.skill_id}>"


# -----------------------------------------------------------------------------
# Skill Registry
# -----------------------------------------------------------------------------

SkillT = TypeVar("SkillT", bound=BaseSkill)


class SkillRegistry:
    """
    Registry for managing and discovering skills.

    The registry maintains a collection of skill instances and provides
    methods for skill lookup by ID or category.

    Example:
        registry = SkillRegistry()
        registry.register(RoomServiceSkill())
        registry.register(HousekeepingSkill())

        skill = registry.get("CON-001")
        concierge_skills = registry.list_by_category(SkillCategory.CONCIERGE)
    """

    def __init__(self) -> None:
        self._skills: Dict[str, BaseSkill] = {}
        self._by_category: Dict[SkillCategory, List[str]] = {
            category: [] for category in SkillCategory
        }

    def register(self, skill: BaseSkill) -> None:
        """
        Register a skill with the registry.

        Args:
            skill: The skill instance to register

        Raises:
            ValueError: If a skill with the same ID is already registered
        """
        skill_id = skill.metadata.skill_id

        if skill_id in self._skills:
            raise ValueError(f"Skill {skill_id} is already registered")

        self._skills[skill_id] = skill
        self._by_category[skill.metadata.category].append(skill_id)

        logger.info(
            f"Registered skill: {skill_id} ({skill.metadata.name}) "
            f"in category {skill.metadata.category.value}"
        )

    def unregister(self, skill_id: str) -> None:
        """
        Remove a skill from the registry.

        Args:
            skill_id: The ID of the skill to remove
        """
        if skill_id not in self._skills:
            return

        skill = self._skills.pop(skill_id)
        self._by_category[skill.metadata.category].remove(skill_id)

        logger.info(f"Unregistered skill: {skill_id}")

    def get(self, skill_id: str) -> Optional[BaseSkill]:
        """
        Get a skill by its ID.

        Args:
            skill_id: The skill ID to look up

        Returns:
            The skill instance or None if not found
        """
        return self._skills.get(skill_id)

    def get_or_raise(self, skill_id: str) -> BaseSkill:
        """
        Get a skill by ID, raising an error if not found.

        Args:
            skill_id: The skill ID to look up

        Returns:
            The skill instance

        Raises:
            KeyError: If the skill is not found
        """
        skill = self.get(skill_id)
        if skill is None:
            raise KeyError(f"Skill not found: {skill_id}")
        return skill

    def list_by_category(self, category: SkillCategory) -> List[BaseSkill]:
        """
        Get all skills in a category.

        Args:
            category: The category to filter by

        Returns:
            List of skill instances in the category
        """
        skill_ids = self._by_category.get(category, [])
        return [self._skills[sid] for sid in skill_ids]

    def list_all(self) -> List[BaseSkill]:
        """Get all registered skills."""
        return list(self._skills.values())

    def list_enabled(self) -> List[BaseSkill]:
        """Get all enabled skills."""
        return [s for s in self._skills.values() if s.metadata.enabled]

    def get_metadata(self) -> List[SkillMetadata]:
        """Get metadata for all registered skills."""
        return [skill.metadata for skill in self._skills.values()]

    def find_by_utterance(
        self,
        utterance: str,
        category: Optional[SkillCategory] = None
    ) -> List[tuple[BaseSkill, float]]:
        """
        Find skills that might match an utterance.

        This performs a simple keyword match against example utterances.
        For production use, this should be replaced with proper
        semantic matching using embeddings.

        Args:
            utterance: The user's utterance
            category: Optional category to filter by

        Returns:
            List of (skill, score) tuples sorted by score descending
        """
        results: List[tuple[BaseSkill, float]] = []
        utterance_lower = utterance.lower()

        skills = (
            self.list_by_category(category)
            if category
            else self.list_enabled()
        )

        for skill in skills:
            score = 0.0
            for example in skill.metadata.example_utterances:
                example_lower = example.lower()
                # Simple word overlap scoring
                utterance_words = set(utterance_lower.split())
                example_words = set(example_lower.split())
                overlap = len(utterance_words & example_words)
                if overlap > 0:
                    score = max(score, overlap / len(example_words))

            if score > 0:
                results.append((skill, score))

        return sorted(results, key=lambda x: x[1], reverse=True)

    def __len__(self) -> int:
        return len(self._skills)

    def __contains__(self, skill_id: str) -> bool:
        return skill_id in self._skills


# -----------------------------------------------------------------------------
# Protocol Definitions
# -----------------------------------------------------------------------------

class BackendService(Protocol):
    """Protocol for backend service integrations (PMS, Maps, etc.)."""

    async def call(
        self,
        method: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Make a call to the backend service."""
        ...


class AIService(Protocol):
    """Protocol for AI service calls (LLM/chat provider)."""

    async def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs: Any
    ) -> str:
        """Send a chat completion request."""
        ...

    async def generate_image(
        self,
        prompt: str,
        **kwargs: Any
    ) -> str:
        """Generate an image and return the URL."""
        ...

    async def generate_video(
        self,
        prompt: str,
        **kwargs: Any
    ) -> str:
        """Generate a video and return the URL."""
        ...


# -----------------------------------------------------------------------------
# Module Exports
# -----------------------------------------------------------------------------

__all__ = [
    # Enums
    "SkillCategory",
    "SkillState",
    "ResponseType",
    # Data Classes
    "SkillMetadata",
    "Message",
    "ConversationContext",
    "SkillResponse",
    "ValidationResult",
    # Base Class
    "BaseSkill",
    # Registry
    "SkillRegistry",
    # Protocols
    "BackendService",
    "AIService",
]
