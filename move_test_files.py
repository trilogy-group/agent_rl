#!/usr/bin/env python3
import os
import shutil

# Files to move to tests directory
test_files = [
    'test_training_data.py',
    'test_blind_evaluation.py', 
    'test_llm_metric_selection.py',
    'test_decorator.py',
    'test_import.py',
    'simple_test.py',
    'test_fixed_extractor.py',
    'test_debug_extractor.py',
    'test_fixed_evaluator_generator.py',
    'test_final_fix.py',
    'test_metrics_extraction.py',
    'test_function_analysis.py',
    'test_metrics_extraction_debug.py',
    'test_fixed_extraction.py',
    'simple_regex_test.py',
    'manual_test_extraction.py',
    'test_extraction.py',
    'test_dependency_extraction.py',
    'test_evaluator_generator.py',
    'test_validation_logic.py',
    'test_validation_only.py',
    'test_import_extraction.py',
    'test_quantitative_evaluator.py',
    'test_algorithmic_prompt.py',
    'test_json_parser_fix.py',
    'test_evaluator_fix.py',
    'test_prompt_evaluator.py',
    'test_all_evaluator_types.py',
    'test_prompt_evaluation_approach.py',
    'test_intent_classification_evaluation.py',
    'demo_quantitative_classification.py',
    'demo_algorithmic_evaluation.py',
    'create_custom_evaluator.py',
    'debug_error_handling.py',
    'efficient_evaluator_example.py',
    'evolve_decorator.py',
    'example_decorated_tools.py',
    'extract_commented_evolve.py',
    'extract_decorated_tools.py',
    'extract_tools.py',
    'fix_config.py',
    'fix_evaluator_json_parsing.py',
    'fix_extraction.py',
    'generate_evaluators.py',
    'generate_evaluators_broken.py',
    'generate_evaluators_old.py',
    'generate_evaluators_old_1.py',
    'generate_evaluators_simple.py',
    'generate_openevolve_configs.py',
    'generate_training_data.py',
    'json_evaluator_example.py',
    'realistic_linkedin_examples.py',
    'regenerate_configs_now.py',
    'rerun_extractor.py',
    'run_config_generator.py',
    'run_extraction.py',
    'run_extractor.py',
    'run_generator.py',
    'run_openevolve.py',
    'setup.py',
    'update_configs_with_correct_metrics.py',
    'verify_extraction.py'
]

base_dir = 'agent_evolve'
tests_dir = os.path.join(base_dir, 'tests')

for filename in test_files:
    src = os.path.join(base_dir, filename)
    dst = os.path.join(tests_dir, filename)
    
    if os.path.exists(src):
        print(f'Moving {src} -> {dst}')
        shutil.move(src, dst)
    else:
        print(f'File not found: {src}')

print('Done moving test files!')