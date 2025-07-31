#!/usr/bin/env python3
"""
OpenEvolve Runner Script

This script runs OpenEvolve for a selected tool directory using its 
openevolve_config.yaml configuration and evaluator.py.

Usage:
    python run_openevolve.py <tool_directory>
    python run_openevolve.py evolution/tools/reflect_on_draft
"""

import os
import sys
import asyncio
from pathlib import Path
import yaml
from openevolve import OpenEvolve


async def run_openevolve_for_tool(tool_dir: str):
    """Run OpenEvolve for a specific tool directory using Python API"""
    tool_path = Path(tool_dir)
    
    # Validate tool directory
    if not tool_path.exists():
        print(f"Error: Tool directory '{tool_path}' does not exist")
        return False
    
    if not tool_path.is_dir():
        print(f"Error: '{tool_path}' is not a directory")
        return False
    
    # Check for required files
    required_files = {
        'tool.py': tool_path / 'tool.py',
        'evaluator.py': tool_path / 'evaluator.py', 
        'openevolve_config.yaml': tool_path / 'openevolve_config.yaml',
        'training_data.json': tool_path / 'training_data.json'
    }
    
    missing_files = []
    for file_name, file_path in required_files.items():
        if not file_path.exists():
            missing_files.append(file_name)
    
    if missing_files:
        print(f"Error: Missing required files in {tool_path}:")
        for file_name in missing_files:
            print(f"  - {file_name}")
        print("\nPlease run the evaluator generator first:")
        print(f"  python evolution/generate_evaluators.py {tool_path.parent}")
        print(f"  python evolution/generate_openevolve_configs.py {tool_path.parent}")
        return False
    
    # Check for OpenAI API key
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is required")
        print("Please set your OpenAI API key: export OPENAI_API_KEY=your_key_here")
        return False
    
    # Read and validate config
    config_file = required_files['openevolve_config.yaml']
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        print(f"✓ Loaded OpenEvolve config from {config_file}")
        
        # Display key config details
        max_iterations = config.get('max_iterations', 1000)
        population_size = config.get('database', {}).get('population_size', 'unknown')
        temperature = config.get('llm', {}).get('temperature', 'unknown')
        
        print(f"  Max iterations: {max_iterations}")
        print(f"  Population size: {population_size}")
        print(f"  LLM temperature: {temperature}")
        
    except Exception as e:
        print(f"Error: Failed to read config file: {e}")
        return False
    
    # Check if openevolve is available
    
    # Get tool name for display
    tool_name = tool_path.name
    print(f"\n🚀 Starting OpenEvolve optimization for: {tool_name}")
    print(f"📁 Tool directory: {tool_path}")
    print("=" * 60)
    
    # Get absolute paths for OpenEvolve
    tool_file = str(required_files['tool.py'].absolute())
    evaluator_file = str(required_files['evaluator.py'].absolute())
    config_file_path = str(config_file.absolute())
    
    try:
        print(f"Initializing OpenEvolve...")
        print(f"  Initial program: {tool_file}")
        print(f"  Evaluator: {evaluator_file}")
        print(f"  Config: {config_file_path}")
        print(f"  Iterations: {max_iterations}")
        print()
        
        # Initialize OpenEvolve
        evolve = OpenEvolve(
            initial_program_path=tool_file,
            evaluation_file=evaluator_file,
            config_path=config_file_path
        )
        
        print("🔄 Running evolutionary optimization...")
        print("Note: This may take a while depending on max_iterations setting...")
        print("Press Ctrl+C to interrupt if needed.")
        print()
        
        # Run evolution
        best_program = await evolve.run(iterations=max_iterations)
        
        print(f"\n✅ OpenEvolve completed successfully for {tool_name}!")
        print(f"🏆 Best program generated and saved.")
        print(f"📁 Check the output directory for optimized tool variants.")
        
        if best_program:
            print(f"📈 Final optimization results available.")
        
        return True
        
    except KeyboardInterrupt:
        print(f"\n⏹️  OpenEvolve interrupted by user for {tool_name}")
        return False
    except Exception as e:
        print(f"\n❌ Error running OpenEvolve: {e}")
        print(f"Details: {type(e).__name__}: {str(e)}")
        return False


def list_available_tools(tools_base_dir: str = "evolution/tools"):
    """List all available tools with required files"""
    tools_path = Path(tools_base_dir)
    
    if not tools_path.exists():
        print(f"Tools directory '{tools_path}' does not exist")
        return []
    
    available_tools = []
    
    print(f"\nAvailable tools in {tools_path}:")
    print("-" * 40)
    
    for item in tools_path.iterdir():
        if not item.is_dir():
            continue
            
        # Check for required files
        has_tool = (item / 'tool.py').exists()
        has_evaluator = (item / 'evaluator.py').exists()
        has_config = (item / 'openevolve_config.yaml').exists()
        has_data = (item / 'training_data.json').exists()
        
        status = "✅" if all([has_tool, has_evaluator, has_config, has_data]) else "❌"
        missing = []
        
        if not has_tool: missing.append('tool.py')
        if not has_evaluator: missing.append('evaluator.py') 
        if not has_config: missing.append('config.yaml')
        if not has_data: missing.append('training_data.json')
        
        print(f"{status} {item.name}")
        if missing:
            print(f"    Missing: {', '.join(missing)}")
        else:
            available_tools.append(str(item))
    
    return available_tools


async def main():
    """Main entry point"""
    if len(sys.argv) == 1:
        # No arguments - show help and list available tools
        print("OpenEvolve Runner - Evolutionary optimization for agent tools")
        print("=" * 60)
        print("\nUsage:")
        print("  python run_openevolve.py <tool_directory>")
        print("\nExamples:")
        print("  python run_openevolve.py evolution/tools/reflect_on_draft")
        print("  python run_openevolve.py evolution/tools/generate_brand_guidelines")
        
        # List available tools
        available_tools = list_available_tools()
        
        if available_tools:
            print(f"\nReady tools (✅) can be run immediately:")
            for tool in available_tools:
                print(f"  python run_openevolve.py {tool}")
        
        print(f"\nTo prepare tools missing requirements (❌):")
        print(f"  export OPENAI_API_KEY=your_key_here")
        print(f"  python evolution/generate_evaluators.py evolution/tools")
        print(f"  python evolution/generate_openevolve_configs.py evolution/tools")
        
        return
    
    if len(sys.argv) != 2:
        print("Error: Please provide exactly one tool directory")
        print("Usage: python run_openevolve.py <tool_directory>")
        sys.exit(1)
    
    tool_directory = sys.argv[1]
    
    # Run OpenEvolve for the specified tool
    success = await run_openevolve_for_tool(tool_directory)
    
    if not success:
        sys.exit(1)
    
    print(f"\n🎉 OpenEvolve optimization completed!")


if __name__ == "__main__":
    asyncio.run(main())