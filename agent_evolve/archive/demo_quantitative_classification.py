#!/usr/bin/env python3
"""
Demo of quantitative function classification and specialized prompts
"""

from pathlib import Path

def analyze_function_type(tool_dir: Path) -> tuple:
    """Simulate the enhanced function analysis without requiring API key"""
    
    tool_file = tool_dir / "evolve_target.py"
    
    if not tool_file.exists():
        return "Unknown function", "creative", ["quality", "relevance", "usefulness", "clarity"]
    
    # Read the function source code
    with open(tool_file, 'r') as f:
        source_code = f.read()
    
    # Simple heuristic classification based on code analysis
    quantitative_indicators = [
        'calculate', 'analysis', 'technical', 'financial', 'mathematical', 
        'statistics', 'metrics', 'indicators', 'sma', 'rsi', 'macd',
        'DataFrame', 'numpy', 'pandas', 'yfinance', 'rolling', 'mean'
    ]
    
    creative_indicators = [
        'generate', 'create', 'write', 'content', 'essay', 'story',
        'brand', 'marketing', 'guidelines', 'draft', 'text'
    ]
    
    # Count indicators in source code (case insensitive)
    source_lower = source_code.lower()
    quant_score = sum(1 for indicator in quantitative_indicators if indicator in source_lower)
    creative_score = sum(1 for indicator in creative_indicators if indicator in source_lower)
    
    # Determine function type
    if quant_score > creative_score:
        function_type = "quantitative"
        if 'technical_analysis' in tool_dir.name or 'analysis' in source_lower:
            description = "Performs technical analysis on financial data with mathematical indicators"
            metrics = ["correctness", "completeness", "accuracy", "consistency"]
        else:
            description = "Performs quantitative calculations and data analysis"  
            metrics = ["accuracy", "precision", "logical_soundness", "completeness"]
    else:
        function_type = "creative"
        description = "Generates creative content or text-based materials"
        metrics = ["quality", "relevance", "engagement", "authenticity"]
    
    return description, function_type, metrics

def demo_classification():
    """Demo the classification system"""
    
    print("🔍 Demo: Quantitative Function Classification System")
    print("=" * 60)
    
    tool_dir = Path("tools/get_technical_analysis")
    
    if tool_dir.exists():
        print(f"📁 Analyzing tool: {tool_dir.name}")
        
        # Simulate the enhanced analysis
        description, function_type, metrics = analyze_function_type(tool_dir)
        
        print(f"\n📊 Classification Results:")
        print(f"  Function Type: {function_type.upper()}")
        print(f"  Description: {description}")
        print(f"  Specialized Metrics: {metrics}")
        
        # Show what evaluation approach would be used
        print(f"\n🎯 Evaluation Approach:")
        if function_type == "quantitative":
            print("  ✓ QUANTITATIVE EVALUATION")
            print("    - Focus on logical correctness of calculations")
            print("    - Verify completeness of analysis")
            print("    - Check accuracy of algorithmic implementation")
            print("    - Assess consistency of results")
            print("    - Validate data integrity and value ranges")
            
            print(f"\n📝 Sample Evaluation Criteria:")
            for metric in metrics:
                if metric == "correctness":
                    print(f"    - {metric}: Are calculations mathematically sound?")
                elif metric == "completeness": 
                    print(f"    - {metric}: Does output include all expected indicators?")
                elif metric == "accuracy":
                    print(f"    - {metric}: Are the algorithmic implementations correct?")
                elif metric == "consistency":
                    print(f"    - {metric}: Do results make logical sense?")
                    
        else:
            print("  ✓ CREATIVE/CONTENT EVALUATION")
            print("    - Focus on subjective quality assessment")
            print("    - Evaluate relevance to requirements")
            print("    - Assess engagement and effectiveness")
            print("    - Check authenticity and originality")
            
        print(f"\n🚀 Enhanced Features:")
        print("    ✅ Automatic function type detection")
        print("    ✅ Specialized evaluation prompts")
        print("    ✅ Context-aware metrics selection") 
        print("    ✅ Domain-specific evaluation criteria")
        
        # Show file content sample
        tool_file = tool_dir / "evolve_target.py"
        if tool_file.exists():
            with open(tool_file, 'r') as f:
                lines = f.readlines()
            
            print(f"\n📄 Function Code Sample:")
            for i, line in enumerate(lines[50:65], 51):  # Show function definition area
                if 'def get_technical_analysis' in line:
                    print(f"    {i:2d}: >>> {line.rstrip()}")
                else:
                    print(f"    {i:2d}:     {line.rstrip()}")
                    
    else:
        print(f"❌ Tool directory not found: {tool_dir}")
        print("   Make sure get_technical_analysis tool is extracted")

if __name__ == "__main__":
    demo_classification()