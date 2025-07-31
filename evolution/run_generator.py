#!/usr/bin/env python3
import subprocess
import sys
import os

# Change to the correct directory
os.chdir('/Users/praveenkoka/koka/tril/agent_rl/evolution')

# Run the config generator
try:
    # Try running with different Python interpreters
    result = subprocess.run(['/usr/bin/python3', 'generate_openevolve_configs.py', 'tools'], 
                          capture_output=True, text=True, timeout=60)
    
    print("STDOUT:")
    print(result.stdout)
    
    if result.stderr:
        print("\nSTDERR:")
        print(result.stderr)
    
    print(f"\nReturn code: {result.returncode}")
    
except Exception as e:
    print(f"Error: {e}")