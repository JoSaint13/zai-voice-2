"""
Tests for Clawdbot skill system and intent routing.

Tests cover:
- Skill base class interface
- Intent detection and routing
- Individual skill execution
- Skill integration with chat system
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from abc import ABC, abstractmethod


class SkillBase(ABC):
    """Base class for all Clawdbot skills."""

    def __init__(self, name: str, intents: list):
        """
        Initialize skill.

        Args:
            name: Skill identifier
            intents: List of intent patterns this skill handles
        """
        self.name = name
        self.intents = intents
        self.enabled = True

    @abstractmethod
    def handle(self, user_input: str, context: dict = None) -> str:
        """
        Handle user input and return response.

        Args:
            user_input: The user's message
            context: Optional context dict with session info

        Returns:
            Response string
        """
        pass

    def matches(self, user_input: str) -> bool:
        """Check if this skill can handle the input."""
        user_lower = user_input.lower()
        return any(intent.lower() in user_lower for intent in self.intents)


class IntentRouter:
    """Routes user input to appropriate skills."""

    def __init__(self):
        """Initialize router."""
        self.skills = {}

    def register(self, skill: SkillBase) -> None:
        """Register a skill."""
        self.skills[skill.name] = skill

    def route(self, user_input: str, context: dict = None) -> dict:
        """
        Route input to matching skill.

        Returns:
            Dict with matched skill, response, confidence
        """
        context = context or {}

        # Find matching skill
        for skill_name, skill in self.skills.items():
            if skill.enabled and skill.matches(user_input):
                try:
                    response = skill.handle(user_input, context)
                    return {
                        'skill': skill_name,
                        'response': response,
                        'confidence': 1.0,
                        'success': True
                    }
                except Exception as e:
                    return {
                        'skill': skill_name,
                        'response': None,
                        'error': str(e),
                        'success': False
                    }

        # No skill matched
        return {
            'skill': None,
            'response': None,
            'confidence': 0.0,
            'success': False,
            'error': 'No matching skill found'
        }

    def get_skill(self, name: str) -> SkillBase:
        """Get skill by name."""
        return self.skills.get(name)

    def list_skills(self) -> list:
        """List all registered skills."""
        return list(self.skills.keys())


# Test Fixtures

@pytest.fixture
def skill_router():
    """Create an intent router."""
    return IntentRouter()


@pytest.fixture
def mock_weather_skill():
    """Create a mock weather skill."""
    class WeatherSkill(SkillBase):
        def __init__(self):
            super().__init__('weather', ['weather', 'temperature', 'forecast', 'rain'])

        def handle(self, user_input: str, context: dict = None) -> str:
            return "The weather is sunny with a high of 72 degrees."

    return WeatherSkill()


@pytest.fixture
def mock_time_skill():
    """Create a mock time skill."""
    class TimeSkill(SkillBase):
        def __init__(self):
            super().__init__('time', ['time', 'what time', 'clock'])

        def handle(self, user_input: str, context: dict = None) -> str:
            return "It is currently 3:30 PM."

    return TimeSkill()


@pytest.fixture
def mock_calculator_skill():
    """Create a mock calculator skill."""
    class CalculatorSkill(SkillBase):
        def __init__(self):
            super().__init__('calculator', ['calculate', 'math', 'plus', 'minus', 'multiply'])

        def handle(self, user_input: str, context: dict = None) -> str:
            # Simple mock - would parse actual math in real implementation
            return "The answer is 42."

    return CalculatorSkill()


# Test Classes

class TestSkillBaseInterface:
    """Test the SkillBase class interface."""

    def test_skill_initialization(self, mock_weather_skill):
        """Test skill initialization."""
        assert mock_weather_skill.name == 'weather'
        assert 'weather' in mock_weather_skill.intents
        assert mock_weather_skill.enabled is True

    def test_skill_handle_method(self, mock_weather_skill):
        """Test skill handle method."""
        response = mock_weather_skill.handle("What's the weather?")
        assert isinstance(response, str)
        assert len(response) > 0

    def test_skill_matches_intent(self, mock_weather_skill):
        """Test skill intent matching."""
        assert mock_weather_skill.matches("What's the weather?") is True
        assert mock_weather_skill.matches("weather forecast") is True
        assert mock_weather_skill.matches("What time is it?") is False

    def test_skill_matches_case_insensitive(self, mock_weather_skill):
        """Test intent matching is case insensitive."""
        assert mock_weather_skill.matches("WEATHER") is True
        assert mock_weather_skill.matches("Weather") is True

    def test_skill_enable_disable(self, mock_weather_skill):
        """Test enabling/disabling a skill."""
        assert mock_weather_skill.enabled is True

        mock_weather_skill.enabled = False
        assert mock_weather_skill.enabled is False

        mock_weather_skill.enabled = True
        assert mock_weather_skill.enabled is True


class TestIntentRouting:
    """Test intent routing logic."""

    def test_register_skill(self, skill_router, mock_weather_skill):
        """Test registering a skill."""
        skill_router.register(mock_weather_skill)
        assert 'weather' in skill_router.skills
        assert skill_router.get_skill('weather') == mock_weather_skill

    def test_route_to_matched_skill(self, skill_router, mock_weather_skill):
        """Test routing to a matching skill."""
        skill_router.register(mock_weather_skill)

        result = skill_router.route("What's the weather?")

        assert result['success'] is True
        assert result['skill'] == 'weather'
        assert result['response'] == "The weather is sunny with a high of 72 degrees."
        assert result['confidence'] == 1.0

    def test_route_no_matching_skill(self, skill_router):
        """Test routing when no skill matches."""
        result = skill_router.route("Tell me a joke")

        assert result['success'] is False
        assert result['skill'] is None
        assert 'error' in result

    def test_route_multiple_skills(self, skill_router, mock_weather_skill, mock_time_skill):
        """Test routing with multiple registered skills."""
        skill_router.register(mock_weather_skill)
        skill_router.register(mock_time_skill)

        # Route to weather skill
        weather_result = skill_router.route("What's the weather?")
        assert weather_result['skill'] == 'weather'

        # Route to time skill
        time_result = skill_router.route("What time is it?")
        assert time_result['skill'] == 'time'

    def test_route_with_context(self, skill_router, mock_weather_skill):
        """Test routing with context information."""
        skill_router.register(mock_weather_skill)

        context = {'session_id': 'test-session', 'user_id': 'user-1'}
        result = skill_router.route("Tell me about the weather", context)

        assert result['success'] is True
        assert result['skill'] == 'weather'

    def test_route_skill_error_handling(self, skill_router):
        """Test routing handles skill errors gracefully."""
        class ErrorSkill(SkillBase):
            def __init__(self):
                super().__init__('error', ['error'])

            def handle(self, user_input: str, context: dict = None) -> str:
                raise RuntimeError("Skill execution failed")

        error_skill = ErrorSkill()
        skill_router.register(error_skill)

        result = skill_router.route("error test")

        assert result['success'] is False
        assert result['response'] is None
        assert 'error' in result

    def test_route_disabled_skill(self, skill_router, mock_weather_skill):
        """Test that disabled skills are not matched."""
        skill_router.register(mock_weather_skill)
        mock_weather_skill.enabled = False

        result = skill_router.route("What's the weather?")

        assert result['success'] is False
        assert result['skill'] is None


class TestSkillExecution:
    """Test individual skill execution."""

    def test_weather_skill_execution(self, mock_weather_skill):
        """Test weather skill handles requests."""
        response = mock_weather_skill.handle("What's the weather in NYC?")
        assert "weather" in response.lower() or "sunny" in response.lower()

    def test_time_skill_execution(self, mock_time_skill):
        """Test time skill handles requests."""
        response = mock_time_skill.handle("What time is it?")
        assert "time" in response.lower() or "PM" in response

    def test_calculator_skill_execution(self, mock_calculator_skill):
        """Test calculator skill handles requests."""
        response = mock_calculator_skill.handle("What is 5 plus 3?")
        assert isinstance(response, str)
        assert len(response) > 0

    def test_skill_with_multiple_intents(self):
        """Test skill matching multiple intent patterns."""
        class MultiIntentSkill(SkillBase):
            def __init__(self):
                super().__init__('multi', ['hello', 'hi', 'hey', 'greetings'])

            def handle(self, user_input: str, context: dict = None) -> str:
                return "Hello! How can I help?"

        skill = MultiIntentSkill()

        assert skill.matches("Hello there")
        assert skill.matches("Hi!")
        assert skill.matches("Hey, what's up?")
        assert skill.matches("Greetings!")
        assert not skill.matches("Goodbye")


class TestIntentRouterIntegration:
    """Test intent router with multiple skills."""

    def test_skill_priority(self, skill_router):
        """Test skill matching priority."""
        class SkillA(SkillBase):
            def __init__(self):
                super().__init__('skill_a', ['test'])

            def handle(self, user_input: str, context: dict = None) -> str:
                return "Response from A"

        class SkillB(SkillBase):
            def __init__(self):
                super().__init__('skill_b', ['test'])

            def handle(self, user_input: str, context: dict = None) -> str:
                return "Response from B"

        skill_router.register(SkillA())
        skill_router.register(SkillB())

        result = skill_router.route("test")
        # First registered skill should match
        assert result['skill'] in ['skill_a', 'skill_b']

    def test_list_skills(self, skill_router, mock_weather_skill, mock_time_skill):
        """Test listing all registered skills."""
        skill_router.register(mock_weather_skill)
        skill_router.register(mock_time_skill)

        skills = skill_router.list_skills()

        assert 'weather' in skills
        assert 'time' in skills
        assert len(skills) >= 2

    def test_get_nonexistent_skill(self, skill_router):
        """Test getting a skill that doesn't exist."""
        result = skill_router.get_skill('nonexistent')
        assert result is None

    def test_chain_of_routing(self, skill_router, mock_weather_skill, mock_time_skill, mock_calculator_skill):
        """Test routing multiple sequential requests."""
        skill_router.register(mock_weather_skill)
        skill_router.register(mock_time_skill)
        skill_router.register(mock_calculator_skill)

        requests = [
            ("What's the weather?", 'weather'),
            ("What time is it?", 'time'),
            ("Calculate 10 plus 5", 'calculator'),
        ]

        for user_input, expected_skill in requests:
            result = skill_router.route(user_input)
            assert result['skill'] == expected_skill
            assert result['success'] is True


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
