import json

# converts a string list to a json format data
def string_list_to_json(string_list):
    if not isinstance(string_list, str):
        return []

    string_list = string_list.replace("'", '"')
    try:
        json_data = json.loads(string_list)
    except json.JSONDecodeError:
        json_data = []
    
    return json_data

# converts the dataset json to a set data structure
def dataset_json_to_set(data):
    if not isinstance(data, list):
        raise ValueError("Input must be a list of dictionaries.")
    
    entities = {item["entity"] for item in data if "entity" in item}
    return entities

# converts the llm response json to a set data structure
def llm_json_to_set(data):
    if not isinstance(data, dict) or "entities" not in data:
        return set()

    texts = {item["text"] for item in data.get("entities", []) if "text" in item}
    return texts