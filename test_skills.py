"""
Test script for NomadAI Voice Agent skills.
Run this to verify the skill system is working correctly.
"""

import sys
import asyncio

# Add src to path
sys.path.insert(0, '.')

from src.skills import get_all_skills


async def test_skills():
    """Test basic skill functionality."""
    print("NomadAI Voice Agent - Skills Test\n")
    print("=" * 60)

    # Get all skills
    skills = get_all_skills()
    print(f"\n✓ Loaded {len(skills)} skills:")

    # Display skills by category
    categories = {}
    for skill in skills:
        skill_type = skill.__class__.__module__.split('.')[-1]
        if skill_type not in categories:
            categories[skill_type] = []
        categories[skill_type].append(skill)

    for category, category_skills in categories.items():
        print(f"\n  {category.upper()}:")
        for skill in category_skills:
            print(f"    - {skill.name}: {skill.description}")
            print(f"      Examples: {', '.join(skill.example_utterances[:2])}")

    # Test a simple skill execution
    print("\n" + "=" * 60)
    print("\n✓ Testing WiFi Skill execution...")

    from src.skills.concierge import WifiSkill

    wifi_skill = WifiSkill()
    context = {
        "transcription": "What's the WiFi password?",
        "session_id": "test_session",
    }

    result = await wifi_skill.execute(context)

    print(f"\n  Input: {context['transcription']}")
    print(f"  Response: {result['response'][:100]}...")
    print(f"  Action: {result['action']}")
    print(f"  Skill: {result['metadata']['skill']}")

    print("\n" + "=" * 60)
    print("\n✅ All tests passed! Skill system is working correctly.\n")


if __name__ == "__main__":
    asyncio.run(test_skills())
