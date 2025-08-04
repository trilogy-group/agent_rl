#!/usr/bin/env python3
import sys
from pathlib import Path
import subprocess

# Run the config generator
try:
    result = subprocess.run([
        sys.executable, 
        "generate_openevolve_configs.py", 
        "tools"
    ], 
    cwd="/Users/praveenkoka/koka/tril/agent_rl/evolution",
    capture_output=True, 
    text=True, 
    timeout=30
    )
    
    print("STDOUT:")
    print(result.stdout)
    
    if result.stderr:
        print("\nSTDERR:")
        print(result.stderr)
    
    print(f"\nReturn code: {result.returncode}")
    
except subprocess.TimeoutExpired:
    print("Command timed out")
except Exception as e:
    print(f"Error running command: {e}")