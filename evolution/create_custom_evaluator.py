"""
Simplified approach to generate truly custom evaluators
"""

def create_custom_evaluator(tool_name: str, tool_source: str, metadata: dict, training_data: list) -> str:
    """Generate a custom evaluator for a specific tool"""
    
    metrics = metadata.get('metrics', ['quality', 'accuracy', 'usefulness'])
    
    prompt = f"""Create a Python evaluator for the tool '{tool_name}'.

The tool does: {metadata.get('description', 'Unknown')}

Tool source code:
```python
{tool_source[:1500]}
```

Example input/output from training data:
{training_data[0] if training_data else {}}

Generate an evaluator that:
1. Loads and executes this specific tool
2. Evaluates outputs based on what THIS tool is supposed to do
3. Uses these metrics: {metrics}
4. Returns scores 0.0-1.0 for each metric

The evaluation should be specific to what {tool_name} produces. For example:
- If it generates brand guidelines, check if they're comprehensive and actionable
- If it classifies intent, check accuracy against expected classifications
- If it creates content, evaluate quality, engagement, relevance

Output ONLY the Python code for the evaluator, starting with imports."""
    
    return prompt