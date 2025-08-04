import yaml
from pathlib import Path

# Read the current config
config_file = Path("tools/generate_essay/openevolve_config.yaml")
with open(config_file, 'r') as f:
    config = yaml.safe_load(f)

# Update the feature_dimensions to match the actual evaluator metrics
config['database']['feature_dimensions'] = ['quality', 'relevance', 'engagement', 'authenticity']

# Update the system message to reflect these metrics
config['prompt']['system_message'] = config['prompt']['system_message'].replace(
    'Quality\n- Relevance\n- Usefulness\n- Clarity',
    'Quality\n- Relevance\n- Engagement\n- Authenticity'
)

# Save the updated config
with open(config_file, 'w') as f:
    yaml.dump(config, f, default_flow_style=False, indent=2, sort_keys=False)

print("Updated generate_essay config with correct metrics: ['quality', 'relevance', 'engagement', 'authenticity']")

# Also fix generate_brand_guidelines config
config_file2 = Path("tools/generate_brand_guidelines/openevolve_config.yaml")
with open(config_file2, 'r') as f:
    config2 = yaml.safe_load(f)

config2['database']['feature_dimensions'] = ['completeness', 'actionability', 'brand_alignment', 'clarity']

# Save the updated config
with open(config_file2, 'w') as f:
    yaml.dump(config2, f, default_flow_style=False, indent=2, sort_keys=False)

print("Updated generate_brand_guidelines config with correct metrics: ['completeness', 'actionability', 'brand_alignment', 'clarity']")