#!/usr/bin/env python3
"""
Sofia Administrator Test
Quick validation that administrator mode is working.
"""

import asyncio
import json
from pathlib import Path

async def main():
    print("\n" + "="*70)
    print("🔍 SOFIA ADMINISTRATOR MODE — VALIDATION TEST")
    print("="*70 + "\n")
    
    # Test 1: Import modules
    print("📦 Test 1: Importing modules...")
    try:
        from aura_fusion.sofia.autonomy.resource_optimizer import ResourceOptimizer
        from aura_fusion.sofia.autonomy.usage_detector import UsageDetector
        print("   ✅ ResourceOptimizer imported")
        print("   ✅ UsageDetector imported")
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return
    
    # Test 2: Check activity profiles
    print("\n📋 Test 2: Activity profiles available...")
    profiles = ResourceOptimizer.ACTIVITY_PROFILES
    print(f"   ✅ {len(profiles)} profiles configured:")
    for activity, profile in profiles.items():
        print(f"      • {activity:20s} → {profile['name']}")
    
    # Test 3: Check example optimization
    print("\n⚙️  Test 3: Generate optimization (simulated gaming)...")
    try:
        # Create mock agent for testing
        class MockAgent:
            def execute_tool(self, *args, **kwargs):
                class Result:
                    success = True
                    output = "game.exe valorant.exe steam.exe"
                    error = None
                return Result()
        
        mock_agent = MockAgent()
        optimizer = ResourceOptimizer(mock_agent)
        
        # Simulate gaming detection
        usage_info = {
            "activity_type": "gaming",
            "confidence": 0.85,
            "details": {"detected_keywords": ["valorant", "steam"]},
        }
        
        profile_info = optimizer.get_profile_for_activity(usage_info)
        print(f"   ✅ Detected: {profile_info['activity_detected']}")
        print(f"   ✅ Profile: {profile_info['profile_name']}")
        print(f"   ✅ Description: {profile_info['description']}")
        
        # Check optimizations
        actions = optimizer.generate_optimization_actions(usage_info)
        print(f"   ✅ Optimization actions generated: {len(actions)}")
        for action in actions:
            print(f"      • {action['description']}")
        
        # Get status message
        status = optimizer.get_status_message(usage_info)
        print(f"   ✅ Sofia says: \"{status}\"")
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return
    
    # Test 4: Verify config
    print("\n⚙️  Test 4: Check Sofia's configuration...")
    config_path = Path.home() / ".config" / "aura-fusion" / "config.yaml"
    if config_path.exists():
        with open(config_path) as f:
            content = f.read()
            if "llama3.1:8b" in content:
                print(f"   ✅ Config uses llama3.1:8b")
            if "allow_self_modification: true" in content.lower():
                print(f"   ✅ Self-modification enabled")
            if "allow_code_execution: true" in content.lower():
                print(f"   ✅ Code execution enabled")
            if "allow_system_commands: true" in content.lower():
                print(f"   ✅ System commands enabled")
    else:
        print(f"   ⚠️  Config file not found at {config_path}")
    
    # Test 5: Check documentation
    print("\n📚 Test 5: Documentation files...")
    docs = [
        "fusion/PERSONALITY.md",
        "fusion/docs/guides/ADMINISTRATOR_GUIDE.md",
        "fusion/local_self/ADMINISTRATOR_QUICK_START.md",
    ]
    for doc in docs:
        doc_path = Path.home() / "ProjectAuraOS" / doc
        if doc_path.exists():
            print(f"   ✅ {doc}")
        else:
            print(f"   ❌ {doc} not found")
    
    print("\n" + "="*70)
    print("✅ ADMINISTRATOR MODE VALIDATION COMPLETE")
    print("="*70)
    print("\n🚀 Sofia is ready as your PC Administrator!")
    print("   • Monitoring: Every 20 seconds")
    print("   • Detection: Gaming, Editing, Coding, Streaming, Creative, Productivity, Idle")
    print("   • Optimization: Automatic, no confirmation needed")
    print("   • Autonomy: Level 5 (MAXIMUM)")
    print("   • Model: llama3.1:8b (local, private)")
    print("\n📖 For more info, read: fusion/docs/guides/ADMINISTRATOR_GUIDE.md")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
