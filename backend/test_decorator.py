#!/usr/bin/env python3
"""
Test script to check if decorators are working properly
"""

import sys
import os

# Add the backend src to path 
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_decorator_import():
    """Test if we can import and use the decorators"""
    print("🧪 Testing Decorator Import and Functionality")
    print("=" * 50)
    
    try:
        from src.marketing.imports import track_node, evolve
        print("✅ Successfully imported decorators")
        
        # Test track_node
        @track_node()
        def test_node(state):
            print("  📝 test_node executed")
            return {"processed": True}
        
        # Test evolve  
        @evolve()
        def test_function():
            print("  🧬 test_function executed")
            return "evolved"
        
        print("\n🔧 Testing decorator execution:")
        result1 = test_node({"messages": []})
        print(f"  ✅ track_node result: {result1}")
        
        result2 = test_function()
        print(f"  ✅ evolve result: {result2}")
        
        # Check if real tracking happened
        try:
            from agent_evolve.tracking import get_tracker
            tracker = get_tracker()
            
            if hasattr(tracker, 'storage') and hasattr(tracker.storage, 'operations'):
                ops_count = len(tracker.storage.operations)
                msgs_count = len(tracker.storage.messages)
                print(f"\n📊 Tracking Data:")
                print(f"  Operations tracked: {ops_count}")
                print(f"  Messages tracked: {msgs_count}")
                
                if ops_count > 0 or msgs_count > 0:
                    print("  ✅ Real tracking is working!")
                    return True
                else:
                    print("  ⚠️  Decorators working but no data tracked")
                    return False
            else:
                print("  ⚠️  Could not access tracker storage")
                return False
                
        except Exception as e:
            print(f"  ⚠️  Could not check tracking data: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ Failed to import decorators: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing decorators: {e}")
        return False

if __name__ == "__main__":
    working = test_decorator_import()
    print(f"\n{'🎉 Decorators are working!' if working else '⚠️  Decorators may be in dummy mode'}")
    exit(0 if working else 1)