#!/usr/bin/env python3
"""
Simplified evaluator generator that creates custom evaluators for each tool
"""

import json
from typing import Dict, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage


def create_evaluator_with_llm(tool_name: str, tool_source: str, metadata: Dict, training_data: List[Dict]) -> str:
    """Generate a truly custom evaluator for the specific tool"""
    
    model = ChatOpenAI(model="gpt-4o", temperature=0.2)
    metrics = metadata.get('metrics', ["quality", "accuracy", "usefulness"])
    
    # Build a clear understanding of what the tool does
    tool_analysis = f"""
Tool: {tool_name}
Description: {metadata.get('description', 'No description')}
Category: {metadata.get('category', 'utility')}

The tool takes inputs like: {json.dumps(training_data[0]['input'] if training_data else {}, indent=2)}
Expected output qualities: {json.dumps(training_data[0].get('expected_output', {}), indent=2) if training_data else 'High quality output'}
"""
    
    prompt = f"""Create a Python evaluator specifically for the tool '{tool_name}'.

{tool_analysis}

TOOL SOURCE CODE:
```python
{tool_source[:2000]}
```

Generate an evaluator that:
1. Imports and executes the '{tool_name}' function with test inputs
2. Evaluates the OUTPUT based on what '{tool_name}' is supposed to produce
3. Uses evaluation logic that makes sense for THIS specific tool
4. Scores these metrics: {metrics}

The evaluation logic should be SPECIFIC to {tool_name}. For example:
- If it generates brand guidelines: check if they're comprehensive, clear, actionable
- If it classifies intent: check accuracy against expected classifications  
- If it creates posts: evaluate engagement potential, clarity, brand alignment

Output ONLY Python code starting with imports. Use this structure:

```python
import os
import json
import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage

logger = logging.getLogger(__name__)

def evaluate(program) -> dict:
    \"\"\"Evaluate {tool_name} outputs\"\"\"
    metrics = {json.dumps(metrics)}
    
    try:
        # [Load tool and training data]
        # [Execute tool with test inputs]
        # [Evaluate outputs with logic specific to {tool_name}]
        # [Return scores for each metric]
    except Exception as e:
        logger.error(f"Evaluation failed: {{e}}")
        return {{metric: 0.0 for metric in metrics}}
```

Make the evaluation logic SPECIFIC to what {tool_name} does, not generic."""
    
    response = model.invoke([
        SystemMessage(content="You are an expert at creating custom evaluators. Output only Python code."),
        HumanMessage(content=prompt)
    ])
    
    return response.content


# Test it
if __name__ == "__main__":
    # Example usage
    tool_source = '''
def generate_brand_guidelines(brand_research: List[str]) -> str:
    """Generate brand guidelines from research content"""
    # ... implementation
'''
    
    metadata = {
        "name": "generate_brand_guidelines",
        "description": "Generates comprehensive brand guidelines from brand research",
        "metrics": ["brand_alignment", "clarity", "actionability", "comprehensiveness", "structure"]
    }
    
    training_data = [{
        "input": {"brand_research": ["Tech startup focused on AI healthcare", "Professional yet approachable tone"]},
        "expected_output": {"quality_criteria": ["coherent", "actionable", "brand-aligned"]}
    }]
    
    evaluator_code = create_evaluator_with_llm(
        "generate_brand_guidelines",
        tool_source,
        metadata,
        training_data
    )
    
    print(evaluator_code)