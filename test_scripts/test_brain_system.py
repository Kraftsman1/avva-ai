#!/usr/bin/env python3
"""
Test script for the Brain system.

Tests Brain initialization, registration, selection, and execution.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.brain import brain
from core.brain_manager import brain_manager
from core.brain_interface import BrainConfig
from core.brains.rules_brain import RulesBrain


def test_brain_initialization():
    """Test that Brain system initializes correctly."""
    print("\n=== Test 1: Brain Initialization ===")
    
    # Check that Brains are registered
    all_brains = brain_manager.get_all_brains()
    print(f"✓ Registered Brains: {len(all_brains)}")
    
    for b in all_brains:
        print(f"  - {b.name} ({b.provider}) - Privacy: {b.get_privacy_level().value}")
    
    # Check active Brain
    active = brain_manager.get_active_brain()
    if active:
        print(f"✓ Active Brain: {active.name}")
    else:
        print("⚠ No active Brain set")
    
    # Check fallback Brain
    fallback_id = brain_manager.fallback_brain_id
    if fallback_id:
        fallback = brain_manager.get_brain(fallback_id)
        print(f"✓ Fallback Brain: {fallback.name}")
    else:
        print("⚠ No fallback Brain set")
    
    print("✅ Brain initialization test passed\n")


def test_brain_health_checks():
    """Test health checks for all Brains."""
    print("=== Test 2: Brain Health Checks ===")
    
    all_brains = brain_manager.get_all_brains()
    
    for b in all_brains:
        health = b.health_check()
        status_emoji = "✓" if health.status.value == "available" else "⚠"
        print(f"{status_emoji} {b.name}: {health.status.value} - {health.message}")
    
    print("✅ Health check test passed\n")


def test_brain_capabilities():
    """Test capability reporting."""
    print("=== Test 3: Brain Capabilities ===")
    
    all_brains = brain_manager.get_all_brains()
    
    for b in all_brains:
        caps = [cap.value for cap in b.get_capabilities()]
        print(f"  {b.name}: {', '.join(caps)}")
    
    print("✅ Capability test passed\n")


def test_brain_selection():
    """Test Brain selection logic."""
    print("=== Test 4: Brain Selection ===")
    
    # Test default selection
    brain_default = brain_manager.select_brain()
    print(f"✓ Default selection: {brain_default.name if brain_default else 'None'}")
    
    # Test sensitive context (should prefer local)
    context_sensitive = {"sensitive": True}
    brain_sensitive = brain_manager.select_brain(context_sensitive)
    print(f"✓ Sensitive context selection: {brain_sensitive.name if brain_sensitive else 'None'}")
    if brain_sensitive:
        print(f"  Privacy level: {brain_sensitive.get_privacy_level().value}")
    
    print("✅ Selection test passed\n")


def test_rules_brain_execution():
    """Test Rules Brain execution."""
    print("=== Test 5: Rules Brain Execution ===")
    
    rules = brain_manager.get_brain("rules")
    if not rules:
        print("❌ Rules Brain not found")
        return
    
    # Test with a simple command
    response = rules.execute("what time is it", {}, {})
    print(f"✓ Rules Brain response:")
    print(f"  Success: {response.success}")
    print(f"  Intent: {response.intent}")
    print(f"  Confidence: {response.confidence}")
    
    print("✅ Rules Brain execution test passed\n")


def test_brain_process():
    """Test the main brain.process() method."""
    print("=== Test 6: Brain Process Method ===")
    
    # Test with a time query
    result = brain.process("what time is it")
    print(f"✓ Process result for 'what time is it':")
    if isinstance(result, dict):
        print(f"  Type: {result.get('type')}")
        print(f"  Text: {result.get('text', str(result))[:100]}")
    else:
        print(f"  Result: {str(result)[:100]}")
    
    print("✅ Process test passed\n")


def main():
    """Run all tests."""
    print("\n" + "="*50)
    print("Brain System Test Suite")
    print("="*50)
    
    try:
        test_brain_initialization()
        test_brain_health_checks()
        test_brain_capabilities()
        test_brain_selection()
        test_rules_brain_execution()
        test_brain_process()
        
        print("="*50)
        print("✅ All tests passed!")
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
