"""
Test Supervity AI Integration

Tests the Supervity AI integration for policies, insights, and chat.
"""
# ruff: noqa: E402  # imports follow sys.path setup + key check by design

import os
import sys
import asyncio
import logging

# Configure logging for CLI output
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Read API key from environment — never hardcode a key in source.
# Export GEMINI_API_KEY before running, e.g.:
#   export GEMINI_API_KEY=$(grep '^GEMINI_API_KEY=' .env | cut -d= -f2-)
if not os.environ.get("GEMINI_API_KEY"):
    print(
        "ERROR: GEMINI_API_KEY is not set in the environment.\n"
        "Set it (e.g. `export GEMINI_API_KEY=...`) before running this script.",
        file=sys.stderr,
    )
    sys.exit(1)

from app.services.ai.gemini import GeminiService
from app.services.rule_architect import prompt_optimizer, rule_architect


def test_supervity_connection():
    """Test if Supervity AI client initializes properly."""
    logger.info("\n" + "="*60)
    logger.info("   TESTING SUPERVITY AI CONNECTION")
    logger.info("="*60)
    
    service = GeminiService()
    
    if service.is_available:
        logger.info("✅ Supervity AI client initialized successfully!")
        logger.info(f"   Model: {service.model}")
        return True
    else:
        logger.error("❌ Supervity AI client not available")
        logger.error("   Check if AI package is installed and API key is valid")
        return False


async def test_prompt_optimizer():
    """Test the prompt optimizer."""
    logger.info("\n" + "-"*60)
    logger.info("   Testing Prompt Optimizer")
    logger.info("-"*60)
    
    test_prompts = [
        "Auto approve all invoices under $100 from approved vendors",
        "Flag any employee who works more than 10 hours overtime in a week",
        "Escalate customer tickets from enterprise accounts to tier 2 support"
    ]
    
    for prompt in test_prompts:
        logger.info(f"\n📝 Input: \"{prompt}\"")
        try:
            refined = await prompt_optimizer.refine(prompt)
            logger.info(f"✨ Refined: \"{refined}\"")
        except Exception as e:
            logger.error(f"❌ Error: {e}")


async def test_rule_analysis():
    """Test the rule architect analysis."""
    logger.info("\n" + "-"*60)
    logger.info("   Testing Rule Architect (Conflict Detection)")
    logger.info("-"*60)
    
    # Test analyzing a new rule
    new_rule = {
        "natural_language": "Auto-approve all transactions under $500 without review",
        "policy_type": "BASE",
        "entity_name": None
    }
    
    existing_rules = [
        {
            "id": "existing-001",
            "name": "High-value approval",
            "natural_language": "Require manager approval for transactions over $100",
            "policy_type": "BASE",
            "entity_name": None,
            "is_active": True
        }
    ]
    
    logger.info(f"\n📋 New Rule: \"{new_rule['natural_language']}\"")
    logger.info(f"📋 Existing: \"{existing_rules[0]['natural_language']}\"")
    
    try:
        analysis = await rule_architect.analyze_rule(new_rule, existing_rules)
        logger.info("\n📊 Analysis Result:")
        logger.info(f"   Valid: {analysis.is_valid}")
        logger.info(f"   Conflicts: {len(analysis.conflicts)}")
        logger.info(f"   Overrides: {len(analysis.overrides)}")
        logger.info(f"   Suggestions: {len(analysis.suggested_instructions)}")
        if analysis.suggested_instructions:
            logger.info("\n💡 Suggested Instructions:")
            for i, suggestion in enumerate(analysis.suggested_instructions[:3], 1):
                logger.info(f"   {i}. {suggestion}")
    except Exception as e:
        logger.error(f"❌ Error: {e}")


async def test_supervity_greeting():
    """Test Supervity AI greeting."""
    logger.info("\n" + "-"*60)
    logger.info("   Testing Supervity AI Greeting")
    logger.info("-"*60)
    
    try:
        from google import genai

        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        model = os.environ.get("AI_MODEL", "gemini-3-flash-preview")

        response = client.models.generate_content(
            model=model,
            contents="You are Supervity AI Manager. Greet the user in a friendly, professional way. Start with 'Greetings from Supervity!' and keep it to 2 sentences.",
        )

        logger.info(f"✅ Response (model={model}): {response.text}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False


async def main():
    logger.info("\n" + "="*60)
    logger.info("   🤖 SUPERVITY AI INTEGRATION TEST SUITE")
    logger.info("="*60)
    
    # Test 1: Connection
    connected = test_supervity_connection()
    
    if not connected:
        logger.warning("\n⚠️ Skipping AI tests - Supervity AI not available")
        return
    
    # Test 2: Supervity greeting
    await test_supervity_greeting()
    
    # Test 3: Prompt Optimizer
    await test_prompt_optimizer()
    
    # Test 4: Rule Analysis
    await test_rule_analysis()
    
    logger.info("\n" + "="*60)
    logger.info("   ✅ SUPERVITY AI INTEGRATION TESTS COMPLETE")
    logger.info("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
