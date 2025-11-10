import os
from enum import Enum

class ModelEnum(Enum):
    GEMMA3_QAT_270M = "MODEL_GEMMA3_QAT_270M"
    GEMMA3_QAT_4B = "MODEL_GEMMA3_QAT_4B"
    SMOLL3_Q4 = "MODEL_SMOLL3_Q4"
    SMOLL3_Q8 = "MODEL_SMOLL3_Q8"
    QWEN3_06B = "MODEL_QWEN3_06B"
    QWEN3_8B = "MODEL_QWEN3_8B"
    GRANITE4_TINY = "MODEL_GRANITE4_TINY"
    MISTRAL_NEMO = "MODEL_MISTRAL_NEMO"
    DEEPSEEK = "MODEL_DEEPSEEK"
    LLAMA32_3B= "MODEL_LLAMA32_3B_Q4"
    LLAMA32_1B= "MODEL_LLAMA32_1B_Q8"

def load_model(model_enum: ModelEnum):
    model_key = model_enum.value
    model_value = os.getenv(model_key)

    if not model_value:
        raise KeyError(f"Model '{model_key}' not found in environment variables.")

    return model_value

def load_api_key():
    return os.getenv("API_KEY")

def load_base_url():
    return os.getenv("BASE_URL")
