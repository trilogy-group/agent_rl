#!/usr/bin/env python3
"""
Simple test for the decorator system
"""

# Test basic decorator functionality
class OptimizeCandidate:
    _registered_functions = []
    
    def __init__(self, name=None, description=None, category=None):
        self.name = name
        self.description = description
        self.category = category
    
    def __call__(self, func):
        func._optimize_candidate = True
        func._optimize_name = self.name or func.__name__
        func._optimize_description = self.description or func.__doc__
        func._optimize_category = self.category
        
        self._registered_functions.append({
            'function': func,
            'name': func._optimize_name,
            'description': func._optimize_description,
            'category': func._optimize_category
        })
        
        return func
    
    @classmethod
    def get_registered_functions(cls):
        return cls._registered_functions

# Simple decorator
optimize = OptimizeCandidate

# Test function
@optimize(description="Test function")
def test_function(x):
    """A test function"""
    return x * 2

if __name__ == "__main__":
    print("Testing decorator system...")
    
    # Test the function
    result = test_function(5)
    print(f"Function result: {result}")
    
    # Check if it was registered
    registered = OptimizeCandidate.get_registered_functions()
    print(f"Registered functions: {len(registered)}")
    
    for func_info in registered:
        print(f"- {func_info['name']}: {func_info['description']}")
    
    print("✅ Basic decorator system works!")