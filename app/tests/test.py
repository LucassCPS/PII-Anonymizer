import pandas as pd
from utils import data_conversion_handler

def call_llm(client, model, system_prompt, input, temp):
    messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": input}]

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temp
        )
        output = response.choices[0].message.content.strip()
        return output if output else '{ "entities": [] }'
    except Exception:
        return '{ "entities": [] }'

def compare_results(dataset_set, llm_set_response):
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

def full_test(client, dataset_path, num_rows_dataset, temp, system_prompt, model):
    df = pd.read_parquet(dataset_path)

    for idx, row in df.iterrows():
        if idx == num_rows_dataset:
            break

        entities = row["entities"]
        input = row["text"]

        # getting dataset solution to a given dataset input
        dataset_json_data = data_conversion_handler.string_list_to_json(entities)
        dataset_set_data = data_conversion_handler.dataset_json_to_set(dataset_json_data)

        # getting llm response to the same dataset input
        llm_response = call_llm(client, model, system_prompt, input, temp)
        llm_json_data = data_conversion_handler.string_list_to_json(llm_response)
        llm_set_data = data_conversion_handler.llm_json_to_set(llm_json_data)

        # comparing llm response to the expected result in the dataset
        result = compare_results(dataset_set_data, llm_set_data)
        print_comparison(result)
