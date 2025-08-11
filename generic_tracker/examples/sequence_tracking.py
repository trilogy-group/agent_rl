"""
Sequence Tracking Example

Demonstrates how to track operation sequences and analyze call chains.
"""

from generic_tracker import track, get_tracker, analyze_sequences
import time


# Example: Nested function calls that form a sequence
@track(thread_id="session_id", user_id="user_id")
def orchestrator(session_id: str, user_id: str, request: str):
    """Main orchestrator function.""" 
    print(f"🎯 Orchestrator: Processing request from {user_id}")
    
    # Call multiple steps in sequence
    context = analyze_request(request)
    plan = create_plan(context)
    result = execute_plan(plan)
    
    return {"result": result, "status": "completed"}


@track(thread_id="session_id")
def analyze_request(request: str, session_id: str = "default"):
    """Analyze the incoming request."""
    print(f"🔍 Analyzing request: {request}")
    time.sleep(0.1)  # Simulate processing
    
    # Call sub-functions
    intent = extract_intent(request)
    entities = extract_entities(request)
    
    return {"intent": intent, "entities": entities}


@track(thread_id="session_id")
def extract_intent(text: str, session_id: str = "default"):
    """Extract intent from text."""
    print("  📋 Extracting intent...")
    time.sleep(0.05)
    return "book_flight"


@track(thread_id="session_id")
def extract_entities(text: str, session_id: str = "default"):
    """Extract entities from text."""
    print("  🏷️  Extracting entities...")
    time.sleep(0.03)
    return {"destination": "Paris", "date": "2024-03-15"}


@track(thread_id="session_id")
def create_plan(context: dict, session_id: str = "default"):
    """Create execution plan."""
    print(f"📝 Creating plan for {context['intent']}")
    time.sleep(0.08)
    
    # Validate the plan
    validate_plan(context)
    
    return {"steps": ["search_flights", "check_availability", "present_options"]}


@track(thread_id="session_id")
def validate_plan(context: dict, session_id: str = "default"):
    """Validate the execution plan."""
    print("  ✅ Validating plan...")
    time.sleep(0.02)
    return True


@track(thread_id="session_id")
def execute_plan(plan: dict, session_id: str = "default"):
    """Execute the plan."""
    print(f"⚡ Executing plan with {len(plan['steps'])} steps")
    time.sleep(0.12)
    
    # Execute steps
    for step in plan["steps"]:
        execute_step(step)
    
    return "Flight options found"


@track(thread_id="session_id")
def execute_step(step: str, session_id: str = "default"):
    """Execute a single step."""
    print(f"  🔧 Executing step: {step}")
    time.sleep(0.04)
    return f"Completed {step}"


def demonstrate_sequence_tracking():
    """Demonstrate sequence tracking capabilities."""
    print("🚀 Sequence Tracking Demonstration\n")
    
    # Execute a complex nested operation
    result = orchestrator(
        session_id="demo-session-123",
        user_id="user-456",
        request="I want to book a flight to Paris on March 15th"
    )
    
    print(f"\n📋 Final result: {result}")
    
    # Analyze the tracked sequences
    print("\n" + "="*80)
    print("📊 SEQUENCE ANALYSIS")
    print("="*80)
    
    # Get all tracked operations
    tracker = get_tracker()
    operations = tracker._storage.get_operations()
    
    # Create analyzer
    analyzer = analyze_sequences(operations)
    
    # Print the sequence
    analyzer.print_sequence("demo-session-123")
    
    # Show call tree
    print("\n🌳 Call Tree:")
    print("-" * 40)
    tree = analyzer.get_call_tree("demo-session-123")
    print_tree(tree, indent=0)
    
    # Show operation flow
    print("\n📈 Operation Flow:")
    print("-" * 40)
    flow = analyzer.get_operation_flow("demo-session-123")
    for item in flow:
        indent = "  " * item["depth"]
        timing = f"({item['duration_ms']:.1f}ms)" if item.get('duration_ms') else ""
        print(f"{indent}{item['seq']}. {item['name']} {timing}")
    
    # Show statistics
    print("\n📊 Statistics:")
    print("-" * 40)
    stats = analyzer.get_statistics("demo-session-123")
    print(f"Total operations: {stats['total_operations']}")
    print(f"Success rate: {stats['by_status'].get('completed', 0) / stats['total_operations'] * 100:.1f}%")
    print(f"Average duration: {sum(op['avg_duration_ms'] for op in stats['by_operation'].values()) / len(stats['by_operation']):.1f}ms")
    
    # Show call chains
    print("\n🔗 Call Chains:")
    print("-" * 40)
    chains = analyzer.get_call_chains("demo-session-123")
    for i, chain in enumerate(chains, 1):
        print(f"{i}. {' → '.join(chain)}")


def print_tree(node, indent=0):
    """Print tree structure recursively."""
    prefix = "  " * indent
    
    if "operations" in node:
        # Root node
        for op in node["operations"]:
            print_tree(op, indent)
    else:
        # Operation node
        status_icon = {"completed": "✅", "failed": "❌", "started": "🔄"}.get(node["status"], "❓")
        duration = f" ({node.get('duration_ms', 0):.1f}ms)" if node.get('duration_ms') else ""
        print(f"{prefix}{status_icon} {node['name']}{duration}")
        
        for child in node.get("children", []):
            print_tree(child, indent + 1)


if __name__ == "__main__":
    demonstrate_sequence_tracking()