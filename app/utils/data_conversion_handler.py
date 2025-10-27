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
    
    entities = {item["entity"] for item in data if isinstance(item, dict) and "entity" in item}
    return entities

# converts the llm response json to a set data structure
def llm_json_to_set(data):
    if not isinstance(data, dict) or "entities" not in data:
        return set()

    texts = set()
    for item in data.get("entities", []):
        if isinstance(item, dict) and "text" in item:
            text_value = item["text"]
            if isinstance(text_value, (str, int, float, tuple)):
                texts.add(text_value)
            elif isinstance(text_value, list):
                texts.add(" ".join(map(str, text_value)))
            else:
                continue
    return texts