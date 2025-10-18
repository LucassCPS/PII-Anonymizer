import os

def load_env_and_models():
    base_url = ""
    api_key = ""
    models = {}

    base_url = os.getenv("BASE_URL")
    api_key = os.getenv("API_KEY")
    for k, v in os.environ.items():
        if k.startswith("MODEL_") and v:
            models[k] = v

    return base_url, api_key, models