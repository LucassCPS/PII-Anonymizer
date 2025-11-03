import os
from dotenv import dotenv_values, load_dotenv

def load_env_and_models(env_path: str):
    env_vars = {}

    if os.path.exists(env_path):
        env_vars = dotenv_values(env_path)

    base_url = env_vars.get("BASE_URL")
    api_key = env_vars.get("API_KEY") or os.getenv("API_KEY")
    models = {k: v for k, v in env_vars.items() if k.startswith("MODEL_")} if env_vars else {}

    if not models or not api_key or not base_url:
        target_env = None
        if os.path.exists(env_path):
            target_env = env_path
        elif os.path.exists(".env"):
            target_env = ".env"
        
        if target_env:
            load_dotenv(dotenv_path=target_env, override=False)
            
        base_url = base_url or os.getenv("BASE_URL")
        api_key = api_key or os.getenv("API_KEY")

        for k, v in os.environ.items():
            if k.startswith("MODEL_") and v:
                models[k] = v

    return base_url, api_key, models, env_vars

def load_models():
    models = {}    
    for k, v in os.environ.items():
        if k.startswith("MODEL_") and v:
            models[k] = v
    return models
