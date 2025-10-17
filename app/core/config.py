
import os
from dotenv import dotenv_values, load_dotenv
from typing import Dict, List, Tuple, Any

def parse_models_manual(path: str) -> Dict[str, str]:
    models = {}
    if not os.path.exists(path):
        return models
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k.startswith("MODEL_") and v:
                    models[k] = v
    return models

def load_env_and_models(env_path: str) -> Tuple[str | None, str | None, Dict[str, str], str, Dict[str, Any]]:
    source: List[str] = []
    env_vars: Dict[str, Any] = {}

    if os.path.exists(env_path):
        env_vars = dotenv_values(env_path)
        source.append(f"dotenv_values({env_path})")

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
            source.append(f"load_dotenv({target_env})")
            
        base_url = base_url or os.getenv("BASE_URL")
        api_key = api_key or os.getenv("API_KEY")

        for k, v in os.environ.items():
            if k.startswith("MODEL_") and v:
                models[k] = v

    if not models and os.path.exists(env_path):
        manual = parse_models_manual(env_path)
        if manual:
            models = manual
            source.append(f"parse_models_manual({env_path})")

    if not models and os.path.exists(".env") and env_path != ".env":
        manual = parse_models_manual(".env")
        if manual:
            models = manual
            source.append("parse_models_manual(.env)")

    if not api_key:
        lit = env_vars.get("API_KEY") if env_vars else None
        if lit and lit.startswith("$(") and ":-" in lit and lit.endswith(")"):
            padrao = lit.split(":-", 1)[1][:-1]
            api_key = padrao

    return base_url, api_key, models, " -> ".join(source) or "(nenhuma fonte)", env_vars