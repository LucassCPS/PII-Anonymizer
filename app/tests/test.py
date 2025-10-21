from pathlib import Path
import pandas as pd
import json

from openai import OpenAI
from core import config
from utils import prompts

# Using the test dataset.
# https://huggingface.co/datasets/gretelai/gretel-pii-masking-en-v1
DATASET_FILE = "gretelaigretel_pii_masking_en_v1.parquet"
MODEL = "ai/qwen3:0.6B-Q4_K_M"
#MODEL = "ai/qwen3:8B-Q4_K_M"
NUM_ROWS = 1000

def call_llm(input, model_instructions, base_url, api_key, model):
    client = OpenAI(base_url=base_url, api_key=api_key)

    messages = [{"role": "system", "content": model_instructions},
                {"role": "user", "content": input}]

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.3
        )
        output = response.choices[0].message.content.strip()
        return output if output else '{ "entities": [] }'
    except Exception:
        return '{ "entities": [] }'

def string_list_to_json(string_list):
    if not isinstance(string_list, str):
        return []

    aux_string_list = string_list.replace("'", '"')
    try:
        final_json = json.loads(aux_string_list)
    except json.JSONDecodeError:
        final_json = []
    
    return final_json

def llm_json_to_set(data):
    if not isinstance(data, dict) or "entities" not in data:
        return set()

    texts = {item["text"] for item in data.get("entities", []) if "text" in item}
    return texts

def dataset_json_to_set(data):
    if not isinstance(data, list):
        raise ValueError("Input must be a list of dictionaries.")
    
    entities = {item["entity"] for item in data if "entity" in item}
    return entities

def compare_sets(dataset_set, llm_set_response):
    return {
        "only_in_dataset": dataset_set - llm_set_response,
        "only_in_llm_response": llm_set_response - dataset_set,
        "in_both": dataset_set & llm_set_response
    }

def print_comparison(result):
    print("Only in dataset:")
    for item in sorted(result["only_in_dataset"]):
        print(f"  - {item}")

    print("\nOnly in LLM response:")
    for item in sorted(result["only_in_llm_response"]):
        print(f"  - {item}")

    print("\nIn both:")
    for item in sorted(result["in_both"]):
        print(f"  - {item}")


def test_case():
    dataset_path = Path(__file__).parent / "dataset" / DATASET_FILE
    assert dataset_path.exists(), f"Dataset not found at {dataset_path}"

    df = pd.read_parquet(dataset_path)

    base_url, api_key, _ = config.load_env_and_models()

    for idx, row in df.iterrows():
        if idx == NUM_ROWS:
            break
        
        entities = row["entities"]
        input = row["text"]

        #print(f"input: {input}")

        dataset_json_data = string_list_to_json(entities)
        dataset_set_data = dataset_json_to_set(dataset_json_data)
        #print("DATASET: ", dataset_set_data)

        llm_response = call_llm(input, prompts.get_few_shot_prompt(), base_url, api_key, MODEL)
        llm_json_data = string_list_to_json(llm_response)
        llm_set_data = llm_json_to_set(llm_json_data)
        #print("LLM: ", llm_set_data)
        print(f"\n[{idx+1}] ======================")
        print_comparison(compare_sets(dataset_set=dataset_set_data, llm_set_response=llm_set_data))