"""
Test imports from backend directory to verify LangGraph server will work.
"""

import sys
import os

def test_agent_evolve_imports():
    """Test that we can import from agent_evolve package."""
    
    print("🧪 Testing Agent Evolve Imports from Backend Directory")
    print("=" * 60)
    
    try:
        from src.marketing.imports import track_node
        print("✅ Successfully imported track_node")
    except ImportError as e:
        print(f"❌ Failed to import track_node: {e}")
        return False
    
    try:
        from src.marketing.imports import evolve
        print("✅ Successfully imported evolve")
    except ImportError as e:
        print(f"❌ Failed to import evolve: {e}")
        return False
    
    return True


def test_marketing_imports():
    """Test marketing module imports."""
    
    print("\n🔧 Testing Marketing Module Imports")
    print("-" * 40)
    
    try:
        from src.marketing.tools import classify_intent
        print("✅ Successfully imported from tools.py")
    except ImportError as e:
        print(f"❌ Failed to import from tools.py: {e}")
        return False
    
    try:
        from src.marketing.graph import orchestrator_node
        print("✅ Successfully imported from graph.py")
    except ImportError as e:
        print(f"❌ Failed to import from graph.py: {e}")
        return False
    
    return True


def test_decorator_functionality():
    """Test that decorators work."""
    
    print("\n⚡ Testing Decorator Functionality")
    print("-" * 40)
    
    from src.marketing.imports import track_node, evolve
    
    # Test track_node decorator
    @track_node()
    def test_node(state):
        return {"processed": True}
    
    # Test evolve decorator  
    @evolve()
    def test_function():
        return "evolved"
    
    try:
        result1 = test_node({"messages": []})
        print(f"✅ track_node decorator works: {result1}")
    except Exception as e:
        print(f"❌ track_node decorator failed: {e}")
        return False
    
    try:
        result2 = test_function()
        print(f"✅ evolve decorator works: {result2}")
    except Exception as e:
        print(f"❌ evolve decorator failed: {e}")
        return False
    
    return True


if __name__ == "__main__":
    print("🚀 Backend Import Test Suite")
    print("=" * 60)
    print(f"Current directory: {os.getcwd()}")
    print(f"Python path includes: {sys.path[:3]}...")
    
    tests = [
        ("Agent Evolve Imports", test_agent_evolve_imports),
        ("Marketing Module Imports", test_marketing_imports),
        ("Decorator Functionality", test_decorator_functionality)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All imports working! LangGraph server should start successfully.")
    else:
        print(f"\n⚠️  Some imports failed. LangGraph server may have issues.")
    
    exit(0 if passed == total else 1)