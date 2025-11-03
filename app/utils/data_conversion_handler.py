import json
import re

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
    
def clean_llm_response(response):
    cleaned_str = response.strip()

    match = re.search(r'\{.*\}', cleaned_str, re.DOTALL)
    if match:
        json_candidate = match.group(0).strip()
        json_candidate = re.sub(r'^\s*```(?:json|python|text)?\s*', '', json_candidate, flags=re.IGNORECASE)
        json_candidate = re.sub(r'```\s*$', '', json_candidate)
        try:
            data = json.loads(json_candidate)
            
            if 'entities' not in data or not isinstance(data['entities'], list):
                 if isinstance(data, list):
                     return json.dumps({"entities": data})
                 return '{ "entities": [] }'
            return json.dumps(data, separators=(',', ':'))       
        except json.JSONDecodeError:
            return '{ "entities": [] }'
    return '{ "entities": [] }'