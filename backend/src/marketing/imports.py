"""
Import helper for agent_evolve package.

This module handles the import of agent_evolve components from the installed package.
"""

# Import from the installed agent-evolve package
try:
    from agent_evolve.tracking.decorator import track_node
    from agent_evolve.evolve_decorator import evolve
    print(f"✅ Successfully imported decorators from installed agent-evolve package")
    __all__ = ['track_node', 'evolve']
except ImportError as e:
    # Fallback - create dummy decorators that do nothing
    print(f"⚠️  Warning: Could not import agent_evolve components: {e}")
    print("🔄 Using dummy decorators...")
    
    def track_node(**kwargs):
        """Dummy track_node decorator that does nothing."""
        print(f"🟡 Dummy track_node decorator called with {kwargs}")
        def decorator(func):
            print(f"🟡 Dummy track_node decorating function: {func.__name__}")
            return func
        return decorator
    
    def evolve(**kwargs):
        """Dummy evolve decorator that does nothing."""
        print(f"🟡 Dummy evolve decorator called with {kwargs}")
        def decorator(func):
            print(f"🟡 Dummy evolve decorating function: {func.__name__}")
            return func
        return decorator
    
    __all__ = ['track_node', 'evolve']