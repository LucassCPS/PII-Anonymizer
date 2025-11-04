import re

def clean_json_output(text: str) -> str:
    cleaned_text = re.sub(r'^\s*```(?:json)?\s*', '', text, flags=re.MULTILINE | re.IGNORECASE)
    cleaned_text = re.sub(r'\s*```\s*$', '', cleaned_text, flags=re.MULTILINE)
    cleaned_text = re.sub(r'^\s*(?:Aqui está o JSON:\s*|Resposta:\s*|JSON\s*:\s*)', '', cleaned_text, flags=re.IGNORECASE)
    return cleaned_text.strip()
