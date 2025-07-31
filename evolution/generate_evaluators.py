#!/usr/bin/env python3
"""
Evaluator Generation Script for Agent Evolution Framework

This script uses an LLM to generate OpenEvolve-compatible evaluators
for each extracted tool. The evaluators assess tool performance across
multiple dimensions relevant to agent capabilities.

Usage:
    python generate_evaluators.py [tools_directory]
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage


class EvaluatorGenerator:
    """Generates OpenEvolve evaluators for agent tools using LLM"""
    
    def __init__(self, model_name: str = "gpt-4o"):
        self.model = ChatOpenAI(model=model_name, temperature=0.2)
        self.tools_dir = Path("evolution/tools")
    
    def generate_evaluators(self, tools_directory: str = None):
        """Generate evaluators for all tools in the directory"""
        if tools_directory:
            self.tools_dir = Path(tools_directory)
        
        if not self.tools_dir.exists():
            print(f"Error: Tools directory '{self.tools_dir}' does not exist")
            return
        
        print(f"Generating evaluators for tools in: {self.tools_dir}")
        
        # Find all tool directories
        tool_dirs = [d for d in self.tools_dir.iterdir() if d.is_dir() and (d / "tool.py").exists()]
        
        if not tool_dirs:
            print("No tool directories found")
            return
        
        print(f"Found {len(tool_dirs)} tools to generate evaluators for")
        
        for tool_dir in tool_dirs:
            print(f"\nGenerating evaluator for: {tool_dir.name}")
            self._generate_training_data(tool_dir)
        
        print("\nEvaluator generation completed!")

    def _get_source_code(self, file_path: Path):
        """Get the source code for a single tool"""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e: 
            print(f"Error reading tool file: {e}")
            return


    def _generate_training_data(self, tool_dir: Path, number_of_examples: int = 10):
        """Generate training data for a single tool"""
        tool_name = tool_dir.name
        tool_file = tool_dir / "tool.py"
        training_data_file = tool_dir / "training_data.json"
        
        # Read tool source code
        source_code = self._get_source_code(tool_file)

        prompt = {
            "role": "You are an expert in data analysis and generation.",
            "task": "Given a function's source code, generate a training dataset that will be used in a function that evaluates the tool's output quality.",
            "function_name": tool_name,
            "function_code": source_code,
            "instructions": ("Generate a training dataset that will be used in a function that evaluates the tool's output quality." 
                             "The training dataset should be a list of dictionaries, where each dictionary contains the input and output of the function.",
                             "Each training example should contain the input and output of the function.",
                             "If the function is a classification function, do NOT make up fresh classification labels. Use the existing labels in the function.",
                             "If the function generates content like text or code, returning non deterministic LLM outputs, don't generate expected output. Generate only a wide variety of inputs. Don't return an output field.",
                             "The inputs should exactly match the args of the function. Don't add any extra fields. The outputs should exactly match the return type of the function.",
                             "If the function is a quantitative function, generate inputs and outputs that are quantitative. They have to be accurate.",
                             f"Generate {number_of_examples} training data rows."
            ),
            "output_format": "json",
            "output_instructions": "Return ONLY a valid array of JSON object. Don't include any other text, comments backticks, the word 'json' or markdown.",

        }

        response = self.model.invoke([HumanMessage(content=json.dumps(prompt))])
        print(response.content)

        try:
            training_data = json.loads(response.content)
            with open(training_data_file, 'w', encoding='utf-8') as f:
                json.dump(training_data, f, indent=4)
            print(f"Training data saved to {training_data_file}")
        except Exception as e:
            print(f"Error saving training data: {e}")

        return training_data


    def _generate_evaluator_file(self, tool_dir: Path, number_of_examples: int = 10):
        """Generate training data for a single tool"""
        tool_name = tool_dir.name
        tool_file = tool_dir / "tool.py"
        training_data_file = tool_dir / "training_data.json"
        evaluator_file = tool_dir / "evaluator.py"
        
        # Read tool source code
        source_code = self._get_source_code(tool_file)
        training_data = json.load(open(training_data_file, 'r', encoding='utf-8'))


        prompt = {
            "role": "You are an expert in software development and testing.",
            "task": "Given a function's source code, an example training data generate an evaluator that will iterate through a list of training rows and return evaluation metrics for the function.",
            "function_name": tool_name,
            "function_code": source_code,
            "training_data_examples": training_data[:2],
            "instructions": ("Generate an evaluator file that evaluates the tool's output quality." 
                             "It should return a dictionary with the evaluation metrics.",
                             "Choose the metrics contextually relevant to the function.",
                             "If the function is a quantitative function, the evaluator should quantify the accuracy of the function's return value.",
                             f"Generate {number_of_examples} training data rows."
            ),
            "critical_instructions": ("Return a complete python file, complete with all the necessary imports and dependencies.",                        
                                      "It should ALWAYS have an evaluate function.",
                                      "The evaluate function should be able to run on a single machine. It should not require any external dependencies.",
                                      "The evaluate function should accept a single argument, called program, which is the path to the tool's source code.",
            ),
            "output_format": "python",
            "output_instructions": "Return ONLY a valid array of JSON object. Don't include any other text, comments backticks, the word 'json' or markdown.",

        }

        response = self.model.invoke([HumanMessage(content=json.dumps(prompt))])
        print(response.content)

        try:
            training_data = json.loads(response.content)
            with open(training_data_file, 'w', encoding='utf-8') as f:
                json.dump(training_data, f, indent=4)
            print(f"Training data saved to {training_data_file}")
        except Exception as e:
            print(f"Error saving training data: {e}")

        return training_data


        
        


    
    def _generate_single_evaluator(self, tool_dir: Path):
        """Generate an evaluator for a single tool"""
        tool_name = tool_dir.name
        tool_file = tool_dir / "tool.py"
        metadata_file = tool_dir / "metadata.json"
        evaluator_file = tool_dir / "evaluator.py"
        
        # Read tool source code
        try:
            with open(tool_file, 'r', encoding='utf-8') as f:
                tool_source = f.read()
        except Exception as e:
            print(f"Error reading tool file: {e}")
            return
        
        # Read metadata if available
        metadata = {}
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            except Exception as e:
                print(f"Warning: Could not read metadata: {e}")
        
        # Generate training data and evaluator using LLM
        self._generate_training_data(tool_dir)

        
            
        
    


def main():
    """Main entry point"""
    if len(sys.argv) > 2:
        print("Usage: python generate_evaluators.py [tools_directory]")
        print("Example: python generate_evaluators.py evolution/tools")
        sys.exit(1)
    
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY environment variable is required")
        print("Please set your OpenAI API key: export OPENAI_API_KEY=your_key_here")
        sys.exit(1)
    
    tools_directory = sys.argv[1] if len(sys.argv) == 2 else None
    
    generator = EvaluatorGenerator()
    generator.generate_evaluators(tools_directory)


if __name__ == "__main__":
    main()