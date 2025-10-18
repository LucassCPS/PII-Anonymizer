from openai import OpenAI
from core import config
import os
import time

user_prompt = "Olá, meu nome é Lucas e tenho 23 anos"

SYSTEM_PROMPT_FILE = "system_prompt_default.txt"
DEFAULT_SYSTEM_PROMPT = ""

try:
    if os.path.exists(SYSTEM_PROMPT_FILE):
        with open(SYSTEM_PROMPT_FILE, "r", encoding="utf-8") as f:
            DEFAULT_SYSTEM_PROMPT = f.read().strip()
    else:
        print("Arquivo com instruções não encontrado.")
except Exception as e:
    print("Erro ao carregar as instruções para o modelo.")

base_url, api_key, models = config.load_env_and_models()

client = OpenAI(base_url=base_url, api_key=api_key)

messages = [
    {"role": "system", "content": DEFAULT_SYSTEM_PROMPT},
    {"role": "user", "content": user_prompt},
]

try:
    start_time = time.time()
    response = client.chat.completions.create(
        model=models["MODEL_QWEN3_8B"],
        messages=messages,
        temperature=0.3
    )
    end_time = time.time()

    print(f"LLM Full Response:\n {response}")
    print(f"\n\nResponse:\n {response.choices[0].message.content}")
    print(f"\nReasoning Content:\n {response.choices[0].message.reasoning_content}")

    generation_time_ms = response.timings['predicted_ms']
    print(f"\n\nTempo de Geração da Resposta (API): {generation_time_ms:.2f} ms ({generation_time_ms / 1000:.2f} s)")

    total_time = end_time - start_time
    print(f"Tempo Total de Requisição (End-to-End): {total_time:.2f} s")
except Exception as e:
    print(f"An error occurred: {e}")