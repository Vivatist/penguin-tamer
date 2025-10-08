from pathlib import Path
from platformdirs import user_config_dir
import yaml

path = Path(user_config_dir('penguin-tamer')) / 'config.yaml'
print(f'Config path: {path}')
print(f'File exists: {path.exists()}')

with open(path, 'r', encoding='utf-8') as f:
    cfg = yaml.safe_load(f)
    print(f"current_LLM from file: {cfg['global']['current_LLM']}")
