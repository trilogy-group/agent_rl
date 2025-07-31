#!/usr/bin/env python3
"""
OpenEvolve Evaluator for research_for_brand
Generated automatically by LLM-based evaluator generator
"""

import json
import os
import importlib.util

def evaluate(program) -> dict:
    try:
        # Load the training data
        with open('training_data.json', 'r') as f:
            training_data = json.load(f)
        
        # Dynamically import the tool
        spec = importlib.util.spec_from_file_location("tools", program)
        tools = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tools)
        
        # Initialize metrics
        information_accuracy = 0.0
        source_credibility = 0.0
        completeness = 0.0
        relevance = 0.0
        timeliness = 0.0
        num_samples = len(training_data)
        
        # Evaluate each sample
        for sample in training_data:
            input_data = sample['input']
            expected_output = sample['expected_output']
            actual_output = tools.research_for_brand(input_data['brand_info'], input_data.get('existing_content', []))
            
            # Calculate metrics
            if actual_output == expected_output:
                information_accuracy += 1.0
                source_credibility += 1.0
                completeness += 1.0
                relevance += 1.0
                timeliness += 1.0
        
        # Average the metrics
        if num_samples > 0:
            information_accuracy /= num_samples
            source_credibility /= num_samples
            completeness /= num_samples
            relevance /= num_samples
            timeliness /= num_samples
        
        return {
            "information_accuracy": information_accuracy,
            "source_credibility": source_credibility,
            "completeness": completeness,
            "relevance": relevance,
            "timeliness": timeliness
        }
    
    except Exception as e:
        # Handle exceptions and return all metrics as 0.0 on failure
        return {
            "information_accuracy": 0.0,
            "source_credibility": 0.0,
            "completeness": 0.0,
            "relevance": 0.0,
            "timeliness": 0.0
        }