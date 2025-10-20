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

def load_system_prompt_from_file(system_prompt_file):
    system_prompt = ""
    try:
        if os.path.exists(system_prompt_file):
            with open(system_prompt_file, "r", encoding="utf-8") as f:
                system_prompt = f.read().strip()
            return system_prompt
        else:
            print("Prompt file not found.")
    except Exception as e:
        print("Error while loading model instructions.")