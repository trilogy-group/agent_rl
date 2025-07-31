#!/usr/bin/env python3
"""
Test what's available in evolve_decorator
"""

try:
    from evolve_decorator import *
    print("✅ Import successful")
    
    # Check what's available
    import evolve_decorator
    print("\nAvailable in evolve_decorator:")
    for name in dir(evolve_decorator):
        if not name.startswith('_'):
            print(f"  - {name}")
    
    # Test if evolve_nlg exists
    if hasattr(evolve_decorator, 'evolve_nlg'):
        print("\n✅ evolve_nlg is available")
        print(f"evolve_nlg type: {type(evolve_decorator.evolve_nlg)}")
    else:
        print("\n❌ evolve_nlg is NOT available")
    
    # Try to use it
    try:
        @evolve_nlg(name="test")
        def test_func():
            pass
        print("✅ evolve_nlg decorator works")
    except Exception as e:
        print(f"❌ evolve_nlg decorator failed: {e}")
        
except Exception as e:
    print(f"❌ Import failed: {e}")