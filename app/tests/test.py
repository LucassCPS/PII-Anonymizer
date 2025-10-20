from pathlib import Path
import pandas as pd
import json

import os
from openai import OpenAI
from core import config

# The response set is a list containing either the value or None
# https://huggingface.co/datasets/cicero-im/piiptbrchatml
DATASET_FILE_01 = "pii_ptbrchatml.parquet"

# The response set shows issues; for example, '$' is considered sensitive and classified as a category.
# https://huggingface.co/datasets/ai4privacy/pii-masking-200k
DATASET_FILE_02 = "pii_masking.parquet"

# Using the test dataset.
# https://huggingface.co/datasets/gretelai/gretel-pii-masking-en-v1
# https://huggingface.co/datasets/gretelai/gretel-pii-masking-en-v1/tree/main/data
DATASET_FILE_03 = "gretelaigretel_pii_masking_en_v1.parquet"

def test_case_01():
    dataset_path = Path(__file__).parent / "dataset" / DATASET_FILE_01
    assert dataset_path.exists(), f"Dataset not found at {dataset_path}"

    df = pd.read_parquet(dataset_path)

    print(df.columns)

def test_case_02():
    dataset_path = Path(__file__).parent / "dataset" / DATASET_FILE_02
    assert dataset_path.exists(), f"Dataset not found at {dataset_path}"

    df = pd.read_parquet(dataset_path)
    print(df.columns)


####
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
        return response.choices[0].message.content
    except Exception as e:
        return ""

def string_list_to_json(string_list):
    aux_string_list = string_list.replace("'", '"')
    try:
        final_json = json.loads(aux_string_list)
        return final_json
    except json.JSONDecodeError as e:
        raise ValueError(f"Error while converting string to json: {e}\nContent: {string_list}")


def reorganize_dataset_results(dataset_entities):
    valid_json = string_list_to_json(dataset_entities)

    entities = []
    for item in valid_json:
        entity = item.get("entity")
        types = item.get("types", [])
        for tipo in types:
            entities.append({"label": tipo, "text": entity})

    return {"entities": entities}

def compare_structures(e1, e2):
    set1 = {(item["label"], item["text"]) for item in e1["entities"]}
    set2 = {(item["label"], item["text"]) for item in e2["entities"]}

    only_in_1 = set1 - set2
    only_in_2 = set2 - set1
    intersection = set1 & set2

    map1 = {item["text"]: item["label"] for item in e1["entities"]}
    map2 = {item["text"]: item["label"] for item in e2["entities"]}

    different_labels = []
    for text in set(map1.keys()) & set(map2.keys()):
        if map1[text] != map2[text]:
            different_labels.append({
                "text": text,
                "label_structure1": map1[text],
                "label_structure2": map2[text]
            })

    result = {
        "equal": list(intersection),
        "only_in_structure1": list(only_in_1),
        "only_in_structure2": list(only_in_2),
        "different_labels": different_labels
    }

    print("Matching entities:", len(intersection))
    print("Entities only in structure 1:", len(only_in_1))
    print("Entities only in structure 2:", len(only_in_2))
    print("Texts with different labels:", len(different_labels))

    return result

def test_case_03():
    dataset_path = Path(__file__).parent / "dataset" / DATASET_FILE_03
    assert dataset_path.exists(), f"Dataset not found at {dataset_path}"

    df = pd.read_parquet(dataset_path)

    SYSTEM_PROMPT_FILE = "system_prompt_default.txt"
    DEFAULT_SYSTEM_PROMPT = ""
    try:
        if os.path.exists(SYSTEM_PROMPT_FILE):
            with open(SYSTEM_PROMPT_FILE, "r", encoding="utf-8") as f:
                DEFAULT_SYSTEM_PROMPT = f.read().strip()
        else:
            print("Prompt file not found.")
    except Exception as e:
        print("Error while loading model instructions.")

    base_url, api_key, models = config.load_env_and_models()

    NUM_ROWS = 1
    for idx, row in df.iterrows():
        if idx == NUM_ROWS:
            break
        
        entities = row["entities"]
        input = row["text"]

        print(f"input: {input}")

        dataset_json_data = reorganize_dataset_results(entities)
        print(f"expected: {json.dumps(dataset_json_data, indent=4, ensure_ascii=False)}")

        llm_response = call_llm(input, DEFAULT_SYSTEM_PROMPT, base_url, api_key, models["MODEL_QWEN3_8B"])
        llm_json_data = string_list_to_json(llm_response)
        print(f"llm response: {json.dumps(llm_json_data, indent=4, ensure_ascii=False)}")      

        compare_structures(dataset_json_data, llm_json_data)